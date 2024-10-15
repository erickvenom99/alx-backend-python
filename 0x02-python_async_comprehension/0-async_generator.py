#!/usr/bin/env python3

"""
Module generates a random number
from 0 to 10
"""

import asyncio
import random
from typing import Generator


async def async_generator() -> Generator[float, None, None]:
    """
    Coroutine yields a random number from 0 to 10
    each time pausing a second after each number is
    generated
    """
    for _ in range(10):
        await asyncio.sleep(1)
        yield random.uniform(0, 10)
