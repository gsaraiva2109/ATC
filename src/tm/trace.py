from .runner import Result, Snapshot, Status

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"


def format_tape(
    snapshot: Snapshot,
    blank: str = "B",
    *,
    margin: int = 1,
    color: bool = False,
) -> str:
    """Formata a janela da fita com margem de brancos e cabeçote entre colchetes."""
    if margin < 0:
        raise ValueError("margin não pode ser negativa")

    def _fmt_blank(symbol: str) -> str:
        return f"{DIM}{symbol}{RESET}" if color else symbol

    def _fmt_head(symbol: str) -> str:
        token = f"[{symbol}]"
        return f"{BOLD}{YELLOW}{token}{RESET}" if color else token

    left = [_fmt_blank(blank) for _ in range(margin)]
    right = [_fmt_blank(blank) for _ in range(margin)]

    middle: list[str] = []
    for index, symbol in enumerate(snapshot.tape):
        if index == snapshot.head:
            middle.append(_fmt_head(symbol))
        elif symbol == blank:
            middle.append(_fmt_blank(symbol))
        else:
            middle.append(symbol)

    body = " ".join(left + middle + right)
    dots = f"{DIM}...{RESET}" if color else "..."
    return f"{dots}{body}{dots}"


def format_snapshot(
    snapshot: Snapshot,
    blank: str = "B",
    *,
    step_width: int = 3,
    state_width: int = 0,
    margin: int = 1,
    color: bool = False,
) -> str:
    """Formata uma linha do passo a passo (trace) da execução."""
    step_text = f"{snapshot.step:>{step_width}}"
    state_padded = f"{snapshot.state:<{state_width}}" if state_width > 0 else snapshot.state
    if color:
        state_padded = f"{CYAN}{state_padded}{RESET}"
    tape_text = format_tape(snapshot, blank, margin=margin, color=color)
    return f"Passo {step_text} | estado: {state_padded} | {tape_text}"


def format_result(result: Result, *, color: bool = False) -> str:
    """Formata o resumo final da simulação."""
    status_text = result.status.value
    if color:
        status_color = {
            Status.ACCEPTED: GREEN,
            Status.REJECTED: RED,
            Status.LIMIT_EXCEEDED: YELLOW,
        }[result.status]
        status_text = f"{BOLD}{status_color}{status_text}{RESET}"

    final_tape = result.tape if result.tape else "(vazia)"
    lines = [
        f"Status: {status_text}",
        f"Motivo: {result.reason}",
        f"Estado final: {result.state}",
        f"Total de passos: {result.steps}",
        f"Fita final: {final_tape}",
    ]
    return "\n".join(lines)