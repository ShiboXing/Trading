#include "tech.h"
#include <set>
#include <deque>

using namespace std;

/**
 * @brief Get the streaks from data samples and write to output
 *
 * @param input (assumed sorted)
 * @param output will perform append-only write to output vector
 * @param streak_len
 * @param is_up
 * @return int
 */
int get_streaks(std::vector<Sample> &input, unsigned int streak_len, bool is_up, std::vector<std::string> &res_vec)
{
    deque<Sample> states;
    string cur_code = input[0].code;
    unsigned int i = 0;
    function<bool(float, float)> cmptr = less<float>();
    if (is_up) // I have no idea why the ternary operator won't work here, any C++ expert?
        cmptr = greater<float>();
    while (i < input.size())
    {
        if (states.size() == streak_len + 1)
        {
            // formulate the sample string
            string sample_str;
            for (unsigned j = 1; j < states.size(); j++)
            {
                auto &s = states[j];
                sample_str += " " + s.code + "_" + s.trade_date + "_" + to_string(s.price);
            }
            res_vec.push_back(sample_str);
            states.pop_front();
        }
        if (states.size() && cmptr(states.back().price, input[i].price)) // test if streak is broken by the next sample
            states.clear();
        states.push_back(input[i]);

        i++;
    }
    return 0;
}