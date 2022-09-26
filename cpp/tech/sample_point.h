#include <string>

using namespace std;

struct Sample
{
    char *ts_code, *trade_date;
    float open, close;
    Sample(PyObject *df_row)
    {
        assert((string)df_row->ob_type->tp_name == "list");
        PyArg_Parse(PyList_GetItem(df_row, 0), "s", &ts_code);
        PyArg_Parse(PyList_GetItem(df_row, 1), "s", &trade_date);
        PyArg_Parse(PyList_GetItem(df_row, 2), "f", &open);
        PyArg_Parse(PyList_GetItem(df_row, 3), "f", &close);
    }

    void print()
    {
        cout << "tscode, trade_date, open, close: ";
        cout << ts_code << " " << trade_date << " " << open << " " << close << endl;
    }
};