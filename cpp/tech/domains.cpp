#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <arrayobject.h>
#include <iostream>
#include <string>
#include <queue>
#include <thread>
#include <stdexcept>
#include <sys/mman.h>
#include <boost/version.hpp>
#include <boost/interprocess/managed_shared_memory.hpp>
#include <boost/interprocess/containers/map.hpp>
#include <boost/interprocess/containers/vector.hpp>
#include <boost/interprocess/allocators/allocator.hpp>
// #include <boost/interprocess/creation_tags.hpp>
#include "tech.h"

using namespace std;
using namespace boost::interprocess;

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
    // for (cout << "sample queue: "; !pq.empty(); pq.pop())
    //     pq.top().print();
    // _Py_DECREF((PyObject *)_hist);
    cout << "num of concurrent threads: " << thread::hardware_concurrency() << endl;
    cout << "streak length: " << streak_len << "  "
         << "is_up streak: " << is_up << endl;
    int num_procs = thread::hardware_concurrency();
    shared_memory_object::remove("shmem_streak");
    managed_shared_memory shm(open_or_create, "shmem_streak", 10000);
    typedef boost::interprocess::allocator<int, managed_shared_memory::segment_manager> shmem_allocator;
    typedef boost::interprocess::vector<int, shmem_allocator> shmem_vector;
    const shmem_allocator vec_alloc(shm.get_segment_manager());
    shmem_vector *res_vec = shm.construct<shmem_vector>("res_vec")(vec_alloc);

    for (int i = 0, pid; i < num_procs; i++)
    {
        if ((pid = fork()) == 0)
        {
            auto test_pq_ptr = shm.find<shmem_vector>("res_vec").first;
            cout << "pushing " << i << endl;
            int *val = shm.construct<int>("Integer" + i)(i);
            test_pq_ptr->push_back(*val);
            exit(0);
        }
        else
            cout << "pid: " << pid << " created" << endl;
    }   
    while(wait(NULL)>0);
    auto p_vec = shm.find<shmem_vector>("res_vec").first;
    for (cout << "test res pq: " << endl; p_vec->size(); p_vec->pop_back())
        cout << p_vec->back() << endl;

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