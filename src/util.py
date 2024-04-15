import time
import datetime
import json
from functools import wraps

class TimeCheck:
    def __init__(self, func):
        self.func = func
        
    def __call__(self):
        start = time.time()
        self.func()
        end = time.time()
        sec = end-start
        print(f"{datetime.timedelta(seconds=sec)}초 걸림")


def timeCheck_function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        sec = end_time - start_time
        print(f"Function {func.__name__} executed in {sec} seconds.")
        return result
    return wrapper