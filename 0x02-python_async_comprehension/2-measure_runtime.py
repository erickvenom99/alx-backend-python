#!/usr/bin/env python3

"""
Module returns the total runtime
"""

import asyncio
from typing import List

async_comprehension = __import__('1-async_comprehension').async_comprehension


async def measure_runtime() -> float:
    """
    measure_runtime coroutine executes async_comprehension four times
    in parallel using asyncio.gather,
    measures the total runtime, and returns it.
    """
    start_time: float = asyncio.get_event_loop().time()
    await asyncio.gather(
        *(async_comprehension() for _ in range(4))
    )
    end_time: float = asyncio.get_event_loop().time()

    return end_time - start_time
