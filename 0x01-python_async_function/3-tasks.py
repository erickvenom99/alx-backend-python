#!/usr/bin/env python3

"""
Module contains a function that returns an asyncio task.
"""

import asyncio
from typing import Coroutine
wait_random = __import__('0-basic_async_syntax').wait_random


def task_wait_random(max_delay: int) -> asyncio.Task:
    """
    Creates an asyncio.Task for wait_random with the specified max_delay.

    Args:
        - max_delay (int): Maximum delay for wait_random.

    Returns:
        - asyncio.Task: Task object representing the execution of wait_random.
    """
    return asyncio.create_task(wait_random(max_delay))
