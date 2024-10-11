#!/usr/bin/env python3
"""
 Module uses a function to_kv Takes Two Arguments:
 """

from typing import Union, Tuple


def to_kv(k: str, v: Union[int, float]) -> Tuple[str, float]:
    """
    This function takes two arguements.
    Args:
        first argument is a k is string
        second argument is a square of int/float, annotated
        as float.
    Returns:
        True if all boxes can be opened otherwise False
    """
    return (k, float(v * v))
