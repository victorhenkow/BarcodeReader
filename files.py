# Code written by Victor Henkow, August 2023

# This module contains functions related to controlling files

import pandas as pd
import sys
import time


def save(dic, file_name):
    df = pd.DataFrame(dic)
    df.to_pickle("./" + file_name)


def readToDict(file_name):
    df = pd.read_pickle(file_name)
    dic = df.to_dict()
    return dic


def readToDictList(file_name):
    df = pd.read_pickle(file_name)
    dic = df.to_dict(orient='list')
    return dic


def existInDict(key, dic):
    if key in dic:
        return True
    else:
        return False


class Logger(object):
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "a")

    def write(self, message):
        # Every print, this function gets called twice, once where has length = 1. If the time_stamp is added every
        # time it will result in the time stamp printing twice.
        if len(message) != 1:
            time_stamp = time.ctime(time.time())
            message = time_stamp + "\t" + message + "\n"  # adding a newline between all print to make it easier to read

        self.terminal.write(message)
        self.log.write(message)

    # needed for compatibility, but does nothing
    def flush(self):
        pass
