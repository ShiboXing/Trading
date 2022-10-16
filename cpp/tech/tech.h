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
    std::string ts_code, trade_date;
    float open, close;
    Sample(PyObject *df_row);
    void print() const;
    bool operator>(Sample &rhs);
};

int get_streaks(std::vector<Sample> &input, int streak_len, bool is_up, bip::interprocess_mutex mtx);
