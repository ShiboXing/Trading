#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <iostream>
#include <string>
#include <vector>

using namespace std;

PyObject *day_streak(PyObject *self, PyObject *df)
{
    const char *command;

    if (!PyArg_ParseTuple(df, "s", &command))
        return NULL;
    cout << "command: " << string(command) << endl;

    return 0;
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
