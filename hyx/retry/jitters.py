import random


def full(delay: float) -> float:
    """
    Full Interval Jitter

    Draw a jitter value from [0, upper_bound] interval uniformly

    Reference: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
    """

    return random.uniform(0, delay)


def equal(delay: float) -> float:
    """
    Equal Jitter

    Reference: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
    """
    half_wait_time = 0.5 * delay

    return half_wait_time + random.uniform(0, half_wait_time)
