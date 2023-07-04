import requests
from collections import Counter
from tabulate import tabulate
from itertools import chain
import json
import time
from pathlib import Path
# from collections.abc import Sequence
from typing import Any, TypeVar

SCRIPT_DIR = Path(__file__).parent

BASE_URL = "https://breakoutroom.pythonanywhere.com/allocate/download/"

MARKDOWN_DIR = SCRIPT_DIR/"markdown"
JSON_DIR = SCRIPT_DIR/"json"


def main():
    MARKDOWN_DIR.mkdir(exist_ok=True)
    JSON_DIR.mkdir(exist_ok=True)

    for id in range(1,1000):
        print(f'ID {id}: processing allocation')
        try:
            a = get_allocation(id)
        except InvalidIdError:
            print(f'ID {id}: Failed, stopping')
            break
        print(f'ID {id}: Success: {a.title}')

        # write markdown
        with open(MARKDOWN_DIR / f'{a.title}.md', 'w') as f:
            f.write(a.to_markdown())
        
        # write json
        title = f'{a.num_people}@{a.num_rounds}_'
        title += '_'.join(f"{num}x{size}" for num, size in a.group_sizes)
        with open(JSON_DIR / f'{title}.json', 'w') as f:
            f.write(json.dumps(a.rounds))

        time.sleep(0.5)


class AllocationError(ValueError):
    pass


class Group(list[int]):
    def __init__(self, people: set[int]):
        super().__init__(people)
        
        # check that no duplicate people
        assert len(set(people)) == len(people)

        # sort people from smallest to largest
        self.sort()


class Round(list[Group]):
    def __init__(self, people: set[Any], groups: set[Group]):
        super().__init__(groups)
        self.people = people
        self.num_people = len(people)

        # sort groups from largest to smallest
        self.sort(key=len, reverse=True)

        # group sizes are sorted from largest to smallest
        group_sizes = Counter(sorted(map(len, self), reverse=True)).items()
        self.group_sizes = [(num, size) for size, num in group_sizes]
        
        # check that each person appears exactly once
        if not Counter(chain(*self)) == Counter(people):
            return False



class Allocation(list[Round]):
    num_people: int
    num_groups: int
    group_sizes: list[tuple[int,int]]

    def __init__(self, rounds: list[Round]):
        super().__init__(rounds)
        self.num_people = self[0].num_people


        # check that all rounds have the same group sizes
        if not all(round.group_sizes == self[0].group_sizes for round in self):
            return False

        # check if actual solution, i.e. that noone is in a group with another person more than once
        seen: dict[int, set[int]] = {p: set() for p in range(1, self.num_people+1)}
        for round in self:
            for group in round:
                group = set(group)
                for person in group:
                    others = group - {person}
                    # check intersection
                    if seen[person] & others:
                        return False
                    seen[person].update(others)


        # convert person symbols to person numbers, which start at 1
        symbols = sorted({x for round in rounds for group in round for x in group})
        self.num_people = len(symbols)
        symbol_to_person = {symbol: i+1 for i, symbol in enumerate(symbols)}

        # in each round, sort groups from largest to smallest
        # in each group, sort person from smallest to largest
        # round[i] = sorted([symbol_to_person[symbol] for symbol in round[i]])


        # set title
        groups_str = ', '.join(f"{num} groups of {size}" for num, size in self.group_sizes)
        self.title = f'{self.num_people} people over {self.num_rounds} rounds ({groups_str})'

        # check validity
        if not is_valid(self):
            raise AllocationError("Invalid allocation")
    
    def to_markdown(self) -> str:
        headers = ['Round'] + [f'Group {i+1}' for i in range(self.num_groups)]
        data = []
        for i, groups in enumerate(self.rounds):
            row = [str(i+1)]
            row += [', '.join(map(str,group)) for group in groups]
            data.append(row)
        return tabulate(data, headers, tablefmt="pipe")


# checks if an allocation is valid
def is_valid(allocation: Allocation) -> bool:
    a = allocation

    print("here0")
    
    
    print("here1")

    
    print("here2")

    
    return True


class InvalidIdError(ValueError):
    pass


def get_allocation(id:int) -> Allocation:
    url = BASE_URL + str(id)
    response = requests.get(url, stream=True)
    response.raise_for_status()
    if response.content.decode("utf-8") == "Unknown matching ID.":
        raise InvalidIdError()
    else:
        allocation_str = response.content.decode("utf-8")
        rounds: list[list[list[int]]] = json.loads(allocation_str)
        return Allocation(rounds)
        




if __name__ == "__main__":
    main()