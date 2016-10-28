import time

def countdown_timer(total_secs, stop_iteration=False):
    """Generates an iterator that returns the time remaining from total_time (secs). Returns 0.0 when time is up, unless
    stop_iteration is True."""


    end_secs = time.time() + total_secs
    while True:
        remaining_secs = end_secs - time.time()
        if remaining_secs > 0.:
            yield remaining_secs
        else:
            if stop_iteration:
                raise StopIteration("Time is up!")
            else:
                yield 0.0  # Don't raise a StopIteration error, just return 0

def dt_timer():
    """A Generator that returns the time since last called. Never returns StopIteration."""
    last_time = time.time()
    while True:
        new_time = time.time()
        dt = new_time - last_time
        last_time = new_time
        yield dt