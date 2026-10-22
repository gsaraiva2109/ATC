import sys
from pathlib import Path

# Garante que a pasta src seja encontrada pelo pytest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from main import main
from tm import Result, Snapshot, Status, format_result, format_snapshot, format_tape

MULT_PATH = str(ROOT / "machines/multiplicacao.txt")


def test_format_snapshot_matches_issue_example():
    snap = Snapshot(step=3, state="q2", tape="111*11", head=2)
    line = format_snapshot(snap, "B", color=False)
    assert line == "Passo   3 | estado: q2 | ...B 1 1 [1] * 1 1 B..."


def test_format_tape_highlights_head_at_edges():
    snap_left = Snapshot(step=0, state="q0", tape="B11", head=0)
    assert format_tape(snap_left, "B", color=False) == "...B [B] 1 1 B..."

    snap_right = Snapshot(step=5, state="q0", tape="11B", head=2)
    assert format_tape(snap_right, "B", color=False) == "...B 1 1 [B] B..."


def test_format_result_displays_status_steps_and_final_tape():
    res = Result(
        status=Status.ACCEPTED,
        steps=79,
        state="q_fim",
        tape="111111",
        reason="parou no estado final q_fim",
    )
    text = format_result(res, color=False)
    assert "Status: ACEITA" in text
    assert "Total de passos: 79" in text
    assert "Fita final: 111111" in text


def test_cli_valid_multiplication_trace(capsys):
    code = main([MULT_PATH, "111*11", "--no-color"])
    out = capsys.readouterr().out
    assert code == 0
    assert "Passo   0 |" in out
    assert "[1] 1 1 * 1 1" in out
    assert "Status: ACEITA" in out
    assert "Fita final: 111111" in out


def test_cli_quiet_mode_hides_steps(capsys):
    code = main([MULT_PATH, "111*11", "--quiet", "--no-color"])
    out = capsys.readouterr().out
    assert code == 0
    assert "Passo " not in out
    assert "Status: ACEITA" in out
    assert "Fita final: 111111" in out


def test_cli_rejected_input_returns_nonzero_without_traceback(capsys):
    code = main([MULT_PATH, "1a1*1", "--no-color"])
    captured = capsys.readouterr()
    assert code != 0
    assert "Traceback" not in captured.err
    assert "Traceback" not in captured.out
    assert "Status: REJEITADA" in captured.out
    assert "alfabeto de entrada" in captured.out


def test_cli_missing_file_friendly_error(capsys):
    code = main(["arquivo_inexistente.txt", "1*1", "--no-color"])
    captured = capsys.readouterr()
    assert code != 0
    assert "Erro ao carregar a máquina" in captured.err
    assert "Traceback" not in captured.err