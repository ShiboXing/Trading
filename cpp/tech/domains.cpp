#include "tech.h"

using namespace std;

/**
 * @brief return a list of day streak counts of a certain date and stock
 *
 * @param self python class
 * @param args contains a 2D list of tuples (code: str, date: Datetime, price: float, prev_price1: float, prev_price2: float, prev_streak: float)
 * @return PyList* of day streak count, with the same order as input 2d array
 */
PyObject *day_streak(PyObject *self, PyObject *args)
{
    // parse input list
    PyObject *_hist;
    PyArg_ParseTuple(args, "O", &_hist);

    auto cnt_streak = [](ST_Sample &st)
    {
        float ret = st.price - st.prev_price1, prev_ret = st.prev_price1 - st.prev_price2;
        if ((ret < 0 && prev_ret < 0) || (ret > 0 && prev_ret > 0))
            st.prev_streak++;
        else
            st.prev_streak = 1;
    };

    // calculate the streak count row by row
    ST_Sample prev_s;
    PyObject *res_lst = PyList_New(0);
    for (int i = 0; i < PyList_Size(_hist); i++)
    {
        PyObject *row = PyList_GetItem(_hist, i);
        ST_Sample curr_s(row);

        if (prev_s.code == curr_s.code)
            curr_s.prev_streak = curr_s.prev_streak == 0 ? prev_s.prev_streak : curr_s.prev_streak;
        cnt_streak(curr_s);
        PyList_Append(res_lst, Py_BuildValue("H", curr_s.prev_streak));

        // iterate
        prev_s = curr_s;
    }
    Py_DECREF(_hist);

    return res_lst;
}
