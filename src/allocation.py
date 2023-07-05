from __future__ import annotations
from collections.abc import Iterator
from itertools import chain
from typing import TypeVar, Generic, overload
from collections.abc import Iterable, Collection
from base_allocation import BaseAllocation
from collections import Counter
from canonical_allocation import CanonicalAllocation
import json


T = TypeVar('T')


class AllocationError(ValueError):
    pass



class Group(Collection[T]):
    _people: frozenset[T]

    def __init__(self, people: Iterable[T]):
        self._people = frozenset(people)
    
    def __iter__(self) -> Iterator[T]:
        yield from self._people

    def __len__(self):
        return len(self._people)
    
    def __contains__(self, obj):
        return obj in self._people


class Round(Collection[Group[T]]):
    _groups: frozenset[Group[T]]
    people: frozenset[T]
    group_sizes: frozenset[tuple[int,int]]

    def __init__(self, groups: Iterable[Group[T]]):
        self._groups = frozenset(groups)
        self.people = frozenset(chain(*self))

        # check that each person appears only once
        if not len(self.people) == len(list(chain(*self))):
            raise AllocationError("Invalid allocation")

        group_sizes = Counter(map(len, self)).items()
        self.group_sizes = frozenset((num, size) for size, num in group_sizes)

    def __iter__(self) -> Iterator[Group[T]]:
        yield from self._groups
    
    def __len__(self):
        return len(self._groups)
    
    def __contains__(self, obj):
        return obj in self._groups



"""
Instances of this class are allocations with no specific order on their people, groups, group sizes or rounds.
This provides a lot of flexibility and allows e.g. for fast comparison.
"""
class Allocation(BaseAllocation[T]):
    _rounds: frozenset[Round[T]]
    people: frozenset[T]
    num_groups: int
    group_sizes: frozenset[tuple[int,int]]

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
        yield from self._rounds
    
    def __len__(self) -> int:
        return len(self._rounds)

    def __contains__(self, obj: object) -> bool:
        return obj in self._rounds
    
    def _from_json(self, allocation: str):
        return self._from_collections(json.loads(allocation))
    
    def _from_allocation(self, allocation: BaseAllocation[T]):
        return self._from_collections(allocation)

    def _from_collections(self, allocation: Collection[Collection[Collection[T]]]):
        # convert to rounds and groups
        rounds = set()
        for round in allocation:
            rounds.add(Round(Group(group) for group in round))
        self._rounds = frozenset(rounds)

        # pick one round and copy attributes
        some_round = next(iter(self))
        self.people = some_round.people
        self.num_groups = len(some_round)
        self.group_sizes = some_round.group_sizes

        if not self.is_valid():
            raise AllocationError("Invalid allocation")

    def is_valid(self) -> bool:
        # check that rounds contain same people
        if not all(round.people == self.people for round in self):
            return False

        # check that rounds have the same group sizes
        if not all(round.group_sizes == self.group_sizes for round in self):
            return False

        # check if actual solution, i.e. that noone is in a group with another person more than once
        seen: dict[T, set[T]] = {p: set() for p in self.people}
        for round in self:
            for group in round:
                group = set(group)
                for person in group:
                    others = group - {person}
                    # check intersection
                    if seen[person] & others:
                        return False
                    seen[person].update(others)

        return True
