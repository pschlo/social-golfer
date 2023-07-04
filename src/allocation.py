from __future__ import annotations
from collections.abc import Iterator
from tabulate import tabulate
from itertools import chain
from typing import Any, TypeVar, Generic
from collections.abc import Iterable
from base_allocation import BaseAllocation
from collections import Counter


T = TypeVar('T')


class AllocationError(ValueError):
    pass



class Group(Generic[T]):
    people: set[T]

    def __init__(self, people: Iterable[T]):
        self.people = set(people)
    
    def __iter__(self) -> Iterator[T]:
        yield from self.people

    def __len__(self):
        return len(self.people)


class Round(Generic[T]):
    groups: set[Group[T]]
    people: set[T]
    group_sizes: set[tuple[int,int]]

    def __init__(self, groups: Iterable[Group[T]]):
        self.groups = set(groups)
        self.people = set(chain(*self))

        # check that each person appears only once
        if not len(self.people) == len(list(chain(*self))):
            raise AllocationError("Invalid allocation")

        group_sizes = Counter(map(len, self)).items()
        self.group_sizes = {(num, size) for size, num in group_sizes}

    def __iter__(self) -> Iterator[Group[T]]:
        yield from self.groups
    
    def __len__(self):
        return len(self.groups)


class Allocation(Generic[T], BaseAllocation[T]):
    rounds: set[Round[T]]
    people: set[T]
    num_groups: int
    group_sizes: set[tuple[int,int]]

    def __init__(self, rounds: Iterable[Round[T]]):
        self.rounds = set(rounds)

        some_round = next(iter(self))
        self.people = some_round.people
        self.num_groups = len(some_round)
        self.group_sizes = some_round.group_sizes

        # check that rounds contain same people
        if not all(round.people == self.people for round in self):
            raise AllocationError("Invalid allocation")

        # check that all rounds have the same group sizes
        if not all(round.group_sizes == some_round.group_sizes for round in self):
            raise AllocationError("Invalid allocation")

        # check if actual solution, i.e. that noone is in a group with another person more than once
        seen: dict[T, set[T]] = {p: set() for p in self.people}
        for round in self:
            for group in round:
                group = set(group)
                for person in group:
                    others = group - {person}
                    # check intersection
                    if seen[person] & others:
                        raise AllocationError("Invalid allocation")
                    seen[person].update(others)

    def __iter__(self) -> Iterator[Round[T]]:
        yield from self.rounds
    
    def __len__(self) -> int:
        return len(self.rounds)

    @staticmethod
    def from_lists(allocation: list[list[list[T]]]) -> Allocation[T]:
        rounds: set[Round[T]] = set()
        for round in allocation:
            rounds.add(Round(Group(group) for group in round))
        return Allocation(rounds)
    

    def to_lists(self) -> list[list[list[T]]]:
        return [[list(group) for group in round] for round in self]
    
    # def to_canonical(self) -> list[list[list[int]]]:
    #     #convert people to ids, which start at 1
    #     person_to_id = {person: i+1 for i, person in enumerate(self.people)}

    #     allocation: list[list[list[int]]] = []
    #     for round in self:
    #         new_round: list[list[int]] = []
    #         for group in round:
    #             # sort people
    #             new_round.append(sorted(person_to_id[person] for person in group))
    #         # sort groups
    #         new_round.sort()
    #         new_round.sort(key=len, reverse=True)
    #         allocation.append(new_round)

    #     # sort rounds
    #     allocation.sort()
    #     return allocation
        

