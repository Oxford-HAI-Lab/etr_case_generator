# Generated code - DO NOT EDIT
# Generated on: 2024-10-22 15:38:40

from pyetr import View
from pyetr.cases import BaseExample, ps
from typing import List

class GeneratedCase1(BaseExample):
    """
    Example 1

    P1 The bus is on time , OR  The motorcycle is not starting.
    P2 The bus is not on time , OR  The motorcycle is not starting.
    C  The motorcycle is not starting.
    """

    v: tuple[View, ...] = (ps("(Bus() ∨ ~Motorcycle()) ∧ (~Bus() ∨ ~Motorcycle())"),)
    c: View = ps("{~M()}")
    full_text: str = "(The bus is on time OR The motorcycle is not starting) AND (The bus is not on time OR The motorcycle is not starting)"
    follows: List[str] = ['The motorcycle is not starting']

    # Difficulty information
    num_clauses: int = 2
    num_variables: int = 2
    variables: List[str] = ['B', 'M']
    num_follows: int = 1


class GeneratedCase2(BaseExample):
    """
    Example 2

    P1 The saw is cutting , OR  The wrench is tightening.
    P2 The saw is cutting , OR  The wrench is not tightening.
    C  The saw is cutting.
    """

    v: tuple[View, ...] = (ps("(Saw() ∨ Wrench()) ∧ (Saw() ∨ ~Wrench())"),)
    c: View = ps("{S()}")
    full_text: str = "(The saw is cutting OR The wrench is tightening) AND (The saw is cutting OR The wrench is not tightening)"
    follows: List[str] = ['The saw is cutting']

    # Difficulty information
    num_clauses: int = 2
    num_variables: int = 2
    variables: List[str] = ['S', 'W']
    num_follows: int = 1


class GeneratedCase3(BaseExample):
    """
    Example 3

    P1 The saw is not cutting , OR  The drill is not boring.
    P2 The screwdriver is not turning , OR  The drill is boring.
    C  The saw is not cutting.
    """

    v: tuple[View, ...] = (ps("(~Saw() ∨ ~Drill()) ∧ (~Screwdriver() ∨ Drill())"),)
    c: View = ps("{~S()}")
    full_text: str = "(The saw is not cutting OR The drill is not boring) AND (The screwdriver is not turning OR The drill is boring)"
    follows: List[str] = ['The saw is not cutting']

    # Difficulty information
    num_clauses: int = 2
    num_variables: int = 2
    variables: List[str] = ['D', 'S']
    num_follows: int = 1


class GeneratedCase4(BaseExample):
    """
    Example 4

    P1 The bus is not on time , OR  The ship is docking.
    P2 The ship is docking , OR  The bus is on time.
    C  The ship is docking.
    """

    v: tuple[View, ...] = (ps("(~Bus() ∨ Ship()) ∧ (Ship() ∨ Bus())"),)
    c: View = ps("{S()}")
    full_text: str = "(The bus is not on time OR The ship is docking) AND (The ship is docking OR The bus is on time)"
    follows: List[str] = ['The ship is docking']

    # Difficulty information
    num_clauses: int = 2
    num_variables: int = 2
    variables: List[str] = ['B', 'S']
    num_follows: int = 1


class GeneratedCase5(BaseExample):
    """
    Example 5

    P1 The helicopter is not landing , OR  The train is not arriving.
    P2 The helicopter is not landing , OR  The train is arriving.
    C  The helicopter is not landing.
    """

    v: tuple[View, ...] = (ps("(~Helicopter() ∨ ~Train()) ∧ (~Helicopter() ∨ Train())"),)
    c: View = ps("{~H()}")
    full_text: str = "(The helicopter is not landing OR The train is not arriving) AND (The helicopter is not landing OR The train is arriving)"
    follows: List[str] = ['The helicopter is not landing']

    # Difficulty information
    num_clauses: int = 2
    num_variables: int = 2
    variables: List[str] = ['H', 'T']
    num_follows: int = 1


class GeneratedCase6(BaseExample):
    """
    Example 6

    P1 The person is not sad , OR  The person is not excited.
    P2 The person is not surprised , OR  The person is excited.
    C  The person is not sad.
    """

    v: tuple[View, ...] = (ps("(~Sad() ∨ ~Excited()) ∧ (~Surprised() ∨ Excited())"),)
    c: View = ps("{~S()}")
    full_text: str = "(The person is not sad OR The person is not excited) AND (The person is not surprised OR The person is excited)"
    follows: List[str] = ['The person is not sad']

    # Difficulty information
    num_clauses: int = 2
    num_variables: int = 2
    variables: List[str] = ['E', 'S']
    num_follows: int = 1


class GeneratedCase7(BaseExample):
    """
    Example 7

    P1 The plane is not taking off , OR  The ship is not docking.
    P2 The ship is docking , OR  The plane is not taking off.
    C  The plane is not taking off.
    """

    v: tuple[View, ...] = (ps("(~Plane() ∨ ~Ship()) ∧ (Ship() ∨ ~Plane())"),)
    c: View = ps("{~P()}")
    full_text: str = "(The plane is not taking off OR The ship is not docking) AND (The ship is docking OR The plane is not taking off)"
    follows: List[str] = ['The plane is not taking off']

    # Difficulty information
    num_clauses: int = 2
    num_variables: int = 2
    variables: List[str] = ['P', 'S']
    num_follows: int = 1


class GeneratedCase8(BaseExample):
    """
    Example 8

    P1 There is no lightning , OR  There are no clouds in the sky.
    P2 There are clouds in the sky , OR  There is no lightning.
    C  There is no lightning.
    """

    v: tuple[View, ...] = (ps("(~Lightning() ∨ ~Clouds()) ∧ (Clouds() ∨ ~Lightning())"),)
    c: View = ps("{~L()}")
    full_text: str = "(There is no lightning OR There are no clouds in the sky) AND (There are clouds in the sky OR There is no lightning)"
    follows: List[str] = ['There is no lightning']

    # Difficulty information
    num_clauses: int = 2
    num_variables: int = 2
    variables: List[str] = ['C', 'L']
    num_follows: int = 1


class GeneratedCase9(BaseExample):
    """
    Example 9

    P1 The hippo is submerged , OR  The bear is hibernating.
    P2 The hippo is submerged , OR  The bear is not hibernating.
    C  The hippo is submerged.
    """

    v: tuple[View, ...] = (ps("(Hippo() ∨ Bear()) ∧ (Hippo() ∨ ~Bear())"),)
    c: View = ps("{H()}")
    full_text: str = "(The hippo is submerged OR The bear is hibernating) AND (The hippo is submerged OR The bear is not hibernating)"
    follows: List[str] = ['The hippo is submerged']

    # Difficulty information
    num_clauses: int = 2
    num_variables: int = 2
    variables: List[str] = ['B', 'H']
    num_follows: int = 1


class GeneratedCase10(BaseExample):
    """
    Example 10

    P1 The person is surprised , OR  The person is not fearful.
    P2 The person is surprised , OR  The person is fearful.
    C  The person is surprised.
    """

    v: tuple[View, ...] = (ps("(Surprised() ∨ ~Fearful()) ∧ (Surprised() ∨ Fearful())"),)
    c: View = ps("{S()}")
    full_text: str = "(The person is surprised OR The person is not fearful) AND (The person is surprised OR The person is fearful)"
    follows: List[str] = ['The person is surprised']

    # Difficulty information
    num_clauses: int = 2
    num_variables: int = 2
    variables: List[str] = ['F', 'S']
    num_follows: int = 1


