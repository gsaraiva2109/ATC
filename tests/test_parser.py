import pytest

from tm import MTFormatError, Rule, load_machine, parse_machine

VALID = """\
; Lista de Estados
q0,q1,q2,q_aceita,q_rejeita
; Alfabeto de Entrada
a,b,c
; Alfabeto da Fita
a,b,c,X,Y,Z,B
; Simbolo de Branco
B
; Estado Inicial
q0
; Estados Finais
q_aceita

; Regras
q0, a, X, R, q1
q1, b, Y, L, q2
"""


def with_rules(*rules, header=None):
    lines = header or [
        "q0,q1,qf",
        "a,b",
        "a,b,X,B",
        "B",
        "q0",
        "qf",
    ]
    return "\n".join(lines + list(rules))


def test_parses_pdf_example():
    m = parse_machine(VALID)
    assert m.states == {"q0", "q1", "q2", "q_aceita", "q_rejeita"}
    assert m.input_alphabet == {"a", "b", "c"}
    assert m.tape_alphabet == {"a", "b", "c", "X", "Y", "Z", "B"}
    assert m.blank == "B"
    assert m.start == "q0"
    assert m.finals == {"q_aceita"}
    assert m.rules[("q0", "a")] == Rule("X", "R", "q1")
    assert m.rules[("q1", "b")] == Rule("Y", "L", "q2")
    assert len(m.rules) == 2


def test_load_machine_from_file(tmp_path):
    path = tmp_path / "m.txt"
    path.write_text(VALID, encoding="utf-8")
    assert load_machine(path).start == "q0"


def test_missing_file():
    with pytest.raises(MTFormatError, match="não encontrado"):
        load_machine("/nao/existe.txt")


def test_empty_file(tmp_path):
    path = tmp_path / "vazio.txt"
    path.write_text("  \n\n", encoding="utf-8")
    with pytest.raises(MTFormatError, match="vazio"):
        load_machine(path)


def test_comment_only_file(tmp_path):
    path = tmp_path / "comentario.txt"
    path.write_text("; só comentário\n\n", encoding="utf-8")
    with pytest.raises(MTFormatError, match="incompleto"):
        load_machine(path)


def test_incomplete_header():
    with pytest.raises(MTFormatError, match="incompleto"):
        parse_machine("q0\na\na,B\nB\n")


def test_no_rules_is_allowed():
    assert parse_machine(with_rules()).rules == {}


@pytest.mark.parametrize(
    "rule, message",
    [
        ("q0, a, X, R", "5 campos"),
        ("q0, a, X, R, q1, extra", "5 campos"),
        ("qx, a, X, R, q1", "origem"),
        ("q0, a, X, R, qx", "destino"),
        ("q0, c, X, R, q1", "lido"),
        ("q0, a, Z, R, q1", "escrito"),
        ("q0, a, X, Q, q1", "direção"),
    ],
)
def test_rule_errors_report_line_number(rule, message):
    with pytest.raises(MTFormatError, match=rf"linha 7: .*{message}"):
        parse_machine(with_rules(rule))


def test_duplicate_rule():
    text = with_rules("q0, a, X, R, q1", "q0, a, X, L, q1")
    with pytest.raises(MTFormatError, match="linha 8: .*duplicada"):
        parse_machine(text)


@pytest.mark.parametrize(
    "header, message",
    [
        (["q0,qf", "a,b", "a,b,X", "B", "q0", "qf"], "branco"),
        (["q0,qf", "a,b,B", "a,b,B", "B", "q0", "qf"], "entrada não pode conter o branco"),
        (["q0,qf", "a,c", "a,b,B", "B", "q0", "qf"], "fora do alfabeto da fita"),
        (["q0,qf", "a", "a,B", "B", "qx", "qf"], "estado inicial"),
        (["q0,qf", "a", "a,B", "B", "q0", "qx"], "estado final"),
        (["q0,qf", "a", "a,B", "B,X", "q0", "qf"], "símbolos de 1 caractere|exatamente um"),
        (["q0,qf", "a", "a,B", "B", "q0,qf", "qf"], "exatamente um estado inicial"),
        (["q0,,qf", "a", "a,B", "B", "q0", "qf"], "item vazio"),
        (["q0,qf", "ab", "a,B", "B", "q0", "qf"], "1 caractere"),
    ],
)
def test_header_errors(header, message):
    with pytest.raises(MTFormatError, match=message):
        parse_machine("\n".join(header))


def test_comments_and_blank_lines_keep_real_line_numbers():
    text = "; c\n\nq0,qf\na\na,B\nB\nq0\nqf\n\nq0, z, a, R, qf\n"
    with pytest.raises(MTFormatError, match="linha 10"):
        parse_machine(text)
