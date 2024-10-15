#!/usr/bin/env python3

"""
Module creates a function wait_n to spawn wait_random
n number of times.
"""

from typing import List
import asyncio
wait_random = __import__('0-basic_async_syntax').wait_random


async def wait_n(n: int, max_delay: int) -> List[float]:
    """
    Function spawns wait_random n times.
    Args:
        n (int): Number of times to spawn wait_random.
        max_delay (int): Maximum delay for wait_random.
    Returns:
        A list of all the delays (float values) in ascending order.
    """
    delay_list: List[float] = []
    list_tasks = [wait_random(max_delay) for _ in range(n)]
    delay_task = await asyncio.gather(*list_tasks)

    for task in delay_task:
        delay_list.append(task)
    return sorted(delay_list)
