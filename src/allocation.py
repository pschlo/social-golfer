from __future__ import annotations
from collections.abc import Iterator
from tabulate import tabulate
from itertools import chain
from typing import Any, TypeVar, Generic, overload, cast
from collections.abc import Iterable, Collection
from base_allocation import BaseAllocation
from collections import Counter
from canonical_allocation import CanonicalAllocation
import json


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

    @overload
    def __init__(self, allocation: str):
        ...
    @overload
    def __init__(self, allocation: BaseAllocation[T]):
        ...
    @overload
    def __init__(self, allocation: Collection[Collection[Collection[T]]]):
        ...
    def __init__(self, allocation: str | BaseAllocation[T] | Collection[Collection[Collection[T]]]):
        if isinstance(allocation, BaseAllocation):
            return self._from_allocation(allocation)
        elif isinstance(allocation, str):
            return self._from_json(allocation)
        else:
            return self._from_collections(allocation)

    def __iter__(self) -> Iterator[Round[T]]:
        yield from self.rounds
    
    def __len__(self) -> int:
        return len(self.rounds)
    
    def _from_json(self, allocation: str):
        return self._from_collections(json.loads(allocation))
    
    def _from_allocation(self, allocation: BaseAllocation[T]):
        return self._from_collections(allocation.rounds)

    def _from_collections(self, allocation: Collection[Collection[Collection[T]]]):
        # convert to rounds and groups
        self.rounds: set[Round[T]] = set()
        for round in allocation:
            self.rounds.add(Round(Group(group) for group in round))

        # pick one round and copy attributes
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

    def to_lists(self) -> list[list[list[T]]]:
        return [[list(group) for group in round] for round in self]
    
    def to_canonical(self) -> CanonicalAllocation:
        return CanonicalAllocation(self)
