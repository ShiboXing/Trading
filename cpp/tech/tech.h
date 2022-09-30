#include <string>
#include <iostream>
#include <vector>
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

int get_streaks(vector<Sample> data, int streak_len, bool is_up);