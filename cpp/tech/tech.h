#include <string>
#include <iostream>
#include <vector>
#include <Python.h>

struct Sample
{
    std::string ts_code, trade_date;
    float open, close;
    Sample(PyObject *df_row);
    void print() const;
    bool operator>(Sample &rhs);
};

int get_streaks(std::vector<Sample> data, int streak_len, bool is_up);