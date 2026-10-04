class Tape:
    """Fita infinita nos dois sentidos, guardada de forma esparsa.

    Só as células diferentes do branco ocupam memória; qualquer índice
    inteiro (positivo ou negativo) é válido.
    """

    def __init__(self, blank: str):
        self.blank = blank
        self.head = 0
        self._cells: dict[int, str] = {}

    def load(self, word: str) -> None:
        """Escreve `word` a partir da posição 0 e posiciona o cabeçote nela."""
        self._cells = {i: s for i, s in enumerate(word) if s != self.blank}
        self.head = 0

    def read(self) -> str:
        return self._cells.get(self.head, self.blank)

    def write(self, symbol: str) -> None:
        if symbol == self.blank:
            self._cells.pop(self.head, None)
        else:
            self._cells[self.head] = symbol

    def move(self, direction: str) -> None:
        if direction == "R":
            self.head += 1
        elif direction == "L":
            self.head -= 1
        elif direction != "S":
            raise ValueError(f"direção inválida: {direction!r}")

    def window(self) -> tuple[str, int]:
        """Trecho visitado da fita e a posição do cabeçote dentro dele."""
        lo = min(self._cells, default=self.head)
        hi = max(self._cells, default=self.head)
        lo, hi = min(lo, self.head), max(hi, self.head)
        text = "".join(self._cells.get(i, self.blank) for i in range(lo, hi + 1))
        return text, self.head - lo

    def content(self) -> str:
        """Conteúdo da fita do primeiro ao último símbolo não branco."""
        if not self._cells:
            return ""
        lo, hi = min(self._cells), max(self._cells)
        return "".join(self._cells.get(i, self.blank) for i in range(lo, hi + 1))

    def __len__(self) -> int:
        """Quantidade de células não brancas (memória realmente usada)."""
        return len(self._cells)
