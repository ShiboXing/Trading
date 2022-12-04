#include <string>
#include <iostream>
#include <vector>
#include <Python.h>
#include <boost/version.hpp>
#include <boost/interprocess/managed_shared_memory.hpp>
#include <boost/interprocess/containers/map.hpp>
#include <boost/interprocess/containers/string.hpp>
#include <boost/interprocess/containers/vector.hpp>
#include <boost/interprocess/allocators/allocator.hpp>
#include <boost/interprocess/sync/interprocess_mutex.hpp>
#include <boost/interprocess/sync/scoped_lock.hpp>

namespace bip = boost::interprocess;
typedef bip::managed_shared_memory msm;

struct Sample
{
    std::string code, trade_date;
    float price;
    Sample(PyObject *df_row)
    {
        char *ts_code_tmp, *trade_date_tmp;
        assert((string)df_row->ob_type->tp_name == "list");
        PyArg_Parse(PyList_GetItem(df_row, 0), "s", &ts_code_tmp);
        PyArg_Parse(PyList_GetItem(df_row, 1), "s", &trade_date_tmp);
        PyArg_Parse(PyList_GetItem(df_row, 2), "f", &price);

        code = string(ts_code_tmp);
        trade_date = string(trade_date_tmp);
    }

    void print() const
    {
        cout << "code, trade_date, price";
        cout << code << " " << trade_date << " " << price << endl;
    }

    bool operator>(Sample &rhs)
    {
        if (code != rhs.code)
            return code > rhs.code;
        else
            return trade_date > rhs.trade_date;
    }
};

int get_streaks(std::vector<Sample> &input, unsigned int streak_len, bool is_up, std::vector<std::string> &res_vec);
