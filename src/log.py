import time

prev_timer = None


def timed(message: str) -> None:
    global prev_timer

    now = time.perf_counter()
    if prev_timer is not None:
        message += f" [took {now - prev_timer:.2f}s]"

    prev_timer = now
    print(message)
