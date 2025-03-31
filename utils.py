import os
import sys
from config import debug


def debug_print(text):
    if debug:
        print(text)


def sanitize_name(name):
    res = "".join([x if x.isalnum() else "_" for x in name.lower()])

    while "__" in res:
        res = res.replace("__", "_")

    while res[0] == "_":
        res = res[1:]

    while res[-1] == "_":
        res = res[0:-1]

    return res


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
