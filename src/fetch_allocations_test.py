from unittest import TestCase
from pathlib import Path
import json
from fetch_allocations import Allocation, AllocationError

SCRIPT_DIR = Path(__file__).parent
RESOURCES = SCRIPT_DIR/"test_resources"


class Test(TestCase):

    # correct allocation
    def test_1(self):
        with open(RESOURCES/"1.json") as f:
            rounds = json.load(f)
        a = Allocation(rounds)
        self.assertEqual(a.num_people, 11)
        self.assertEqual(a.num_rounds, 5)
        self.assertEqual(a.num_groups, 5)
        self.assertListEqual(a.group_sizes, [(1,3), (4,2)])
    
    # a single person entry has been replaced with a nonexistent person
    def test_2(self):
        with open(RESOURCES/"2.json") as f:
            rounds = json.load(f)
        with self.assertRaises(AllocationError):
            Allocation(rounds)

    # a single person entry has been replaced with an existant and thus now duplicate person
    def test_3(self):
        with open(RESOURCES/"3.json") as f:
            rounds = json.load(f)
        with self.assertRaises(AllocationError):
            Allocation(rounds)

    # a person from one group is moved to an adjacent group of the same round
    def test_4(self):
        with open(RESOURCES/"4.json") as f:
            rounds = json.load(f)
        with self.assertRaises(AllocationError):
            Allocation(rounds)

    # in two rounds, a group swapped position with another group of the same round
    def test_5(self):
        with open(RESOURCES/"5.json") as f:
            rounds_5 = json.load(f)
        with open(RESOURCES/"1.json") as f:
            rounds_1 = json.load(f)
        self.assertNotEqual(rounds_5, rounds_1)
        a5 = Allocation(rounds_5)
        a1 = Allocation(rounds_1)
        self.assertEqual(a5._rounds, a1._rounds)
        self.assertEqual(a5._rounds, rounds_1)

    # the person order inside of three groups has been changed
    def test_6(self):
        with open(RESOURCES/"6.json") as f:
            rounds_6 = json.load(f)
        with open(RESOURCES/"1.json") as f:
            rounds_1 = json.load(f)
        self.assertNotEqual(rounds_6, rounds_1)
        a6 = Allocation(rounds_6)
        a1 = Allocation(rounds_1)
        self.assertEqual(a6._rounds, a1._rounds)
        self.assertEqual(a6._rounds, rounds_1)
    
    # in one round, two people from different groups were swapped
    def test_7(self):
        with open(RESOURCES/"7.json") as f:
            rounds = json.load(f)
        with self.assertRaises(AllocationError):
            Allocation(rounds)
