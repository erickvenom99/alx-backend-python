#!/usr/bin/env python3

"""
Module contains a coroutine that collects 10 random
numbers between 0 to 10 using async comprehension.
"""

import asyncio
from typing import List
async_generator = __import__('0-async_generator').async_generator


async def async_comprehension() -> List[float]:
    """
    Coroutine collects 10 random numbers between 0 to 10
    using async comprehension over async_generator.
    """
    return [item async for item in async_generator()]
