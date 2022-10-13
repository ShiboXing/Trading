#include "tech.h"

using namespace std;

Sample::Sample(PyObject *df_row)
{
    char *ts_code_tmp, *trade_date_tmp;
    assert((string)df_row->ob_type->tp_name == "list");
    PyArg_Parse(PyList_GetItem(df_row, 0), "s", &ts_code_tmp);
    PyArg_Parse(PyList_GetItem(df_row, 1), "s", &trade_date_tmp);
    PyArg_Parse(PyList_GetItem(df_row, 2), "f", &open);
    PyArg_Parse(PyList_GetItem(df_row, 3), "f", &close);

    ts_code = string(ts_code_tmp);
    trade_date = string(trade_date_tmp);
}

void Sample::print() const
{
    cout << "tscode, trade_date, open, close: ";
    cout << ts_code << " " << trade_date << " " << open << " " << close << endl;
}

bool Sample::operator>(Sample &rhs)
{
    if (ts_code != rhs.ts_code)
        return ts_code > rhs.ts_code;
    else
        return trade_date > rhs.trade_date;
}

int get_streaks(vector<Sample> data, int streak_len, bool is_up)
{
    cout << "data len, len, is_up: " << data.size() << " " << streak_len << " " << is_up << endl;
    return 0;
}