# source: https://gist.github.com/Depado/7925679

# Only dependency needed
import threading

# Dependency for the task
import datetime
import time

# Function wrapper 
def periodic_task(interval, times = -1):
    def outer_wrap(function):
        def wrap(*args, **kwargs):
            stop = threading.Event()
            def inner_wrap():
                i = 0
                while i != times and not stop.isSet():
                    stop.wait(interval)
                    function(*args, **kwargs)
                    i += 1

            t = threading.Timer(0, inner_wrap)
            t.daemon = True
            t.start()
            return stop
        return wrap
    return outer_wrap


@periodic_task(5)
def my_periodic_task():
    # This function is executed every 5 seconds
    print("I am executed at {}".format(datetime.datetime.now()))

# Call the function once to launch the periodic system
my_periodic_task()
# This task will run while the program is alive, so for testing purpose we're just going to sleep.
time.sleep(500)
