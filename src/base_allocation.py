from __future__ import annotations
from typing import Generic, TypeVar, overload, cast
from abc import ABC
from collections.abc import Collection


T = TypeVar('T')
V = TypeVar('V')


"""
Instances of this class represent solutions to instances of the Social Golfer Problem.
They are allocations of people to groups and rounds that also fulfill the solution requirements.
Instances are immutable. It should not be possible to create invalid solutions.
"""
class BaseAllocation(Generic[T, V], ABC, Collection[Collection[Collection[T]]]):
    num_people: int
    num_groups: int
    group_sizes: Collection[tuple[int,int]]

    @property
    def long_title(self) -> str:
        groups_str = ', '.join(f"{num} groups of {size}" for num, size in self.group_sizes)
        return f'{self.num_people} people over {len(self)} rounds ({groups_str})'
    
    @property
    def short_title(self) -> str:
        title = f'{self.num_people}@{len(self)}_'
        title += '_'.join(f"{num}x{size}" for num, size in self.group_sizes)
        return title
    
    def to_lists(self) -> list[list[list[T]]]:
        return [[list(group) for group in round] for round in self]

