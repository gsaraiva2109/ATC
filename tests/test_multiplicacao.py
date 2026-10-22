import json
from pathlib import Path

import pytest

from tm import Execution, Status, load_machine


ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / "tests/cases/multiplicacao.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def machine():
    return load_machine(ROOT / "machines/multiplicacao.txt")


@pytest.mark.parametrize("case", CASES, ids=lambda case: repr(case["entrada"]))
def test_multiplicacao_cases(machine, case):
    execution = Execution(machine, case["entrada"])
    for _ in execution:
        pass
    result = execution.result
    assert result is not None
    expected_status = Status.ACCEPTED if case["aceita"] else Status.REJECTED
    assert result.status is expected_status
    assert result.steps < 100_000
    if case["aceita"]:
        assert result.state in machine.finals
        assert result.tape == case["resultado_esperado"]
        assert len(execution.tape) == len(case["resultado_esperado"])
        assert execution.tape.read() == "1"
        assert execution.tape.head == len(case["entrada"]) + 1
    else:
        assert result.state not in machine.finals


@pytest.mark.parametrize("word", ["", "111", "1**1", "*11", "11*"])
def test_invalid_format_stops_without_a_rule(machine, word):
    execution = Execution(machine, word)
    for _ in execution:
        pass
    assert execution.result.status is Status.REJECTED
    assert (execution.state, execution.tape.read()) not in machine.rules
    assert "sem transição" in execution.result.reason


def test_invalid_alphabet_is_rejected_before_transitions(machine):
    execution = Execution(machine, "1a1*1")
    for _ in execution:
        pass
    assert execution.result.status is Status.REJECTED
    assert execution.result.steps == 0
    assert "alfabeto de entrada" in execution.result.reason
