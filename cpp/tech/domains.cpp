#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <iostream>
#include <string>
#include <vector>

using namespace std;

struct custom_obj
{
    bool a;
    char x, y, z;
};

PyObject *day_streak(PyObject *self, PyObject *df)
{
    custom_obj *obj;
    PyObject res;

    if (!PyArg_ParseTuple(df, "O", &obj))
        return NULL;
    cout << "object: " << obj->x << "  " << obj->y << "  " << obj->z << endl;

    return &res;
}

static PyMethodDef tech_methods[] = {
    {"day_streak", (PyCFunction)day_streak, METH_VARARGS, "calculate the streak signals"},
    {NULL, NULL, 0, NULL}};

static PyModuleDef tech_module = {
    PyModuleDef_HEAD_INIT,
    "tech",
    "technical analysis signals",
    0,
    tech_methods};

PyMODINIT_FUNC PyInit_tech_cpp()
{
    return PyModule_Create(&tech_module);
}

// class obj:
//     def __init__(self):
//         self.a = 0.123
//         self.b = 1
//         self.c = 'f'