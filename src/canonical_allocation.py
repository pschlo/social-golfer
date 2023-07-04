from base_allocation import BaseAllocation
from allocation import Allocation


class CanonicalAllocation(BaseAllocation[int]):
    rounds: list[list[list[int]]]
    people: list[int]
    num_groups: int
    group_sizes: list[tuple[int,int]]

    def __init__(self, allocation: Allocation) -> None:
        #convert people to ids, which start at 1
        person_to_id = {person: i+1 for i, person in enumerate(allocation.people)}

        self.people = sorted(person_to_id[p] for p in allocation.people)
        self.num_groups = allocation.num_groups
        self.group_sizes = sorted(allocation.group_sizes, key=lambda t: t[1], reverse=True)

        self.rounds = []
        for round in allocation:
            new_round: list[list[int]] = []
            for group in round:
                # sort people
                new_round.append(sorted(person_to_id[p] for p in group))
            # sort groups
            new_round.sort()
            new_round.sort(key=len, reverse=True)
            self.rounds.append(new_round)

        # sort rounds
        self.rounds.sort()
