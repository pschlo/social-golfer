from __future__ import annotations
from collections.abc import Iterator
from itertools import chain
from typing import TypeVar, Generic, overload, Any
from collections.abc import Iterable, Collection
from base_allocation import BaseAllocation
from collections import Counter
import json


T = TypeVar('T')


class AllocationError(ValueError):
    pass


class People:
    @staticmethod
    def get_id_map(people: Collection[T]) -> dict[T, int]:
        # try to sort people
        sorted_people: list
        try:
            p: Any = people
            sorted_people = sorted(p)
        except ValueError:
            sorted_people = list(people)
        return {person: i for i, person in enumerate(sorted_people)}


class Round:
    @staticmethod
    def group_sizes(round: Collection[Collection[T]]) -> frozenset[tuple[int,int]]:
        tmp = Counter(map(len, round)).items()
        return frozenset((num, size) for size, num in tmp)
    
    @staticmethod
    def people(round: Collection[Collection[T]]) -> frozenset[T]:
        return frozenset(chain(*round))
    
    @staticmethod
    def is_people_unique(round: Collection[Collection[T]]) -> bool:
        if not len(Round.people(round)) == len(list(chain(*round))):
            return False
        return True


"""
Instances of this class are allocations with no specific order on their people, groups, group sizes or rounds.
This provides a lot of flexibility and allows e.g. for fast comparison.
"""
class Allocation(BaseAllocation[int, int]):
    _rounds: frozenset[frozenset[frozenset[int]]]
    
    num_people: int
    num_groups: int
    group_sizes: frozenset[tuple[int,int]]

    @overload
    def __init__(self, allocation: str):
        ...
    @overload
    def __init__(self, allocation: Collection[Collection[Collection]]):
        ...
    def __init__(self, allocation: str | Collection[Collection[Collection]]):
        if isinstance(allocation, str):
           a: Collection[Collection[Collection]] = json.loads(allocation)
           allocation = a

        some_round = next(iter(allocation))
        people = Round.people(some_round)
        group_sizes = Round.group_sizes(some_round)

        # verify that each person appears only once per round
        if not all(Round.is_people_unique(round) for round in allocation):
            raise AllocationError("People appear multiple times per round")

        # verify that every round has same people
        if not all(Round.people(round) == people for round in allocation):
            raise AllocationError("Rounds have different people")

        # verify that every round has same group sizes
        if not all(Round.group_sizes(round) == group_sizes for round in allocation):
            raise AllocationError("Rounds have different group sizes")
        
        self.num_people = len(people)
        self.num_groups = len(some_round)
        self.group_sizes = group_sizes

        self.set_rounds(people, allocation)
        
        if not self.is_solution():
            raise AllocationError("Not a solution")

    def __iter__(self) -> Iterator[frozenset[frozenset[int]]]:
        yield from self._rounds
    
    def __len__(self) -> int:
        return len(self._rounds)

    def __contains__(self, obj: object) -> bool:
        return obj in self._rounds
    
    def __eq__(self, other: Allocation):
        if isinstance(other, Allocation):
            return self._rounds == other._rounds
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._rounds)

    def set_rounds(self, people: Collection[T], allocation: Collection[Collection[Collection[T]]]):
        person_to_id = People.get_id_map(people)

        new_alloc: set[frozenset[frozenset[int]]] = set()
        for round in allocation:
            new_round: set[frozenset[int]] = set()
            for group in round:
                new_round.add(frozenset(person_to_id[p] for p in group))
            new_alloc.add(frozenset(new_round))
        self._rounds = frozenset(new_alloc)

    def is_solution(self) -> bool:
        # verify that noone is in a group with another person more than once
        seen: dict[int, set[int]] = {p: set() for p in range(self.num_people)}
        for round in self:
            for group in round:
                for person in group:
                    others = group - {person}
                    if seen[person] & others:
                        return False
                    seen[person].update(others)
        return True


