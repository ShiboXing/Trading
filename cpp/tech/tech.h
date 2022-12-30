#include <string>
#include <iostream>
#include <vector>
#include <Python.h>
#include <assert.h>
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
    float prev_ma;
    Sample(PyObject *df_row)
    {
        char *ts_code_tmp, *trade_date_tmp;
        PyArg_Parse(PyList_GetItem(df_row, 0), "s", &ts_code_tmp);
        PyArg_Parse(PyList_GetItem(df_row, 1), "s", &trade_date_tmp);
        PyArg_Parse(PyList_GetItem(df_row, 2), "f", &price);
        if (PyList_GET_SIZE(df_row) > 3)
        {
            float tmp_ma;
            PyArg_Parse(PyList_GetItem(df_row, 3), "f", &tmp_ma);
            std::cout << "args: " << ts_code_tmp << " " << trade_date_tmp << " " << price << "  " << tmp_ma << "\n";
            exit(1);

            PyArg_Parse(PyList_GetItem(df_row, 3), "f", &prev_ma);
        }
        std::cout << "prev_ma: " << prev_ma << '\n';
        std::cout << "row type: " << df_row->ob_type->tp_name << '\n';
        code = std::string(ts_code_tmp);
        trade_date = std::string(trade_date_tmp);
    }

    void print() const
    {
        std::cout << "code, trade_date, price";
        std::cout << code << " " << trade_date << " " << price << "\n";
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
