#include "tech.h"

/**
 * @brief return a list of day streak counts of a certain date and stock
 *
 * @param self python class
 * @param args contains a 2D list of tuples (code: str, date: Datetime, price: float, prev_price1: float, prev_price2: float, prev_streak: float)
 * @return PyList* of day streak count, with the same order as input 2d array
 */
static PyObject *day_streak(PyObject *self, PyObject *args)
{
    PyObject *_hist;
    PyArg_ParseTuple(args, "O", &_hist);
    for (int i = 0; i < PyList_Size(_hist); i++)
    {
        PyObject *row = PyList_GetItem(_hist, i);
        Sample s(row);
    }
    return NULL;
}