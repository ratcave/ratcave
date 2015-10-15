__author__ = 'nickdg'

def countdown_timer(total_secs, stop_iteration=False):
    """Generates an iterator that returns the time remaining from total_time (secs). Returns 0.0 when time is up, unless
    stop_iteration is True."""

    import time
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
