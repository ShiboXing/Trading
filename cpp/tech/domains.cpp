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

    // Parse numpy arrays into pyobjects
    PyArrayObject *_hist;
    int streak_len, is_up;
    auto sample_less = [](Sample &l, Sample &r)
    {
        return l > r;
    };

    priority_queue<Sample, std::vector<Sample>, decltype(sample_less)> pq(sample_less), res_pq(sample_less);
    // auto bip = boost::interprocess;
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
    cout << "num of concurrent threads: " << thread::hardware_concurrency() << endl;
    cout << "total samples: " << pq.size() << endl;

    int num_procs = thread::hardware_concurrency();
    // calculate the streaks using boost shared memory containers
    if (pq.size() >= 10000000)
        cout << "[warning] memory usage > 100MB" << endl;

    // build interprocess containers
    bip::shared_memory_object::remove("shmem_streak");
    bip::managed_shared_memory shm(bip::open_or_create, "shmem_streak", pq.size() * sizeof(string("000001.SZ")));
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
        string curr_code = pq.top().ts_code;
        vector<Sample> child_data_vec;
        // collect enough portion for child but cut off at the end of code section
        while (!pq.empty() && (cnt < child_range || curr_code == pq.top().ts_code))
        {
            // append a sample for the child
            Sample sample = pq.top();
            pq.pop();
            child_data_vec.push_back(sample);
            // update state
            curr_code = sample.ts_code;
            cnt++;
        }

        /* initiate child processes */
        if ((pid = fork()) == 0)
        {
            // calculate the streaks
            vector<string> tmp_res_vec;
            get_streaks(child_data_vec, i, is_up == 1, tmp_res_vec);

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
    cout << "test res pq: " << endl;
    for (auto &elem : *parent_res_vec)
        cout << elem << endl;

    return MyPyLong_FromInt64(0);
}

static PyMethodDef tech_methods[] = {
    {"day_streak", (PyCFunction)day_streak, METH_VARARGS, "calculate the streak signals"},
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