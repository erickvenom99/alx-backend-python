#!/usr/bin/env python3

"""
Module contains a function that returns sorted delays.
"""

import asyncio
from typing import List
task_wait_random = __import__('3-tasks').task_wait_random


async def task_wait_n(n: int, max_delay: int) -> List[float]:
    """
    Function spawns task_wait_random n times with the specified max_delay.

    Args:
        - n (int): Number of times to call task_wait_random.
        - max_delay (int): Maximum delay for task_wait_random.

    Returns:
        - List[float]: A list of delays in ascending order.
    """
    tasks = [task_wait_random(max_delay) for _ in range(n)]
    delays = await asyncio.gather(*tasks)
    return sorted(delays)
