# VL Program: loops_demo
# Type: script
# Target: javascript

from typing import List, Dict, Any

def sumRange(i0: int, i1: int) -> int:
    sum = 0
    for n in i0 range i1:
        sum += n
    return sum

def countdown(i0: int) -> List[Any]:
    result = []
    counter = i0
    while counter > 0:
        result.push(counter)
        counter- = 1
    return result

def multiplicationTable(i0: int) -> List[Any]:
    table = []
    for i in 1 range i0:
        for j in 1 range i0:
            table.push({'i': i, 'j': j, 'product': i * j})
    return table

total = sumRange(1, 100)

# Exported: sumRange