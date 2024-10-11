#!/usr/bin/env python3
"""
 Module contains two function make_multiplier
 and multiplier function that multipliers float
"""

from typing import Union, Tuple
from typing import Callable


def make_multiplier(multiplier: float) -> Callable[[float], float]:
    """
        Function multipliers a float by a multiplier
        Args:
            Takes a float multiplier as argument and
        Returs:
            function that multiplies a float by multiplier.
    """
    def multiplier_func(x: float) -> float:
        """
        The inside function multiplies a float
            defined in the outer function.
        """
        return x * multiplier
    return multiplier_func
