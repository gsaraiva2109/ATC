from pathlib import Path

from .errors import MTFormatError
from .machine import Rule, TuringMachine

DIRECTIONS = {"R", "L", "S"}
HEADERS = [
    "lista de estados",
    "alfabeto de entrada",
    "alfabeto da fita",
    "símbolo de branco",
    "estado inicial",
    "estados finais",
]


def _split(text: str) -> list[str]:
    return [part.strip() for part in text.split(",")]


def _symbol_list(line: tuple[int, str], what: str) -> list[str]:
    number, text = line
    items = _split(text)
    for item in items:
        if len(item) != 1:
            raise MTFormatError(
                f"linha {number}: {what} deve conter símbolos de 1 caractere, encontrado {item!r}"
            )
    return items


def _name_list(line: tuple[int, str], what: str) -> list[str]:
    number, text = line
    items = _split(text)
    if not all(items):
        raise MTFormatError(f"linha {number}: {what} contém um item vazio")
    return items


def parse_machine(text: str) -> TuringMachine:
    """Interpreta o conteúdo de um arquivo de definição de MT.

    Linhas em branco e linhas iniciadas por ';' são ignoradas. As seis
    primeiras linhas de dados são lidas por posição (estados, alfabeto de
    entrada, alfabeto da fita, branco, estado inicial, estados finais); as
    demais são regras de transição.
    """
    data = [
        (number, line.strip())
        for number, line in enumerate(text.splitlines(), start=1)
        if line.strip() and not line.strip().startswith(";")
    ]
    if len(data) < len(HEADERS):
        faltando = HEADERS[len(data)]
        raise MTFormatError(
            f"arquivo incompleto: esperava {len(HEADERS)} linhas de definição "
            f"antes das regras, faltou '{faltando}'"
        )

    states = _name_list(data[0], "lista de estados")
    input_alpha = _symbol_list(data[1], "alfabeto de entrada")
    tape_alpha = _symbol_list(data[2], "alfabeto da fita")
    blank_items = _symbol_list(data[3], "símbolo de branco")
    start_items = _name_list(data[4], "estado inicial")
    finals = _name_list(data[5], "estados finais")

    if len(blank_items) != 1:
        raise MTFormatError(f"linha {data[3][0]}: deve haver exatamente um símbolo de branco")
    blank = blank_items[0]
    if len(start_items) != 1:
        raise MTFormatError(f"linha {data[4][0]}: deve haver exatamente um estado inicial")
    start = start_items[0]

    state_set, input_set, tape_set = set(states), set(input_alpha), set(tape_alpha)
    if blank not in tape_set:
        raise MTFormatError(f"linha {data[3][0]}: branco {blank!r} não pertence ao alfabeto da fita")
    if blank in input_set:
        raise MTFormatError(f"linha {data[1][0]}: o alfabeto de entrada não pode conter o branco")
    if not input_set <= tape_set:
        extra = ", ".join(sorted(input_set - tape_set))
        raise MTFormatError(f"linha {data[1][0]}: símbolos de entrada fora do alfabeto da fita: {extra}")
    if start not in state_set:
        raise MTFormatError(f"linha {data[4][0]}: estado inicial {start!r} não está na lista de estados")
    for final in finals:
        if final not in state_set:
            raise MTFormatError(f"linha {data[5][0]}: estado final {final!r} não está na lista de estados")

    rules: dict[tuple[str, str], Rule] = {}
    for number, text_line in data[len(HEADERS):]:
        fields = _split(text_line)
        if len(fields) != 5:
            raise MTFormatError(
                f"linha {number}: regra deve ter 5 campos (origem, lê, escreve, direção, destino), "
                f"encontrados {len(fields)}"
            )
        origin, read, write, move, target = fields
        for name, label in ((origin, "origem"), (target, "destino")):
            if name not in state_set:
                raise MTFormatError(f"linha {number}: estado de {label} {name!r} não está na lista de estados")
        for symbol, label in ((read, "lido"), (write, "escrito")):
            if len(symbol) != 1 or symbol not in tape_set:
                raise MTFormatError(
                    f"linha {number}: símbolo {label} {symbol!r} não pertence ao alfabeto da fita"
                )
        if move not in DIRECTIONS:
            raise MTFormatError(f"linha {number}: direção {move!r} inválida (use R, L ou S)")
        key = (origin, read)
        if key in rules:
            raise MTFormatError(
                f"linha {number}: regra duplicada para ({origin}, {read}); a máquina deve ser determinística"
            )
        rules[key] = Rule(write, move, target)

    return TuringMachine(
        states=frozenset(states),
        input_alphabet=frozenset(input_alpha),
        tape_alphabet=frozenset(tape_alpha),
        blank=blank,
        start=start,
        finals=frozenset(finals),
        rules=rules,
    )


def load_machine(path: str | Path) -> TuringMachine:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        raise MTFormatError(f"arquivo não encontrado: {path}") from None
    except UnicodeDecodeError:
        raise MTFormatError(f"arquivo não está em UTF-8: {path}") from None
    if not text.strip():
        raise MTFormatError(f"arquivo vazio: {path}")
    return parse_machine(text)
