from __future__ import annotations
from typing import Generic, Iterator, TypeVar, Any
from abc import ABC
from collections.abc import Collection
from tabulate import tabulate
import json


T = TypeVar('T')



class BaseGroup(Generic[T], ABC, Collection[T]):
    people: Collection[T]

    def __init__(self, people: Collection[T]) -> None:
        ...

    def __iter__(self) -> Iterator[T]:
        yield from self.people
    
    def __len__(self) -> int:
        return len(self.people)
    
    def __contains__(self, obj: Any):
        return obj in self.people


class BaseRound(Generic[T], ABC, Collection[Collection[T]]):
    groups: Collection[Collection[T]]
    people: Collection[int]
    num_groups: int
    group_sizes: Collection[tuple[int,int]]

    def __init__(self, groups:Collection[Collection[T]]) -> None:
        ...

    def __iter__(self) -> Iterator[Collection[T]]:
        yield from self.groups
    
    def __len__(self) -> int:
        return len(self.groups)
    
    def __contains__(self, obj: Any):
        return obj in self.groups



"""
Instances of this class represent solutions to instances of the Social Golfer Problem.
They are allocations of people to groups and rounds that also fulfill the solution requirements.
Instances are immutable. It should not be possible to create invalid solutions.
"""
class BaseAllocation(Generic[T], ABC, Collection[Collection[Collection[T]]]):
    people: Collection[T]
    num_groups: int
    group_sizes: Collection[tuple[int,int]]

    def __eq__(self, other: BaseAllocation) -> bool:
        if isinstance(other, BaseAllocation):
            return self.to_sets() == other.to_sets()
        return False

    @property
    def long_title(self) -> str:
        groups_str = ', '.join(f"{num} groups of {size}" for num, size in self.group_sizes)
        return f'{len(self.people)} people over {len(self)} rounds ({groups_str})'
    
    @property
    def short_title(self) -> str:
        title = f'{len(self.people)}@{len(self)}_'
        title += '_'.join(f"{num}x{size}" for num, size in self.group_sizes)
        return title

    def to_markdown(self) -> str:
        headers = ['Round'] + [f'Group {i+1}' for i in range(self.num_groups)]
        data = []
        for i, round in enumerate(self):
            row = [str(i+1)]
            row += [', '.join(map(str,group)) for group in round]
            data.append(row)
        return tabulate(data, headers, tablefmt="pipe")
    
    def to_sets(self) -> set[frozenset[frozenset[T]]]:
        new_alloc: set[frozenset[frozenset[T]]] = set()
        for round in self:
            new_alloc.add(frozenset(frozenset(group) for group in round))
        return new_alloc

    def to_lists(self) -> list[list[list[T]]]:
        return [[list(group) for group in round] for round in self]

    def to_json(self) -> str:
        return json.dumps(self.to_lists())
    