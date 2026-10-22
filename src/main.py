import argparse
import os
import sys
import time
from pathlib import Path

# Garante que `python src/main.py` encontre o pacote `tm` independente do PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent))

from tm import (  # noqa: E402
     Execution,
    MTFormatError,
    Status,
    format_result,
    format_snapshot,
    load_machine,
)
from tm.runner import DEFAULT_MAX_STEPS  # noqa: E402


def _enable_windows_ansi() -> None:
    if os.name == "nt":
        os.system("")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Simulador de Máquina de Turing Determinística de Fita Única.",
    )
    parser.add_argument(
        "machine",
        help="Caminho para o arquivo .txt de definição da Máquina de Turing.",
    )
    parser.add_argument(
        "word",
        help="Palavra de entrada inicial na fita (ex: '111*11').",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=DEFAULT_MAX_STEPS,
        help=f"Limite máximo de passos antes de abortar (padrão: {DEFAULT_MAX_STEPS}).",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Oculta o passo a passo (trace) e exibe apenas o resultado final.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="Atraso em segundos entre cada passo impresso (ex: 0.2).",
    )
    parser.add_argument(
        "--step",
        action="store_true",
        help="Modo passo a passo interativo (pressione Enter para avançar).",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Desativa cores ANSI na saída do terminal.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.max_steps < 0:
        print("Erro: --max-steps não pode ser negativo.", file=sys.stderr)
        return 2
    if args.delay < 0:
        print("Erro: --delay não pode ser negativo.", file=sys.stderr)
        return 2

    use_color = not args.no_color and "NO_COLOR" not in os.environ
    if use_color:
        _enable_windows_ansi()

    try:
        machine = load_machine(args.machine)
    except MTFormatError as exc:
        print(f"Erro ao carregar a máquina: {exc}", file=sys.stderr)
        return 2

    execution = Execution(machine, args.word, max_steps=args.max_steps)
    state_width = max((len(s) for s in machine.states), default=0)

    try:
        for snapshot in execution:
            if not args.quiet:
                line = format_snapshot(
                    snapshot,
                    machine.blank,
                    state_width=state_width,
                    color=use_color,
                )
                if args.step:
                    print(line, end="", flush=True)
                    input("  [Enter]")
                else:
                    print(line, flush=True)
                    if args.delay > 0:
                        time.sleep(args.delay)
    except (KeyboardInterrupt, EOFError):
        print("\nExecução interrompida pelo usuário.", file=sys.stderr)
        return 130

    assert execution.result is not None
    if not args.quiet:
        print("-" * 60)
    print(format_result(execution.result, color=use_color))

    return 0 if execution.result.status is Status.ACCEPTED else 1


if __name__ == "__main__":
    raise SystemExit(main())