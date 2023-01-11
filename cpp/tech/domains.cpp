#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <arrayobject.h>
#include <iostream>
#include <string>
#include <queue>
#include <thread>
#include <stdexcept>
#include <sys/mman.h>
#include "tech.h"

using namespace std;

static PyObject *day_streak(PyObject *self, PyObject *args)
{
    /**
     * @brief calculates and returns the set of stock code and date key pair of stocks at which streaks end
     * @param _hist 2D list, with [stock code, trading date, price] as the columns
     * @param streak_len the length of required streak
     * @param is_up bool, which signifies losing or gaining streak
     */

    // Parse numpy arrays into pyobjects
    PyArrayObject *_hist;
    int streak_len, is_up;
    auto sample_less = [](Sample &l, Sample &r)
    {
        return l > r;
    };

    priority_queue<Sample, std::vector<Sample>, decltype(sample_less)> pq(sample_less), res_pq(sample_less);

    if (!PyArg_ParseTuple(args, "Oii", &_hist, &streak_len, &is_up))
    {
        throw std::invalid_argument("parse tuple failed");
        return NULL;
    }

    // insert all dataframe samples into priority queue
    for (int i = 0; i < PyList_Size((PyObject *)_hist); i++)
    {
        PyObject *tmp_obj = PyList_GetItem((PyObject *)_hist, i);
        Sample s(tmp_obj);
        pq.push(s);
        // _Py_DECREF(tmp_obj); // will trigger segfault?
    }
    _Py_DECREF((PyObject *)_hist);

    // calculate the streaks using boost shared memory containers
    cout << "num of concurrent threads: " << thread::hardware_concurrency() << endl;
    cout << "total samples: " << pq.size() << endl;
    int num_procs = thread::hardware_concurrency();
    int shm_size = pq.size() * 5 * streak_len * sizeof(string("000001.SZ")) * 0.2;
    cout << "shared memory size: " << shm_size << " bytes" << endl;

    // build interprocess containers
    bip::shared_memory_object::remove("shmem_streak");
    bip::managed_shared_memory shm(bip::open_or_create, "shmem_streak", shm_size);
    bip::allocator<char, msm::segment_manager> chr_altr(shm.get_segment_manager());
    typedef bip::basic_string<char, char_traits<char>, decltype(chr_altr)> str;
    bip::allocator<str, msm::segment_manager> str_altr(shm.get_segment_manager());
    typedef vector<str, decltype(str_altr)> vec;

    // create interprocess specs
    int child_range = pq.size() / num_procs;

    for (int i = 0, pid; i < num_procs; i++)
    {
        /* parent assigns samples to a child proportionately for calculation */
        if (pq.empty())
            break;
        int cnt = 0;
        string curr_code = pq.top().code;
        vector<Sample> child_data_vec;
        // collect enough portion for child but cut off at the end of code section
        while (!pq.empty() && (cnt < child_range || curr_code == pq.top().code))
        {
            // append a sample for the child
            Sample sample = pq.top();
            pq.pop();
            child_data_vec.push_back(sample);
            // update state
            curr_code = sample.code;
            cnt++;
        }

        /* initiate child processes */
        if ((pid = fork()) == 0)
        {
            // calculate the streaks
            vector<string> tmp_res_vec;
            get_streaks(child_data_vec, streak_len, is_up == 1, tmp_res_vec);

            // put the results in shared vector
            auto child_res_vec = shm.find_or_construct<vec>("res_vec")(str_altr);
            auto mtx = shm.find_or_construct<bip::interprocess_mutex>("mtx")();
            mtx->lock();
            for (string &elem : tmp_res_vec)
            {
                str tmp_str(chr_altr);
                tmp_str = elem.c_str();
                child_res_vec->push_back(tmp_str);
            }
            mtx->unlock();
            exit(0);
        }
        else
            cout << "[parent] pid: " << pid << " created" << endl;
    }

    while (wait(NULL) > 0)
        ;
    auto *parent_res_vec = shm.find<vec>("res_vec").first;
    cout << "test res pq: " << parent_res_vec->size() << endl;
    PyObject *res = PyList_New(parent_res_vec->size());
    for (unsigned int i = 0; i < parent_res_vec->size(); i++)
    {
        auto &elem = parent_res_vec->at(i);
        PyObject *key = PyUnicode_DecodeUTF8(elem.c_str(), elem.size(), "utf-8 error");
        PyList_SetItem(res, i, key);
    }

    return res;
}
/**
 * @brief get the moving average of close prices of the stocks
 *
 * @param self
 * @param args contains a 2D list of historical data, assumed sorted by (code, date) compound key
 * @return PyObject*
 */
static PyObject *ma(PyObject *self, PyObject *args)
{
    PyArrayObject *_hist;

    if (!PyArg_ParseTuple(args, "O", &_hist))
    {
        throw std::invalid_argument("parse tuple failed");
        return NULL;
    }

    string curr_code = "";

    for (int i = 0; i < PyList_Size((PyObject *)_hist); i++)
    {
        PyObject *row = PyList_GetItem((PyObject *)_hist, i);

        Sample s(row);
    }

    // _Py_DECREF((PyObject *)_hist);
    // PyObject *res = PyList_New(2);

    return PyList_New(2);
}

static PyMethodDef tech_methods[] = {
    {"day_streak", (PyCFunction)day_streak, METH_VARARGS, "calculate the streak signals"},
    {"ma", (PyCFunction)ma, METH_VARARGS, "calculate the streak signals"},
    {NULL, NULL, 0, NULL}};

static PyModuleDef tech_module = {
    PyModuleDef_HEAD_INIT,
    "rumble_cpp",
    "technical analysis signals",
    0,
    tech_methods};

PyMODINIT_FUNC PyInit_rumble_cpp()
{
    return PyModule_Create(&tech_module);
}