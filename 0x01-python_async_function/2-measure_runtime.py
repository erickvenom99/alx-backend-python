#!/usr/bin/env python3

"""
Module measures the average
execution time
"""


import time
import asyncio
wait_n = __import__('1-concurrent_coroutines').wait_n


def measure_time(n: int, max_delay: int) -> float:
    """
    Function to measure the average execution time.

    Args:
        - n (int): Number of times to call wait_n.
        - max_delay (int): Maximum delay for wait_n.

    Returns:
        - float: Average time taken per wait_n call.
    """
    start_time = time.time()
    asyncio.run(wait_n(n, max_delay))
    end_time = time.time()
    total_execution = end_time - start_time

    return total_execution / n
