# VL Program: functions
# Type: function
# Target: python

from typing import List, Dict, Any

def add(i0: int, i1: int) -> int:
    return i0 + i1

def multiply(i0: int, i1: int) -> int:
    return i0 * i1

def max(i0: int, i1: int) -> int:
    return (i0 if i0 > i1 else i1)

def sum_range(i0: int) -> int:
    total = 0
    for idx in range(0, i0):
        total = total + idx
    return total

def double_all(i0: List[Any]) -> List[Any]:
    return [x * 2 for x in i0]

# Exported: add