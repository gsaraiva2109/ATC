from dataclasses import dataclass
from enum import Enum
from typing import Iterator

from .errors import InputError
from .machine import TuringMachine
from .tape import Tape

DEFAULT_MAX_STEPS = 100_000


class Status(Enum):
    ACCEPTED = "ACEITA"
    REJECTED = "REJEITADA"
    LIMIT_EXCEEDED = "LIMITE DE PASSOS EXCEDIDO"


@dataclass(frozen=True)
class Snapshot:
    step: int
    state: str
    tape: str  # trecho visitado da fita
    head: int  # índice do cabeçote dentro de `tape`


@dataclass(frozen=True)
class Result:
    status: Status
    steps: int
    state: str
    tape: str  # conteúdo final da fita, sem brancos nas pontas
    reason: str


class Execution:
    """Execução de uma MT. Iterar produz um `Snapshot` por configuração
    (inclusive a inicial); ao fim da iteração `result` está disponível."""

    def __init__(self, machine: TuringMachine, word: str, max_steps: int = DEFAULT_MAX_STEPS):
        if not word:
            raise InputError("a palavra de entrada não pode ser vazia")
        invalid = sorted({s for s in word if s not in machine.input_alphabet})
        if invalid:
            raise InputError(
                f"símbolos fora do alfabeto de entrada: {', '.join(repr(s) for s in invalid)}"
            )
        if max_steps < 0:
            raise ValueError("max_steps não pode ser negativo")
        self.machine = machine
        self.max_steps = max_steps
        self.tape = Tape(machine.blank)
        self.tape.load(word)
        self.state = machine.start
        self.steps = 0
        self.result: Result | None = None

    def _snapshot(self) -> Snapshot:
        text, head = self.tape.window()
        return Snapshot(self.steps, self.state, text, head)

    def _finish(self, status: Status, reason: str) -> None:
        self.result = Result(status, self.steps, self.state, self.tape.content(), reason)

    def __iter__(self) -> Iterator[Snapshot]:
        machine = self.machine
        while True:
            yield self._snapshot()
            if self.state in machine.finals:
                self._finish(Status.ACCEPTED, f"parou no estado final {self.state}")
                return
            if self.steps >= self.max_steps:
                self._finish(
                    Status.LIMIT_EXCEEDED,
                    f"limite de {self.max_steps} passos atingido (possível loop infinito)",
                )
                return
            symbol = self.tape.read()
            rule = machine.rules.get((self.state, symbol))
            if rule is None:
                self._finish(
                    Status.REJECTED,
                    f"sem transição para ({self.state}, {symbol}) em estado não final",
                )
                return
            self.tape.write(rule.write)
            self.tape.move(rule.move)
            self.state = rule.next_state
            self.steps += 1


def run(machine: TuringMachine, word: str, max_steps: int = DEFAULT_MAX_STEPS) -> Result:
    """Executa até o fim e devolve só o `Result` (sem trace)."""
    execution = Execution(machine, word, max_steps)
    for _ in execution:
        pass
    assert execution.result is not None
    return execution.result
