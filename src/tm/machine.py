from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    write: str
    move: str
    next_state: str


@dataclass(frozen=True)
class TuringMachine:
    states: frozenset[str]
    input_alphabet: frozenset[str]
    tape_alphabet: frozenset[str]
    blank: str
    start: str
    finals: frozenset[str]
    rules: dict[tuple[str, str], Rule]  # (estado, símbolo lido) -> Rule
