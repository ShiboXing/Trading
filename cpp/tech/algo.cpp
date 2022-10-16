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

/**
 * @brief Get the streaks from data samples and write to output
 *
 * @param input (assumed sorted)
 * @param output will perform append-only write to output vector
 * @param streak_len
 * @param is_up
 * @return int
 */
int get_streaks(std::vector<Sample> &input, int streak_len, bool is_up, msm &shm, bip::interprocess_mutex &mtx)
{
    // string curr_code = data.ts_code;
    std::cout << "data len, len, is_up: " << input.size() << " " << streak_len << " " << is_up << std::endl;

    // build shared memory containers
    bip::allocator<char, msm::segment_manager> chr_altr(shm.get_segment_manager());
    typedef bip::basic_string<char, std::char_traits<char>, decltype(chr_altr)> str;
    bip::allocator<str, msm::segment_manager> str_altr(shm.get_segment_manager());
    typedef std::vector<str, decltype(str_altr)> vec;
    auto *res_vec = shm.find_or_construct<std::vector<str, decltype(str_altr)>>("res_vec")(str_altr);

    return 0;
}