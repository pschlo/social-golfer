from __future__ import annotations
from typing import Generic, TypeVar
from abc import ABC, abstractmethod
from collections.abc import Collection
from tabulate import tabulate
import json


T = TypeVar('T')

class BaseAllocation(Generic[T], ABC):
    rounds: Collection[Collection[Collection[T]]]
    people: Collection[T]
    num_groups: int
    group_sizes: Collection[tuple[int,int]]

    @property
    def long_title(self) -> str:
        groups_str = ', '.join(f"{num} groups of {size}" for num, size in self.group_sizes)
        return f'{len(self.people)} people over {len(self.rounds)} rounds ({groups_str})'
    
    @property
    def short_title(self) -> str:
        title = f'{len(self.people)}@{len(self.rounds)}_'
        title += '_'.join(f"{num}x{size}" for num, size in self.group_sizes)
        return title

    def to_markdown(self) -> str:
        headers = ['Round'] + [f'Group {i+1}' for i in range(self.num_groups)]
        data = []
        for i, round in enumerate(self.rounds):
            row = [str(i+1)]
            row += [', '.join(map(str,group)) for group in round]
            data.append(row)
        return tabulate(data, headers, tablefmt="pipe")

    def to_json(self) -> str:
        return json.dumps(self.rounds)
