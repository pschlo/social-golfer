from __future__ import annotations
from base_allocation import BaseAllocation
from typing import TYPE_CHECKING, Iterator, Collection
from allocation import Allocation


"""
Instances of this class have a specific order defined on their people, groups, group sizes and rounds.
"""
class CanonicalAllocation(BaseAllocation[int]):
    _allocation: Allocation
    _rounds: tuple[tuple[tuple[int]]]
    people: tuple[int]
    num_groups: int
    group_sizes: tuple[tuple[int,int]]

    def __init__(self, allocation: Allocation) -> None:
        self._allocation = allocation

        # try to sort people
        sorted_people: list
        try:
            sorted_people = sorted(allocation.people)
        except ValueError:
            sorted_people = list(allocation.people)

        #convert people to ids, which start at 1
        person_to_id = {person: i+1 for i, person in enumerate(sorted_people)}

        self.people = tuple(sorted(person_to_id[p] for p in allocation.people))
        self.num_groups = allocation.num_groups
        self.group_sizes = tuple(sorted(allocation.group_sizes, key=lambda t: t[1], reverse=True))

        new_alloc = []
        for round in allocation:
            new_round: list[list[int]] = []
            for group in round:
                # sort people
                new_round.append(sorted(person_to_id[p] for p in group))
            # sort groups
            new_round.sort()
            new_round.sort(key=len, reverse=True)
            new_alloc.append(new_round)
        # sort rounds
        self._rounds = tuple(sorted(new_alloc))
    
    def __iter__(self) -> Iterator[Collection[Collection[int]]]:
        yield from self._rounds
    
    def __len__(self) -> int:
        return len(self._rounds)
    
    def __contains__(self, obj: object) -> bool:
        return obj in self._rounds
    
    def __eq__(self, other: CanonicalAllocation | Allocation) -> bool:
        if isinstance(other, CanonicalAllocation):
            return other._rounds == self._rounds
        if isinstance(other, Allocation):
            return other == self._allocation
        return False