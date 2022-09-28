#include <string>
#include <iostream>
#include <Python.h>

using namespace std;

struct Sample
{
    string ts_code, trade_date;
    float open, close;
    Sample(PyObject *df_row);
    void print() const;
    bool operator>(Sample &rhs);
};