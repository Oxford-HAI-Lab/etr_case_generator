# Generated code - DO NOT EDIT
# Generated on: 2024-10-22 15:38:42

from pyetr import View
from pyetr.cases import BaseExample, ps
from typing import List

class GeneratedCase1(BaseExample):
    """
    Example 1

    P1 The person is not surprised , OR  The person is angry.
    P2 The person is not excited , OR  The person is not sad , OR  The person is not disgusted , OR  The person is calm , OR  The person is not angry.
    P3 The person is happy , OR  The person is angry , OR  The person is sad.
    P4 The person is not sad , OR  The person is not fearful , OR  The person is not disgusted , OR  The person is calm.
    P5 The person is not angry , OR  The person is not surprised.
    C  The person is not surprised.
    """

    v: tuple[View, ...] = (ps("(~Surprised() ∨ Angry()) ∧ (~Excited() ∨ ~Sad() ∨ ~Disgusted() ∨ Calm() ∨ ~Angry()) ∧ (Happy() ∨ Angry() ∨ Sad()) ∧ (~Sad() ∨ ~Fearful() ∨ ~Disgusted() ∨ Calm()) ∧ (~Angry() ∨ ~Surprised())"),)
    c: View = ps("{~S()}")
    full_text: str = "(The person is not surprised OR The person is angry) AND (The person is not excited OR The person is not sad OR The person is not disgusted OR The person is calm OR The person is not angry) AND (The person is happy OR The person is angry OR The person is sad) AND (The person is not sad OR The person is not fearful OR The person is not disgusted OR The person is calm) AND (The person is not angry OR The person is not surprised)"
    follows: List[str] = ['The person is not surprised']

    # Difficulty information
    num_clauses: int = 5
    num_variables: int = 7
    variables: List[str] = ['A', 'C', 'D', 'E', 'F', 'H', 'S']
    num_follows: int = 1


class GeneratedCase2(BaseExample):
    """
    Example 2

    P1 The hammer is not being used , OR  The level is balancing.
    P2 The level is balancing , OR  The hammer is being used , OR  The drill is not boring , OR  The pliers are not gripping.
    P3 The level is not balancing , OR  The hammer is not being used.
    P4 The wrench is tightening , OR  The pliers are gripping.
    P5 The hammer is not being used , OR  The level is balancing.
    C  The hammer is not being used.
    """

    v: tuple[View, ...] = (ps("(~Hammer() ∨ Level()) ∧ (Level() ∨ Hammer() ∨ ~Drill() ∨ ~Pliers()) ∧ (~Level() ∨ ~Hammer()) ∧ (Wrench() ∨ Pliers()) ∧ (~Hammer() ∨ Level())"),)
    c: View = ps("{~H()}")
    full_text: str = "(The hammer is not being used OR The level is balancing) AND (The level is balancing OR The hammer is being used OR The drill is not boring OR The pliers are not gripping) AND (The level is not balancing OR The hammer is not being used) AND (The wrench is tightening OR The pliers are gripping) AND (The hammer is not being used OR The level is balancing)"
    follows: List[str] = ['The hammer is not being used']

    # Difficulty information
    num_clauses: int = 5
    num_variables: int = 5
    variables: List[str] = ['D', 'H', 'L', 'P', 'W']
    num_follows: int = 1


class GeneratedCase3(BaseExample):
    """
    Example 3

    P1 The giraffe is not eating leaves , OR  The elephant is not trumpeting , OR  The dolphin is not swimming.
    P2 The giraffe is eating leaves , OR  The dolphin is swimming , OR  The cheetah is running , OR  The antelope is grazing , OR  The bear is not hibernating , OR  The hippo is submerged.
    P3 The bear is hibernating , OR  The dolphin is not swimming , OR  The antelope is not grazing , OR  The cheetah is not running , OR  The elephant is not trumpeting.
    P4 The dolphin is swimming , OR  The antelope is grazing.
    P5 The antelope is grazing , OR  The dolphin is not swimming.
    C  The antelope is grazing.
    """

    v: tuple[View, ...] = (ps("(~Giraffe() ∨ ~Elephant() ∨ ~Dolphin()) ∧ (Giraffe() ∨ Dolphin() ∨ Cheetah() ∨ Antelope() ∨ ~Bear() ∨ Hippo()) ∧ (Bear() ∨ ~Dolphin() ∨ ~Antelope() ∨ ~Cheetah() ∨ ~Elephant()) ∧ (Dolphin() ∨ Antelope()) ∧ (Antelope() ∨ ~Dolphin())"),)
    c: View = ps("{A()}")
    full_text: str = "(The giraffe is not eating leaves OR The elephant is not trumpeting OR The dolphin is not swimming) AND (The giraffe is eating leaves OR The dolphin is swimming OR The cheetah is running OR The antelope is grazing OR The bear is not hibernating OR The hippo is submerged) AND (The bear is hibernating OR The dolphin is not swimming OR The antelope is not grazing OR The cheetah is not running OR The elephant is not trumpeting) AND (The dolphin is swimming OR The antelope is grazing) AND (The antelope is grazing OR The dolphin is not swimming)"
    follows: List[str] = ['The antelope is grazing']

    # Difficulty information
    num_clauses: int = 5
    num_variables: int = 7
    variables: List[str] = ['A', 'B', 'C', 'D', 'E', 'G', 'H']
    num_follows: int = 1


class GeneratedCase4(BaseExample):
    """
    Example 4

    P1 The fox is hunting , OR  The antelope is grazing , OR  The elephant is not trumpeting , OR  The cheetah is running , OR  The hippo is not submerged , OR  The dolphin is not swimming.
    P2 The elephant is not trumpeting , OR  The hippo is submerged.
    P3 The dolphin is not swimming , OR  The cheetah is running , OR  The fox is not hunting , OR  The giraffe is not eating leaves , OR  The antelope is not grazing.
    P4 The elephant is not trumpeting , OR  The hippo is not submerged.
    P5 The bear is not hibernating , OR  The hippo is not submerged , OR  The cheetah is running , OR  The giraffe is eating leaves , OR  The dolphin is not swimming , OR  The elephant is not trumpeting.
    C  The elephant is not trumpeting.
    """

    v: tuple[View, ...] = (ps("(Fox() ∨ Antelope() ∨ ~Elephant() ∨ Cheetah() ∨ ~Hippo() ∨ ~Dolphin()) ∧ (~Elephant() ∨ Hippo()) ∧ (~Dolphin() ∨ Cheetah() ∨ ~Fox() ∨ ~Giraffe() ∨ ~Antelope()) ∧ (~Elephant() ∨ ~Hippo()) ∧ (~Bear() ∨ ~Hippo() ∨ Cheetah() ∨ Giraffe() ∨ ~Dolphin() ∨ ~Elephant())"),)
    c: View = ps("{~E()}")
    full_text: str = "(The fox is hunting OR The antelope is grazing OR The elephant is not trumpeting OR The cheetah is running OR The hippo is not submerged OR The dolphin is not swimming) AND (The elephant is not trumpeting OR The hippo is submerged) AND (The dolphin is not swimming OR The cheetah is running OR The fox is not hunting OR The giraffe is not eating leaves OR The antelope is not grazing) AND (The elephant is not trumpeting OR The hippo is not submerged) AND (The bear is not hibernating OR The hippo is not submerged OR The cheetah is running OR The giraffe is eating leaves OR The dolphin is not swimming OR The elephant is not trumpeting)"
    follows: List[str] = ['The elephant is not trumpeting']

    # Difficulty information
    num_clauses: int = 5
    num_variables: int = 8
    variables: List[str] = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    num_follows: int = 1


class GeneratedCase5(BaseExample):
    """
    Example 5

    P1 The bus is on time , OR  The car is moving.
    P2 The train is arriving , OR  The motorcycle is not starting , OR  The ship is docking.
    P3 The train is not arriving , OR  The bicycle is not parked , OR  The plane is not taking off , OR  The motorcycle is starting , OR  The helicopter is landing , OR  The car is not moving.
    P4 The bus is not on time , OR  The helicopter is landing.
    P5 The bicycle is not parked , OR  The car is moving.
    C  The car is moving.
    """

    v: tuple[View, ...] = (ps("(Bus() ∨ Car()) ∧ (Train() ∨ ~Motorcycle() ∨ Ship()) ∧ (~Train() ∨ ~Bicycle() ∨ ~Plane() ∨ Motorcycle() ∨ Helicopter() ∨ ~Car()) ∧ (~Bus() ∨ Helicopter()) ∧ (~Bicycle() ∨ Car())"),)
    c: View = ps("{C()}")
    full_text: str = "(The bus is on time OR The car is moving) AND (The train is arriving OR The motorcycle is not starting OR The ship is docking) AND (The train is not arriving OR The bicycle is not parked OR The plane is not taking off OR The motorcycle is starting OR The helicopter is landing OR The car is not moving) AND (The bus is not on time OR The helicopter is landing) AND (The bicycle is not parked OR The car is moving)"
    follows: List[str] = ['The car is moving']

    # Difficulty information
    num_clauses: int = 5
    num_variables: int = 7
    variables: List[str] = ['B', 'C', 'H', 'M', 'P', 'S', 'T']
    num_follows: int = 1


