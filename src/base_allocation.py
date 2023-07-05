from __future__ import annotations
from typing import Generic, TypeVar
from abc import ABC
from collections.abc import Collection
from tabulate import tabulate
import json


T = TypeVar('T')


"""
Instances of this class represent solutions to instances of the Social Golfer Problem.
They are allocations of people to groups and rounds that also fulfill the solution requirements.
Instances are immutable. It should not be possible to create invalid solutions.
"""
class BaseAllocation(Generic[T], ABC, Collection[Collection[Collection[T]]]):
    _people: Collection[T]
    _num_groups: int
    _group_sizes: Collection[tuple[int,int]]

    @property
    def long_title(self) -> str:
        groups_str = ', '.join(f"{num} groups of {size}" for num, size in self._group_sizes)
        return f'{len(self._people)} people over {len(self)} rounds ({groups_str})'
    
    @property
    def short_title(self) -> str:
        title = f'{len(self._people)}@{len(self)}_'
        title += '_'.join(f"{num}x{size}" for num, size in self._group_sizes)
        return title

    def to_markdown(self) -> str:
        headers = ['Round'] + [f'Group {i+1}' for i in range(self._num_groups)]
        data = []
        for i, round in enumerate(self):
            row = [str(i+1)]
            row += [', '.join(map(str,group)) for group in round]
            data.append(row)
        return tabulate(data, headers, tablefmt="pipe")
    
    
    def to_lists(self) -> list[list[list[T]]]:
        return [[list(group) for group in round] for round in self]

    def to_json(self) -> str:
        return json.dumps(self.to_lists())
    
    @property
    def people(self):
        return self._people
    @property
    def num_groups(self):
        return self._num_groups
    @property
    def group_sizes(self):
        return self._group_sizes
