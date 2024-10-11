#!/usr/bin/env python3


"""
 Module Annotate the below function’s parameters
 and return values with the appropriate types
"""

from typing import Iterable, Sequence, List, Tuple


def element_length(lst: Iterable[Sequence]) -> List[Tuple[Sequence, int]]:
    """Function returns:
            a list of tuples containing an element and its length
    """
    return [(i, len(i)) for i in lst]
