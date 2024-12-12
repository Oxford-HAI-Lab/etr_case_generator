# Generated code - DO NOT EDIT
# Generated on: 2024-10-22 15:38:40

from pyetr import View
from pyetr.cases import BaseExample, ps
from typing import List

class GeneratedCase1(BaseExample):
    """
    Example 1

    P1 The bicycle is not parked , OR  The car is not moving , OR  The plane is taking off , OR  The train is not arriving , OR  The helicopter is landing.
    P2 The helicopter is landing , OR  The car is moving , OR  The plane is not taking off , OR  The bicycle is not parked.
    P3 The plane is not taking off , OR  The train is arriving.
    P4 The train is not arriving , OR  The plane is not taking off.
    C  The plane is not taking off.
    """

    v: tuple[View, ...] = (ps("(~Bicycle() ∨ ~Car() ∨ Plane() ∨ ~Train() ∨ Helicopter()) ∧ (Helicopter() ∨ Car() ∨ ~Plane() ∨ ~Bicycle()) ∧ (~Plane() ∨ Train()) ∧ (~Train() ∨ ~Plane())"),)
    c: View = ps("{~P()}")
    full_text: str = "(The bicycle is not parked OR The car is not moving OR The plane is taking off OR The train is not arriving OR The helicopter is landing) AND (The helicopter is landing OR The car is moving OR The plane is not taking off OR The bicycle is not parked) AND (The plane is not taking off OR The train is arriving) AND (The train is not arriving OR The plane is not taking off)"
    follows: List[str] = ['The plane is not taking off']

    # Difficulty information
    num_clauses: int = 4
    num_variables: int = 5
    variables: List[str] = ['B', 'C', 'H', 'P', 'T']
    num_follows: int = 1


class GeneratedCase2(BaseExample):
    """
    Example 2

    P1 The person is angry , OR  The person is not calm , OR  The person is surprised , OR  The person is happy , OR  The person is disgusted.
    P2 The person is not angry , OR  The person is not calm.
    P3 The person is angry , OR  The person is not calm.
    P4 The person is happy , OR  The person is surprised , OR  The person is not calm , OR  The person is angry , OR  The person is disgusted.
    C  The person is not calm.
    """

    v: tuple[View, ...] = (ps("(Angry() ∨ ~Calm() ∨ Surprised() ∨ Happy() ∨ Disgusted()) ∧ (~Angry() ∨ ~Calm()) ∧ (Angry() ∨ ~Calm()) ∧ (Happy() ∨ Surprised() ∨ ~Calm() ∨ Angry() ∨ Disgusted())"),)
    c: View = ps("{~C()}")
    full_text: str = "(The person is angry OR The person is not calm OR The person is surprised OR The person is happy OR The person is disgusted) AND (The person is not angry OR The person is not calm) AND (The person is angry OR The person is not calm) AND (The person is happy OR The person is surprised OR The person is not calm OR The person is angry OR The person is disgusted)"
    follows: List[str] = ['The person is not calm']

    # Difficulty information
    num_clauses: int = 4
    num_variables: int = 5
    variables: List[str] = ['A', 'C', 'D', 'H', 'S']
    num_follows: int = 1


class GeneratedCase3(BaseExample):
    """
    Example 3

    P1 The antelope is not grazing , OR  The dolphin is swimming.
    P2 The dolphin is swimming , OR  The bear is hibernating , OR  The fox is hunting.
    P3 The dolphin is not swimming , OR  The bear is not hibernating.
    P4 The antelope is grazing , OR  The bear is not hibernating.
    C  The bear is not hibernating.
    """

    v: tuple[View, ...] = (ps("(~Antelope() ∨ Dolphin()) ∧ (Dolphin() ∨ Bear() ∨ Fox()) ∧ (~Dolphin() ∨ ~Bear()) ∧ (Antelope() ∨ ~Bear())"),)
    c: View = ps("{~B()}")
    full_text: str = "(The antelope is not grazing OR The dolphin is swimming) AND (The dolphin is swimming OR The bear is hibernating OR The fox is hunting) AND (The dolphin is not swimming OR The bear is not hibernating) AND (The antelope is grazing OR The bear is not hibernating)"
    follows: List[str] = ['The bear is not hibernating']

    # Difficulty information
    num_clauses: int = 4
    num_variables: int = 4
    variables: List[str] = ['A', 'B', 'D', 'F']
    num_follows: int = 1


class GeneratedCase4(BaseExample):
    """
    Example 4

    P1 The giraffe is eating leaves , OR  The dolphin is swimming.
    P2 The giraffe is not eating leaves , OR  The antelope is grazing , OR  The cheetah is running , OR  The dolphin is not swimming , OR  The hippo is not submerged.
    P3 The hippo is not submerged , OR  The cheetah is not running , OR  The dolphin is not swimming , OR  The giraffe is eating leaves , OR  The antelope is not grazing.
    P4 The giraffe is not eating leaves , OR  The dolphin is swimming.
    C  The dolphin is swimming.
    """

    v: tuple[View, ...] = (ps("(Giraffe() ∨ Dolphin()) ∧ (~Giraffe() ∨ Antelope() ∨ Cheetah() ∨ ~Dolphin() ∨ ~Hippo()) ∧ (~Hippo() ∨ ~Cheetah() ∨ ~Dolphin() ∨ Giraffe() ∨ ~Antelope()) ∧ (~Giraffe() ∨ Dolphin())"),)
    c: View = ps("{D()}")
    full_text: str = "(The giraffe is eating leaves OR The dolphin is swimming) AND (The giraffe is not eating leaves OR The antelope is grazing OR The cheetah is running OR The dolphin is not swimming OR The hippo is not submerged) AND (The hippo is not submerged OR The cheetah is not running OR The dolphin is not swimming OR The giraffe is eating leaves OR The antelope is not grazing) AND (The giraffe is not eating leaves OR The dolphin is swimming)"
    follows: List[str] = ['The dolphin is swimming']

    # Difficulty information
    num_clauses: int = 4
    num_variables: int = 5
    variables: List[str] = ['A', 'C', 'D', 'G', 'H']
    num_follows: int = 1


class GeneratedCase5(BaseExample):
    """
    Example 5

    P1 The air is humid , OR  There is no thunder , OR  There are clouds in the sky , OR  The sun is shining , OR  There is fog.
    P2 The sun is not shining , OR  There is fog.
    P3 The sun is shining , OR  There is fog.
    P4 The air is humid , OR  The sun is shining , OR  There are clouds in the sky , OR  There is no fog.
    C  There is fog.
    """

    v: tuple[View, ...] = (ps("(Humidity() ∨ ~Thunder() ∨ Clouds() ∨ Sun() ∨ Fog()) ∧ (~Sun() ∨ Fog()) ∧ (Sun() ∨ Fog()) ∧ (Humidity() ∨ Sun() ∨ Clouds() ∨ ~Fog())"),)
    c: View = ps("{F()}")
    full_text: str = "(The air is humid OR There is no thunder OR There are clouds in the sky OR The sun is shining OR There is fog) AND (The sun is not shining OR There is fog) AND (The sun is shining OR There is fog) AND (The air is humid OR The sun is shining OR There are clouds in the sky OR There is no fog)"
    follows: List[str] = ['There is fog']

    # Difficulty information
    num_clauses: int = 4
    num_variables: int = 5
    variables: List[str] = ['C', 'F', 'H', 'S', 'T']
    num_follows: int = 1


class GeneratedCase6(BaseExample):
    """
    Example 6

    P1 The train is not arriving , OR  The helicopter is not landing.
    P2 The helicopter is landing , OR  The bus is on time.
    P3 The helicopter is landing , OR  The car is moving.
    P4 The train is arriving , OR  The car is moving , OR  The helicopter is not landing.
    C  The car is moving.
    """

    v: tuple[View, ...] = (ps("(~Train() ∨ ~Helicopter()) ∧ (Helicopter() ∨ Bus()) ∧ (Helicopter() ∨ Car()) ∧ (Train() ∨ Car() ∨ ~Helicopter())"),)
    c: View = ps("{C()}")
    full_text: str = "(The train is not arriving OR The helicopter is not landing) AND (The helicopter is landing OR The bus is on time) AND (The helicopter is landing OR The car is moving) AND (The train is arriving OR The car is moving OR The helicopter is not landing)"
    follows: List[str] = ['The car is moving']

    # Difficulty information
    num_clauses: int = 4
    num_variables: int = 4
    variables: List[str] = ['B', 'C', 'H', 'T']
    num_follows: int = 1


class GeneratedCase7(BaseExample):
    """
    Example 7

    P1 The person is sad , OR  The person is happy , OR  The person is fearful , OR  The person is not calm.
    P2 The person is fearful , OR  The person is not happy.
    P3 The person is fearful , OR  The person is not calm.
    P4 The person is not fearful , OR  The person is not calm.
    C  The person is not calm.
    """

    v: tuple[View, ...] = (ps("(Sad() ∨ Happy() ∨ Fearful() ∨ ~Calm()) ∧ (Fearful() ∨ ~Happy()) ∧ (Fearful() ∨ ~Calm()) ∧ (~Fearful() ∨ ~Calm())"),)
    c: View = ps("{~C()}")
    full_text: str = "(The person is sad OR The person is happy OR The person is fearful OR The person is not calm) AND (The person is fearful OR The person is not happy) AND (The person is fearful OR The person is not calm) AND (The person is not fearful OR The person is not calm)"
    follows: List[str] = ['The person is not calm']

    # Difficulty information
    num_clauses: int = 4
    num_variables: int = 4
    variables: List[str] = ['C', 'F', 'H', 'S']
    num_follows: int = 1


class GeneratedCase8(BaseExample):
    """
    Example 8

    P1 The person is not happy , OR  The person is not excited.
    P2 The person is not surprised , OR  The person is excited , OR  The person is fearful , OR  The person is not happy.
    P3 The person is not happy , OR  The person is not sad.
    P4 The person is sad , OR  The person is not happy.
    C  The person is not happy.
    """

    v: tuple[View, ...] = (ps("(~Happy() ∨ ~Excited()) ∧ (~Surprised() ∨ Excited() ∨ Fearful() ∨ ~Happy()) ∧ (~Happy() ∨ ~Sad()) ∧ (Sad() ∨ ~Happy())"),)
    c: View = ps("{~H()}")
    full_text: str = "(The person is not happy OR The person is not excited) AND (The person is not surprised OR The person is excited OR The person is fearful OR The person is not happy) AND (The person is not happy OR The person is not sad) AND (The person is sad OR The person is not happy)"
    follows: List[str] = ['The person is not happy']

    # Difficulty information
    num_clauses: int = 4
    num_variables: int = 4
    variables: List[str] = ['E', 'F', 'H', 'S']
    num_follows: int = 1


class GeneratedCase9(BaseExample):
    """
    Example 9

    P1 The hammer is being used , OR  The wrench is not tightening , OR  The screwdriver is turning , OR  The drill is not boring.
    P2 The wrench is tightening , OR  The screwdriver is turning.
    P3 The wrench is tightening , OR  The screwdriver is not turning.
    P4 The wrench is tightening , OR  The drill is boring , OR  The screwdriver is not turning , OR  The hammer is not being used.
    C  The wrench is tightening.
    """

    v: tuple[View, ...] = (ps("(Hammer() ∨ ~Wrench() ∨ Screwdriver() ∨ ~Drill()) ∧ (Wrench() ∨ Screwdriver()) ∧ (Wrench() ∨ ~Screwdriver()) ∧ (Wrench() ∨ Drill() ∨ ~Screwdriver() ∨ ~Hammer())"),)
    c: View = ps("{W()}")
    full_text: str = "(The hammer is being used OR The wrench is not tightening OR The screwdriver is turning OR The drill is not boring) AND (The wrench is tightening OR The screwdriver is turning) AND (The wrench is tightening OR The screwdriver is not turning) AND (The wrench is tightening OR The drill is boring OR The screwdriver is not turning OR The hammer is not being used)"
    follows: List[str] = ['The wrench is tightening']

    # Difficulty information
    num_clauses: int = 4
    num_variables: int = 4
    variables: List[str] = ['D', 'H', 'S', 'W']
    num_follows: int = 1


class GeneratedCase10(BaseExample):
    """
    Example 10

    P1 The hammer is being used , OR  The wrench is not tightening.
    P2 The screwdriver is not turning , OR  The wrench is not tightening.
    P3 The hammer is not being used , OR  The screwdriver is turning , OR  The wrench is not tightening.
    P4 The hammer is not being used , OR  The drill is boring , OR  The screwdriver is turning , OR  The wrench is not tightening.
    C  The wrench is not tightening.
    """

    v: tuple[View, ...] = (ps("(Hammer() ∨ ~Wrench()) ∧ (~Screwdriver() ∨ ~Wrench()) ∧ (~Hammer() ∨ Screwdriver() ∨ ~Wrench()) ∧ (~Hammer() ∨ Drill() ∨ Screwdriver() ∨ ~Wrench())"),)
    c: View = ps("{~W()}")
    full_text: str = "(The hammer is being used OR The wrench is not tightening) AND (The screwdriver is not turning OR The wrench is not tightening) AND (The hammer is not being used OR The screwdriver is turning OR The wrench is not tightening) AND (The hammer is not being used OR The drill is boring OR The screwdriver is turning OR The wrench is not tightening)"
    follows: List[str] = ['The wrench is not tightening']

    # Difficulty information
    num_clauses: int = 4
    num_variables: int = 4
    variables: List[str] = ['D', 'H', 'S', 'W']
    num_follows: int = 1


