"""
This file contains global helper functions used in the project.
"""

from itertools import compress
from typing import List


def match_pattern_in_list(folder_list: List[str], pattern: str) -> List[str]:
    """This function finds the matching string in pattern.
    The matching is case-insensitive.

    Args:
        list (List[str]): List of strings to search from.
        pattern (str): Pattern to search for in list
    """
    if len(folder_list) > 0 and pattern not in [None, ""]:
        filter = [pattern.lower() == f.lower() for f in folder_list]
        if any(filter):
            return list(compress(folder_list, filter))
    else:
        return []
