#!/usr/bin/env python3

"""
 Function takes a mixed list and return sum of float
"""

from typing import List, Union


def sum_mixed_list(mxd_lst: List[Union[int, float]]) -> float:
    """
    This function takes a list of integers and floats
 and returns their sum as a float.
    """
    return float(sum(mxd_lst))
