#include "tech.h"
#include <set>
#include <deque>

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

/**
 * @brief Get the streaks from data samples and write to output
 *
 * @param input (assumed sorted)
 * @param output will perform append-only write to output vector
 * @param streak_len
 * @param is_up
 * @return int
 */
int get_streaks(std::vector<Sample> &input, int streak_len, bool is_up, vector<string> &res_vec)
{
    // string curr_code = data.ts_code;
    cout << "data len, len, is_up: " << input.size() << " " << streak_len << " " << is_up << endl;
    deque<Sample> states;
    string cur_code = input[0].ts_code;
    int i = 0;
    while (i < input.size())
    {
        if (states.size() == streak_len + 1)
        {
            res_vec.push_back(states[0].ts_code + "." + states[0].trade_date);
            states.pop_front();
        }
        if (states.size() && states.back().close > input[i].close)
            states.clear();
        states.push_back(input[i]);

        i++;
    }
    return 0;
}