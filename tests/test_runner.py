import pytest

from tm import Execution, Status, parse_machine, run

# troca todos os 'a' por 'X' e aceita ao ver o branco
REPLACE = """\
q0,qf
a
a,X,B
B
q0
qf
q0, a, X, R, q0
q0, B, B, S, qf
"""

# aceita palavras da forma a* (b leva a estado sem saída)
ONLY_A = """\
q0,q1,qf
a,b
a,b,B
B
q0
qf
q0, a, a, R, q0
q0, B, B, S, qf
"""

# anda para a esquerda para sempre
LOOP = """\
q0,qf
a
a,B
B
q0
qf
q0, a, a, L, q0
q0, B, B, L, q0
"""

# escreve 'a' à esquerda da entrada: a fita cresce para índices negativos
LEFT = """\
q0,q1,qf
a
a,B
B
q0
qf
q0, a, a, L, q1
q1, B, a, S, qf
"""


def test_transducer_final_tape_is_output():
    result = run(parse_machine(REPLACE), "aaa")
    assert result.status is Status.ACCEPTED
    assert result.tape == "XXX"
    assert result.steps == 4
    assert result.state == "qf"


def test_accepts_and_rejects():
    machine = parse_machine(ONLY_A)
    assert run(machine, "aaa").status is Status.ACCEPTED
    rejected = run(machine, "aab")
    assert rejected.status is Status.REJECTED
    assert "q0" in rejected.reason and "b" in rejected.reason


def test_step_limit():
    result = run(parse_machine(LOOP), "a", max_steps=1000)
    assert result.status is Status.LIMIT_EXCEEDED
    assert result.steps == 1000


def test_zero_step_limit_still_accepts_if_already_final():
    machine = parse_machine("qf\na\na,B\nB\nqf\nqf\n")
    assert run(machine, "a", max_steps=0).status is Status.ACCEPTED


def test_tape_grows_left():
    result = run(parse_machine(LEFT), "a")
    assert result.status is Status.ACCEPTED
    assert result.tape == "aa"


def test_snapshots_trace_each_configuration():
    execution = Execution(parse_machine(REPLACE), "aa")
    snaps = list(execution)
    assert [s.step for s in snaps] == [0, 1, 2, 3]
    assert [s.state for s in snaps] == ["q0", "q0", "q0", "qf"]
    assert (snaps[0].tape, snaps[0].head) == ("aa", 0)
    assert (snaps[1].tape, snaps[1].head) == ("Xa", 1)
    assert (snaps[3].tape, snaps[3].head) == ("XXB", 2)
    assert execution.result is not None
    assert execution.result.steps == 3


def test_result_unavailable_until_iterated():
    execution = Execution(parse_machine(REPLACE), "a")
    assert execution.result is None


def test_invalid_input_symbols():
    machine = parse_machine(ONLY_A)
    for word, symbol in [("abc", "c"), ("aXa", "X")]:
        result = run(machine, word)
        assert result.status is Status.REJECTED
        assert result.steps == 0
        assert result.state not in machine.finals
        assert "alfabeto de entrada" in result.reason
        assert repr(symbol) in result.reason


def test_blank_in_input_is_invalid():
    machine = parse_machine(ONLY_A)
    result = run(machine, "aBa")
    assert result.status is Status.REJECTED
    assert result.steps == 0
    assert result.state not in machine.finals
    assert "alfabeto de entrada" in result.reason
    assert "'B'" in result.reason


def test_empty_input():
    # ONLY_A reconhece a*: inclui a palavra vazia.
    # A regra (q0, B) leva ao estado final qf.
    result = run(parse_machine(ONLY_A), "")
    assert result.status is Status.ACCEPTED
    assert result.state == "qf"
    assert result.steps == 1
    assert result.tape == ""


def test_negative_step_limit():
    with pytest.raises(ValueError):
        run(parse_machine(ONLY_A), "a", max_steps=-1)
