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



# class Group(Collection[int]):
#     _people: frozenset[int]

#     def __init__(self, people: Iterable[int]):
#         self._people = frozenset(people)
    
#     def __iter__(self) -> Iterator[int]:
#         yield from self._people

#     def __len__(self):
#         return len(self._people)
    
#     def __contains__(self, obj):
#         return obj in self._people
    
#     def __eq__(self, other: Group):
#         if isinstance(other, Group):
#             return self._people == other._people
#         return NotImplemented
    
#     def __hash__(self) -> int:
#         return hash(self._people)


# class Round(Collection[Group]):
#     _groups: frozenset[Group]
#     people: frozenset[int]
#     group_sizes: frozenset[tuple[int,int]]

#     def __init__(self, groups: Iterable[Group]):
#         self._groups = frozenset(groups)
#         self.people = frozenset(chain(*self))

#         # check that each person appears only once
#         if not len(self.people) == len(list(chain(*self))):
#             raise AllocationError("Invalid allocation")

#         group_sizes = Counter(map(len, self)).items()
#         self.group_sizes = frozenset((num, size) for size, num in group_sizes)

#     def __iter__(self) -> Iterator[Group]:
#         yield from self._groups
    
#     def __len__(self):
#         return len(self._groups)
    
#     def __contains__(self, obj):
#         return obj in self._groups
    
#     def __eq__(self, other: Round):
#         if isinstance(other, Round):
#             return self._groups == other._groups
#         return NotImplemented
    
#     def __hash__(self) -> int:
#         return hash(self._groups)

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
class Allocation(BaseAllocation[int]):
    _rounds: frozenset[frozenset[frozenset[int]]]
    num_people: int
    num_groups: int
    group_sizes: frozenset[tuple[int,int]]

    @overload
    def __init__(self, allocation: str):
        ...
    @overload
    def __init__(self, allocation: BaseAllocation):
        ...
    @overload
    def __init__(self, allocation: Collection[Collection[Collection]]):
        ...
    def __init__(self, allocation: str | BaseAllocation | Collection[Collection[Collection]]):
        if isinstance(allocation, BaseAllocation):
            return self._from_allocation(allocation)
        elif isinstance(allocation, str):
            return self._from_json(allocation)
        else:
            return self._from_collections(allocation)

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
    
    def _from_json(self, allocation: str):
        return self._from_collections(json.loads(allocation))
    
    def _from_allocation(self, allocation: BaseAllocation):
        return self._from_collections(allocation)
    
    def _from_collections(self, allocation: Collection[Collection[Collection[T]]]):
        some_round = next(iter(allocation))
        people = Round.people(some_round)
        group_sizes = Round.group_sizes(some_round)

        # verify that each person appears only once per round
        if not all(Round.is_people_unique(round) for round in allocation):
            return False

        # verify that every round has same people
        if not all(Round.people(round) == people for round in allocation):
            return False

        # verify that every round has same group sizes
        if not all(Round.group_sizes(round) == group_sizes for round in allocation):
            return False
        
        self.num_people = len(people)
        self.num_groups = len(some_round)
        self.group_sizes = group_sizes

        person_to_id = self._get_people_id_map(people)

        new_alloc: set[frozenset[frozenset[int]]] = set()
        for round in allocation:
            new_round: set[frozenset[int]] = set()
            for group in round:
                new_round.add(frozenset(person_to_id[p] for p in group))
            new_alloc.add(frozenset(new_round))
        self._rounds = frozenset(new_alloc)
        




        if not self.is_valid():
            raise AllocationError("Invalid allocation")
    
    def _get_people_id_map(self, people: Collection[T]) -> dict[T, int]:
        # try to sort people
        sorted_people: list
        try:
            p: Any = people
            sorted_people = sorted(p)
        except ValueError:
            sorted_people = list(people)
        return {person: i for i, person in enumerate(sorted_people)}
        
    # def _collections_to_rounds(self, allocation: Collection[Collection[Collection[T]]], person_to_id: dict[T, int]) -> frozenset[Round]:
    #     # convert to rounds and groups
    #     # also convert
    #     rounds: set[Round] = set()
    #     for round in allocation:
    #         tmp_round: set[Group] = set()
    #         for group in round:
    #             tmp_round.add(Group(person_to_id[p] for p in group))
    #         rounds.add(Round(tmp_round))
    #     return frozenset(rounds)

    def is_valid(self) -> bool:
        # check that rounds contain same people
        if not all(round.people == self.people for round in self):
            return False

        # check that rounds have the same group sizes
        if not all(round.group_sizes == self.group_sizes for round in self):
            return False

        # check if actual solution, i.e. that noone is in a group with another person more than once
        seen: dict[int, set[int]] = {p: set() for p in self.people}
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

    # map people to list of groups, where each position stands for a round
    @overload
    def people_to_groups(self) -> dict[int, list[int]]:
        ...
    @overload
    def people_to_groups(self, group_labels: list[str]) -> dict[int, list[str]]:
        ...
    def people_to_groups(self, group_labels: list[str]|None=None):
        people_to_groups: dict[int, list[Any]] = {p: [] for p in self.people}
        for round in self:
            for i, group in enumerate(round):
                for person in group:
                    label = group_labels[i] if group_labels else i
                    people_to_groups[person].append(label)
        # because each person appears exactly once per round, each person now has num_groups many group ids
        return people_to_groups





    
    def __hash__(self) -> int:
        return hash(self._rounds)
