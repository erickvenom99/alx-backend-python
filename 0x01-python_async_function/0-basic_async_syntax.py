#!/usr/bin/env python3

"""
    An asynchronous coroutine that takes in an integer argument
"""
import asyncio
import random


async def wait_random(max_delay=10):
    """
        funtion is an asychronous coroutine
        Args:
            max_delay (int): Maximum delay for wait_n.
        Returns:
            random delays
    """
    random_delay = random.uniform(0, max_delay)
    await asyncio.sleep(random_delay)
    return random_delay
