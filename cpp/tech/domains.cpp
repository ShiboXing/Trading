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
    PyArrayObject *_strs, *_nums;
    cout << " day streak before" << endl;
    if (!PyArg_ParseTuple(arr, "OO", &_strs, &_nums))
    {
        cout << "parse tuple failed";
        throw invalid_argument("parse tuple failed");
        return NULL;
    }

    cout << "day streak middle" << endl;

    int r = PyArray_DIM(_nums, 0), c = PyArray_DIM(_nums, 1);
    int r_strd = _nums->strides[0], c_strd = _nums->strides[1];
    cout << "r, c: " << r << "  " << c << endl;
    cout << "dim0, 1 strides: " << r_strd << "  " << c_strd << endl;
    double *arr2d0 = (double *)PyArray_DATA(_nums);
    cout << "arr2d0 dim0: " << arr2d0[0] << "  " << arr2d0[1] << "  " << arr2d0[2] << endl;
    cout << "arr2d0 dim1: " << arr2d0[c] << "  " << arr2d0[c + 1] << "  " << arr2d0[c + 2] << endl;

    // cout << "arr2d0 dim0: " << arr2d0[0] << "  " << (double)*(arr2d0 + c_strd) << "  " << (double)*(arr2d0 + 2 * c_strd) << endl;
    // cout << "arr2d0 dim1: " << arr2d0[0] << "  " << (double)*(arr2d0 + r_strd) << "  " << (double)*(arr2d0 + 2 * r_strd) << endl;

    return (PyObject *)_nums;
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