#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <arrayobject.h>
#include <iostream>
#include <string>
#include <vector>
#include <stdexcept>

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

    int num_lines = PyList_Size((PyObject *)_hist);
    cout << "num lines: " << num_lines << endl;
    PyObject *line0 = PyList_GetItem((PyObject *)_hist, 0);
    int num_elems = PyList_Size(line0);
    cout << "line0 num elems: " << num_elems << endl;
    cout << "print line 0: " << endl;
    for (int i = 0; i < PyList_Size(line0); i++)
    {
        auto tmp_obj = PyList_GetItem(line0, i);
        if ((string)tmp_obj->ob_type->tp_name == "float")
        {
            float f = 0;
            PyArg_Parse(PyList_GetItem(line0, i), "f", &f);
            cout << f << " ";
        }
        else if ((string)tmp_obj->ob_type->tp_name == "str")
        {
            const char *s = 0;
            PyArg_Parse(PyList_GetItem(line0, i), "s", &s);
            cout << s << " ";
        }
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

// class obj:
//     def __init__(self):
//         self.a = 0.123
//         self.b = 1
//         self.c = 'f'