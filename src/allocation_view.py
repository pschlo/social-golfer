from __future__ import annotations
from allocation import Allocation
from typing import Generic, TypeVar, Iterator, overload
from collections.abc import Sequence
from base_allocation import BaseAllocation


T = TypeVar('T')


class AllocationView(BaseAllocation[T]):
    _allocation: Allocation
    _rounds: tuple[tuple[tuple[T]]]
    people: tuple[T]
    num_people: int
    num_groups: int
    group_sizes: tuple[tuple[int,int]]

    def __init__(self, allocation: Allocation, people: Sequence[T]) -> None:
        if len(people) < allocation.num_people:
            raise ValueError("Not enough people labels")
        self.people = tuple(people[:allocation.num_people])
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
    

class IntAllocationView(AllocationView[int]):
    def __init__(self, allocation: Allocation) -> None:
        super().__init__(allocation, range(1, allocation.num_people+1))