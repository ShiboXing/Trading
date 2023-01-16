#include "tech.h"

using namespace std;

/**
 * @brief get the moving average of close prices of the stocks
 *
 * @param self
 * @param args contains a 2D list of historical data, assumed sorted by (code: str, date: Datetime, price: float, prev_ma: float) compound key
 * @return PyList* of tuples (positive ma, negative ma), with the same order as the input list.
 */
static PyObject *ma(PyObject *self, PyObject *args)
{
    PyObject *_hist;
    PyArg_ParseTuple(args, "O", &_hist);

    // create lambda to calculate moving average
    auto get_ma = [](MA_Sample &s)
    {
        float ret = s.price - s.prev_price;
        if (ret >= 0)
        {
            s.pos_prev_ma = (s.pos_prev_ma * 13 + ret) / 14;
            s.neg_prev_ma = s.neg_prev_ma * 13 / 14;
        }
        else if (ret < 0)
        {
            s.pos_prev_ma = s.pos_prev_ma * 13 / 14;
            s.neg_prev_ma = (s.neg_prev_ma * 13 + ret) / 14;
        }
    };

    // calculate the postive and negative moving averages
    PyObject *res_lst = PyList_New(0);
    MA_Sample prev_s;
    for (int i = 0; i < PyList_Size(_hist); i++)
    {
        PyObject *row = PyList_GetItem(_hist, i);
        MA_Sample curr_s(row);
        if (curr_s.code != prev_s.code) // new code series
        {
            curr_s.prev_price = curr_s.prev_price == 0 ? curr_s.price : curr_s.prev_price;
        }
        else // inherit the previously calculated ma
        {
            curr_s.neg_prev_ma = prev_s.neg_prev_ma;
            curr_s.pos_prev_ma = prev_s.pos_prev_ma;
        }

        // calculate and collect
        get_ma(curr_s);
        PyList_Append(res_lst, PyTuple_Pack(2, Py_BuildValue("f", curr_s.pos_prev_ma), Py_BuildValue("f", curr_s.neg_prev_ma)));

        // iterate
        prev_s = curr_s;
    }

    Py_DECREF(_hist);

    return res_lst;
}

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
    for (int i = 0; i < 5; i++)
    {
        PyObject *row = PyList_GetItem(_hist, i);
        ST_Sample s(row);

        cout << string(s) << endl;
    }
    PyObject *res;
    return res;
}

static PyMethodDef tech_methods[] = {
    {"ma", (PyCFunction)ma, METH_VARARGS, "calculate the returns' moving averages"},
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