#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <arrayobject.h>
#include <iostream>
#include <string>
#include <vector>
#include <stdexcept>
#include "sample_point.h"

using namespace std;

static PyObject *day_streak(PyObject *self, PyObject *arr)
{
    // Parse numpy arrays into pyobjects
    PyArrayObject *_hist;
    if (!PyArg_ParseTuple(arr, "O", &_hist))
    {
        throw invalid_argument("parse tuple failed");
        return NULL;
    }

    for (int i = 0; i < PyList_Size((PyObject *)_hist); i++)
    {
        PyObject *tmp_obj = PyList_GetItem((PyObject *)_hist, i);
        Sample s(tmp_obj);
        s.print();
        if (i == 100)
            break;
        // _Py_DECREF(tmp_obj);
    }

    return (PyObject *)_hist;
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