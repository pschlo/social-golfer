from __future__ import annotations
from collections.abc import Collection
from typing import Collection, Any
from canonical_allocation import CanonicalGroup, CanonicalRound, CanonicalAllocation
from allocation import Allocation



class MyCanonicalGroup(CanonicalGroup[int]):
    def __init__(self, people: Collection[int]) -> None:
        super().__init__(sorted(people))


class MyCanonicalRound(CanonicalRound[int]):
    def __init__(self, groups: Collection[MyCanonicalGroup]) -> None:
        super().__init__(sorted(groups, key=len, reverse=True))


"""
Instances of this class are allocations with a strict order on their people, groups, rounds, and group sizes.
"""
class MyCanonicalAllocation(CanonicalAllocation[int]):
    group_to_canonical: dict[Any,Any]
    round_to_canonical: dict[Any,Any]

    # def __init__(self, rounds: Collection[MyCanonicalRound]) -> None:
    #     super().__init__(sorted(rounds))

    def __init__(self, allocation: Allocation):
        # try to sort people
        sorted_people: list
        try:
            sorted_people = sorted(allocation.people)
        except ValueError:
            sorted_people = list(allocation.people)

        #convert people to ids, which start at 1
        person_to_id = {person: i+1 for i, person in enumerate(sorted_people)}

        self.people = tuple(person_to_id[p] for p in allocation.people)


        self.num_groups = allocation.num_groups
        self.group_sizes = tuple(sorted(allocation.group_sizes, key=lambda t: t[1], reverse=True))

        new_alloc: list[MyCanonicalRound] = []
        for round in allocation:
            tmp_round: list[MyCanonicalGroup] = []
            for group in round:
                new_group = MyCanonicalGroup(sorted(person_to_id[p] for p in group))
                self.group_to_canonical[group] = new_group
                tmp_round.append(new_group)
            new_round = MyCanonicalRound(tmp_round)
            self.round_to_canonical[round] = new_round
            new_alloc.append(new_round)
        # sort rounds
        self.rounds = tuple(sorted(new_alloc))
