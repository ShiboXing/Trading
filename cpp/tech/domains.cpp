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
    priority_queue<Sample, vector<Sample>, decltype(sample_less)> pq(sample_less);

    if (!PyArg_ParseTuple(args, "Oii", &_hist, &streak_len, &is_up))
    {
        throw invalid_argument("parse tuple failed");
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
    // for (cout << "sample queue: "; !pq.empty(); pq.pop())
    //     pq.top().print();
    _Py_DECREF((PyObject *)_hist);
    cout << "num of concurrent threads: " << thread::hardware_concurrency() << endl;
    cout << "streak length: " << streak_len << "  "
         << "is_up streak: " << is_up << endl;
    int num_procs = thread::hardware_concurrency();
    // auto res_pq = (priority_queue<Sample, vector<Sample>, decltype(sample_less)> *)mmap(NULL, pq.size() * 0.5 * 8 * 4, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    auto res_pq = (priority_queue<int> *)mmap((void *)new priority_queue<int>(), pq.size() * 0.5 * 8 * 4, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    cout << "pq size: " << pq.size() * 0.5 * 8 * 4 << endl;
    for (int i = 0, pid; i < num_procs - 1; i++)
    {
        if ((pid = fork()) == 0)
        {
            res_pq->push(i);
            exit(0);
        }
        else
            cout << "pid: " << pid << " created" << endl;
    }
    for (cout << "dump res pq: " << endl; res_pq->size(); res_pq->pop())
    {
        cout << res_pq->top() << endl;
    }
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