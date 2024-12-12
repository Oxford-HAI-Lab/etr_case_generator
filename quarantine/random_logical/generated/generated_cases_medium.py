# Generated code - DO NOT EDIT
# Generated on: 2024-10-22 15:38:40

from pyetr import View
from pyetr.cases import BaseExample, ps
from typing import List

class GeneratedCase1(BaseExample):
    """
    Example 1

    P1 The person is sad , OR  The person is not angry.
    P2 The person is fearful , OR  The person is angry.
    P3 The person is sad , OR  The person is angry.
    C  The person is sad.
    """

    v: tuple[View, ...] = (ps("(Sad() ∨ ~Angry()) ∧ (Fearful() ∨ Angry()) ∧ (Sad() ∨ Angry())"),)
    c: View = ps("{S()}")
    full_text: str = "(The person is sad OR The person is not angry) AND (The person is fearful OR The person is angry) AND (The person is sad OR The person is angry)"
    follows: List[str] = ['The person is sad']

    # Difficulty information
    num_clauses: int = 3
    num_variables: int = 3
    variables: List[str] = ['A', 'F', 'S']
    num_follows: int = 1


class GeneratedCase2(BaseExample):
    """
    Example 2

    P1 The plane is taking off , OR  The bus is on time.
    P2 The bus is on time , OR  The plane is taking off , OR  The car is moving.
    P3 The plane is taking off , OR  The bus is not on time.
    C  The plane is taking off.
    """

    v: tuple[View, ...] = (ps("(Plane() ∨ Bus()) ∧ (Bus() ∨ Plane() ∨ Car()) ∧ (Plane() ∨ ~Bus())"),)
    c: View = ps("{P()}")
    full_text: str = "(The plane is taking off OR The bus is on time) AND (The bus is on time OR The plane is taking off OR The car is moving) AND (The plane is taking off OR The bus is not on time)"
    follows: List[str] = ['The plane is taking off']

    # Difficulty information
    num_clauses: int = 3
    num_variables: int = 3
    variables: List[str] = ['B', 'C', 'P']
    num_follows: int = 1


class GeneratedCase3(BaseExample):
    """
    Example 3

    P1 The helicopter is not landing , OR  The motorcycle is starting.
    P2 The car is moving , OR  The bus is not on time , OR  The motorcycle is not starting.
    P3 The motorcycle is starting , OR  The helicopter is landing.
    C  The motorcycle is starting.
    """

    v: tuple[View, ...] = (ps("(~Helicopter() ∨ Motorcycle()) ∧ (Car() ∨ ~Bus() ∨ ~Motorcycle()) ∧ (Motorcycle() ∨ Helicopter())"),)
    c: View = ps("{M()}")
    full_text: str = "(The helicopter is not landing OR The motorcycle is starting) AND (The car is moving OR The bus is not on time OR The motorcycle is not starting) AND (The motorcycle is starting OR The helicopter is landing)"
    follows: List[str] = ['The motorcycle is starting']

    # Difficulty information
    num_clauses: int = 3
    num_variables: int = 4
    variables: List[str] = ['B', 'C', 'H', 'M']
    num_follows: int = 1


class GeneratedCase4(BaseExample):
    """
    Example 4

    P1 The helicopter is not landing , OR  The car is moving.
    P2 The helicopter is landing , OR  The plane is not taking off , OR  The car is not moving.
    P3 The helicopter is not landing , OR  The car is not moving.
    C  The helicopter is not landing.
    """

    v: tuple[View, ...] = (ps("(~Helicopter() ∨ Car()) ∧ (Helicopter() ∨ ~Plane() ∨ ~Car()) ∧ (~Helicopter() ∨ ~Car())"),)
    c: View = ps("{~H()}")
    full_text: str = "(The helicopter is not landing OR The car is moving) AND (The helicopter is landing OR The plane is not taking off OR The car is not moving) AND (The helicopter is not landing OR The car is not moving)"
    follows: List[str] = ['The helicopter is not landing']

    # Difficulty information
    num_clauses: int = 3
    num_variables: int = 3
    variables: List[str] = ['C', 'H', 'P']
    num_follows: int = 1


class GeneratedCase5(BaseExample):
    """
    Example 5

    P1 The cheetah is not running , OR  The antelope is not grazing , OR  The bear is not hibernating.
    P2 The bear is not hibernating , OR  The dolphin is swimming.
    P3 The bear is not hibernating , OR  The dolphin is not swimming.
    C  The bear is not hibernating.
    """

    v: tuple[View, ...] = (ps("(~Cheetah() ∨ ~Antelope() ∨ ~Bear()) ∧ (~Bear() ∨ Dolphin()) ∧ (~Bear() ∨ ~Dolphin())"),)
    c: View = ps("{~B()}")
    full_text: str = "(The cheetah is not running OR The antelope is not grazing OR The bear is not hibernating) AND (The bear is not hibernating OR The dolphin is swimming) AND (The bear is not hibernating OR The dolphin is not swimming)"
    follows: List[str] = ['The bear is not hibernating']

    # Difficulty information
    num_clauses: int = 3
    num_variables: int = 4
    variables: List[str] = ['A', 'B', 'C', 'D']
    num_follows: int = 1


class GeneratedCase6(BaseExample):
    """
    Example 6

    P1 The person is sad , OR  The person is not calm.
    P2 The person is sad , OR  The person is not disgusted , OR  The person is calm.
    P3 The person is not sad , OR  The person is not calm.
    C  The person is not calm.
    """

    v: tuple[View, ...] = (ps("(Sad() ∨ ~Calm()) ∧ (Sad() ∨ ~Disgusted() ∨ Calm()) ∧ (~Sad() ∨ ~Calm())"),)
    c: View = ps("{~C()}")
    full_text: str = "(The person is sad OR The person is not calm) AND (The person is sad OR The person is not disgusted OR The person is calm) AND (The person is not sad OR The person is not calm)"
    follows: List[str] = ['The person is not calm']

    # Difficulty information
    num_clauses: int = 3
    num_variables: int = 3
    variables: List[str] = ['C', 'D', 'S']
    num_follows: int = 1


class GeneratedCase7(BaseExample):
    """
    Example 7

    P1 The tape measure is extending , OR  The wrench is not tightening , OR  The level is balancing.
    P2 The level is balancing , OR  The drill is boring.
    P3 The drill is boring , OR  The level is not balancing.
    C  The drill is boring.
    """

    v: tuple[View, ...] = (ps("(Tape_measure() ∨ ~Wrench() ∨ Level()) ∧ (Level() ∨ Drill()) ∧ (Drill() ∨ ~Level())"),)
    c: View = ps("{D()}")
    full_text: str = "(The tape measure is extending OR The wrench is not tightening OR The level is balancing) AND (The level is balancing OR The drill is boring) AND (The drill is boring OR The level is not balancing)"
    follows: List[str] = ['The drill is boring']

    # Difficulty information
    num_clauses: int = 3
    num_variables: int = 4
    variables: List[str] = ['D', 'L', 'T', 'W']
    num_follows: int = 1


class GeneratedCase8(BaseExample):
    """
    Example 8

    P1 The hammer is being used , OR  The wrench is not tightening , OR  The pliers are gripping.
    P2 The saw is not cutting , OR  The hammer is being used.
    P3 The saw is not cutting , OR  The hammer is not being used.
    C  The saw is not cutting.
    """

    v: tuple[View, ...] = (ps("(Hammer() ∨ ~Wrench() ∨ Pliers()) ∧ (~Saw() ∨ Hammer()) ∧ (~Saw() ∨ ~Hammer())"),)
    c: View = ps("{~S()}")
    full_text: str = "(The hammer is being used OR The wrench is not tightening OR The pliers are gripping) AND (The saw is not cutting OR The hammer is being used) AND (The saw is not cutting OR The hammer is not being used)"
    follows: List[str] = ['The saw is not cutting']

    # Difficulty information
    num_clauses: int = 3
    num_variables: int = 4
    variables: List[str] = ['H', 'P', 'S', 'W']
    num_follows: int = 1


class GeneratedCase9(BaseExample):
    """
    Example 9

    P1 The ship is not docking , OR  The bicycle is not parked.
    P2 The motorcycle is not starting , OR  The bicycle is parked.
    P3 The bicycle is parked , OR  The ship is not docking , OR  The motorcycle is starting.
    C  The ship is not docking.
    """

    v: tuple[View, ...] = (ps("(~Ship() ∨ ~Bicycle()) ∧ (~Motorcycle() ∨ Bicycle()) ∧ (Bicycle() ∨ ~Ship() ∨ Motorcycle())"),)
    c: View = ps("{~S()}")
    full_text: str = "(The ship is not docking OR The bicycle is not parked) AND (The motorcycle is not starting OR The bicycle is parked) AND (The bicycle is parked OR The ship is not docking OR The motorcycle is starting)"
    follows: List[str] = ['The ship is not docking']

    # Difficulty information
    num_clauses: int = 3
    num_variables: int = 3
    variables: List[str] = ['B', 'M', 'S']
    num_follows: int = 1


class GeneratedCase10(BaseExample):
    """
    Example 10

    P1 The person is not disgusted , OR  The person is not calm , OR  The person is not excited.
    P2 The person is not calm , OR  The person is not fearful.
    P3 The person is calm , OR  The person is not fearful.
    C  The person is not fearful.
    """

    v: tuple[View, ...] = (ps("(~Disgusted() ∨ ~Calm() ∨ ~Excited()) ∧ (~Calm() ∨ ~Fearful()) ∧ (Calm() ∨ ~Fearful())"),)
    c: View = ps("{~F()}")
    full_text: str = "(The person is not disgusted OR The person is not calm OR The person is not excited) AND (The person is not calm OR The person is not fearful) AND (The person is calm OR The person is not fearful)"
    follows: List[str] = ['The person is not fearful']

    # Difficulty information
    num_clauses: int = 3
    num_variables: int = 4
    variables: List[str] = ['C', 'D', 'E', 'F']
    num_follows: int = 1


