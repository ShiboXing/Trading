from pandas import DataFrame as DF


def rsi(avg_gain, avg_loss):
    return 100 - (100 / (1 + avg_gain / float(abs(avg_loss))))
