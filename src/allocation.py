from __future__ import annotations
from collections.abc import Iterator
from itertools import chain
from typing import TypeVar, Generic, overload
from collections.abc import Iterable, Collection
from base_allocation import BaseAllocation
from collections import Counter
from my_canonical_allocation import MyCanonicalAllocation
import json


T = TypeVar('T')


class AllocationError(ValueError):
    pass



class Group(Generic[T], Collection[T]):
    _people: frozenset[T]

    def __init__(self, people: Iterable[T]):
        self._people = frozenset(people)
    
    def __iter__(self) -> Iterator[T]:
        yield from self._people

    def __len__(self):
        return len(self._people)
    
    def __contains__(self, obj):
        return obj in self._people

    def __eq__(self, other: Iterable) -> bool:
        if isinstance(other, Group):
            return self._people == other._people
        if isinstance(other, Iterable):
            return self._people == set(other)
        return False
    
    def to_set(self):
        return 


class Round(Generic[T], Collection[Group[T]]):
    _groups: frozenset[Group[T]]
    _people: frozenset[T]
    _group_sizes: frozenset[tuple[int,int]]

    def __init__(self, groups: Iterable[Group[T]]):
        self._groups = frozenset(groups)
        self._people = frozenset(chain(*self))

        # check that each person appears only once
        if not len(self._people) == len(list(chain(*self))):
            raise AllocationError("Invalid allocation")

        group_sizes = Counter(map(len, self)).items()
        self._group_sizes = frozenset((num, size) for size, num in group_sizes)

    def __iter__(self) -> Iterator[Group[T]]:
        yield from self._groups
    
    def __len__(self):
        return len(self._groups)
    
    def __contains__(self, obj):
        return obj in self._groups
    
    def __eq__(self, other: Iterable) -> bool:
        if isinstance(other, Round):
            return self._groups == other._groups
        if isinstance(other, Iterable):
            return 
        return False

    @property
    def people(self):
        return self._people
    @property
    def group_sizes(self):
        return self._group_sizes


"""
Instances of this class are allocations with no predefined order defined for its people, groups, rounds or group sizes.
This allows for faster lookup and more flexibility.
"""
class Allocation(Generic[T], BaseAllocation[T]):
    _rounds: frozenset[Round[T]]
    _people: frozenset[T]
    _num_groups: int
    _group_sizes: frozenset[tuple[int,int]]
    _canonical: CanonicalAllocation

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
        yield from self._canonical
    
    def __len__(self) -> int:
        return len(self._rounds)

    def __contains__(self, obj: object) -> bool:
        return obj in self._rounds

    def __eq__(self, other: BaseAllocation) -> bool:
        if isinstance(other, Allocation):
            return self._rounds == other._rounds
        elif isinstance(other, BaseAllocation):
            return set(self._rounds) == set(other)
        return False
    
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
        self._people = some_round.people
        self._num_groups = len(some_round)
        self._group_sizes = some_round.group_sizes
        
        # set canonical representation
        self._canonical = MyCanonicalAllocation(self)


    def is_valid(self):
        some_round = next(iter(self))

        # check that rounds contain same people
        if not all(round.people == self._people for round in self):
            raise AllocationError("Invalid allocation")

        # check that rounds have the same group sizes
        if not all(round.group_sizes == some_round.group_sizes for round in self):
            raise AllocationError("Invalid allocation")

        # check if actual solution, i.e. that noone is in a group with another person more than once
        seen: dict[T, set[T]] = {p: set() for p in self._people}
        for round in self:
            for group in round:
                group = set(group)
                for person in group:
                    others = group - {person}
                    # check intersection
                    if seen[person] & others:
                        raise AllocationError("Invalid allocation")
                    seen[person].update(others)

    @property
    def people(self):
        return self._canonical.people
    @property
    def num_groups(self):
        return self._canonical.num_groups
    @property
    def group_sizes(self):
        return self._canonical.group_sizes