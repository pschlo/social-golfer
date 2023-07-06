from __future__ import annotations
from allocation import Allocation
from typing import Generic, TypeVar, Iterator, overload
from collections.abc import Sequence
from base_allocation import BaseAllocation
from tabulate import tabulate
import json


T = TypeVar('T')
V = TypeVar('V')
W = TypeVar('W')


class AllocationView(BaseAllocation[T, V]):
    _allocation: Allocation
    _rounds: tuple[tuple[tuple[T]]]

    people: tuple[T]
    group_labels: tuple[V]

    num_people: int
    num_groups: int
    group_sizes: tuple[tuple[int,int]]

    def __init__(self, allocation: Allocation|AllocationView, people: Sequence[T], groups: Sequence[V]) -> None:
        if isinstance(allocation, AllocationView):
            allocation = allocation._allocation
        
        self._allocation = allocation

        if len(people) < allocation.num_people:
            raise ValueError("Not enough people labels")
        self.people = tuple(people[:allocation.num_people])

        if len(groups) < allocation.num_groups:
            raise ValueError("Not enough group labels")
        self.group_labels = tuple(groups)

        self.num_people = allocation.num_people
        self.num_groups = allocation.num_groups
        self.group_sizes = tuple(sorted(allocation.group_sizes, key=lambda t: t[1], reverse=True))

        new_alloc: list[tuple[tuple[T]]] = []
        for round in allocation:
            new_round: list[tuple[T]] = []
            for group in round:
                # sort people
                new_round.append(tuple(self.people[p] for p in sorted(group)))
            # sort groups
            new_round.sort()
            new_round.sort(key=len, reverse=True)
            new_alloc.append(tuple(new_round))
        # sort rounds
        self._rounds = tuple(sorted(new_alloc))

    def __iter__(self) -> Iterator[tuple[tuple[T]]]:
        yield from self._rounds
    
    def __len__(self) -> int:
        return len(self._rounds)

    def __contains__(self, obj: object) -> bool:
        return obj in self._rounds
    
    def __hash__(self) -> int:
        return hash(self._rounds)

    def __eq__(self, other: AllocationView | Allocation) -> bool:
        if isinstance(other, AllocationView):
            return other._rounds == self._rounds
        if isinstance(other, Allocation):
            return other == self._allocation
        return NotImplemented

    def to_markdown(self) -> str:
        headers = ['Round'] + [f'Group {i+1}' for i in range(self.num_groups)]
        data = []
        for i, round in enumerate(self):
            row = [str(i+1)]
            row += [', '.join(map(str,group)) for group in round]
            data.append(row)
        return tabulate(data, headers, tablefmt="pipe")

    def to_json(self) -> str:
        return json.dumps(self.to_lists())

    # map people to list of groups, where each position stands for a round
    def people_to_groups(self) -> dict[T, list[V]]:
        people_to_groups: dict[T, list[V]] = {p: [] for p in self.people}
        for round in self:
            for group, label in zip(round, self.group_labels):
                for person in group:
                    people_to_groups[person].append(label)
        # because each person appears exactly once per round, each person now has num_groups many group labels
        return people_to_groups
    
    def with_people(self, people: Sequence[W]) -> AllocationView[W, V]:
        return AllocationView(self, people, self.group_labels)

    def with_groups(self, groups: Sequence[W]) -> AllocationView[T, W]:
        return AllocationView(self, self.people, groups)


class IntAllocationView(AllocationView[int, int]):
    def __init__(self, allocation: Allocation) -> None:
        people = range(1, allocation.num_people+1)
        groups = range(1, allocation.num_groups+1)
        super().__init__(allocation, people, groups)
