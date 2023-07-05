from __future__ import annotations
from collections.abc import Collection
from base_allocation import BaseAllocation, BaseRound, BaseGroup
from typing import TYPE_CHECKING, Iterator, Collection, Any, TypeVar
if TYPE_CHECKING:
    from allocation import Allocation


T = TypeVar('T')

class CanonicalGroup(BaseGroup[T]):
    people: tuple[T,...]

    def __init__(self, people: Collection[T]) -> None:
        self.people = tuple(people)

    def __lt__(self, other: CanonicalGroup[T]):
        return self.people < other.people
    
    def __gt__(self, other: CanonicalGroup[T]):
        return self.people > other.people
    
    def __eq__(self, other: CanonicalGroup[T]):
        return self.people == other.people


class CanonicalRound(BaseRound[T]):
    groups: tuple[CanonicalGroup[T]]

    def __init__(self, groups: Collection[CanonicalGroup[T]]) -> None:
        self.groups = tuple(groups)
    
    def __lt__(self, other: CanonicalRound[T]):
        return self.groups < other.groups
    
    def __gt__(self, other: CanonicalRound[T]):
        return self.groups > other.groups
    
    def __eq__(self, other: CanonicalRound[T]):
        return self.groups == other.groups


"""
Instances of this class are allocations with a strict order on their people, groups, rounds, and group sizes.
"""
class CanonicalAllocation(BaseAllocation[T]):
    rounds: tuple[CanonicalRound[T]]
    people: tuple[int]
    num_groups: int
    group_sizes: tuple[tuple[int,int], ...]

    def __init__(self, allocation: Allocation) -> None:
        ...
