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
    merge_sort(delay_list)
    return delay_list


def merge_sort(arr: List[float]) -> None:
    """
    Sorts an array in place using the merge sort algorithm.
    """
    if len(arr) > 1:
        mid = len(arr) // 2
        left_half = arr[:mid]
        right_half = arr[mid:]

        merge_sort(left_half)
        merge_sort(right_half)

        i = j = k = 0
        while i < len(left_half) and j < len(right_half):
            if left_half[i] < right_half[j]:
                arr[k] = left_half[i]
                i += 1
            else:
                arr[k] = right_half[j]
                j += 1
            k += 1

        while i < len(left_half):
            arr[k] = left_half[i]
            i += 1
            k += 1

        while j < len(right_half):
            arr[k] = right_half[j]
            j += 1
            k += 1
