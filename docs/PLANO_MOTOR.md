# Plano do motor do simulador (Membro A, 3,0 pts)

Critérios do PDF: fita infinita funcional, tratamento de erros, leitura correta do `.txt`.

## Estrutura

```
src/tm/
  errors.py    # MTFormatError, InputError
  tape.py      # Tape
  machine.py   # Rule, TuringMachine (dados imutáveis da MT)
  parser.py    # load_machine(path) -> TuringMachine
  runner.py    # run(machine, input, max_steps) -> Iterator[Snapshot] + Result
tests/
  test_tape.py  test_parser.py  test_runner.py
```

## 1. Fita infinita (`tape.py`)

- `dict[int, str]` esparso (índice -> símbolo) e `head: int` começando em 0. Células ausentes valem `blank`.
- `read()` = `cells.get(head, blank)`.
- `write(sym)`: se `sym == blank`, remove a chave (a fita não cresce com brancos); senão grava.
- `move(R|L|S)`: ajusta `head` (±1 ou 0). Não existe índice negativo "inválido", então cresce para os dois lados sem realocar nem limite de array.
- Memória proporcional às células **não brancas**, não à distância percorrida. Esta é a resposta da "defesa de arquitetura" na apresentação.
- Para o trace, `window()` devolve `(texto, pos_cabeçote)` entre `min(chaves ∪ {head})` e `max(chaves ∪ {head})`.
- Alternativa descartada: lista com `append`/`insert(0)`, que custa O(n) na esquerda.

## 2. Modelo (`machine.py`)

```python
@dataclass(frozen=True)
class Rule: write: str; move: str; next_state: str

@dataclass(frozen=True)
class TuringMachine:
    states: frozenset[str]
    input_alphabet: frozenset[str]
    tape_alphabet: frozenset[str]
    blank: str
    start: str
    finals: frozenset[str]
    rules: dict[tuple[str, str], Rule]   # (estado, símbolo lido) -> Rule
```

Determinismo garantido pela chave do dicionário. Uma regra duplicada vira erro no parser.

## 3. Parser (`parser.py`)

Formato da seção 4 do PDF. Linhas em branco são ignoradas. Linhas que começam com `;` são comentários e **servem como marcadores de seção**, mas a leitura é posicional: as 5 primeiras linhas de dados (estados, alfabeto de entrada, alfabeto da fita, branco, estado inicial), depois finais, depois regras (uma por linha, 5 campos separados por vírgula, com `strip()`).

Validações, todas com `MTFormatError("linha N: ...")`:
- Seções ausentes ou fora de ordem.
- Branco fora do alfabeto da fita; alfabeto de entrada que não é subconjunto do alfabeto da fita; branco no alfabeto de entrada.
- Estado inicial ou final fora de `states`.
- Regra com campos ≠ 5, estado de origem ou destino inexistente, símbolo lido ou escrito fora do alfabeto da fita, direção fora de `R/L/S`.
- Regra duplicada para o mesmo `(estado, símbolo)`.
- Aviso opcional para regras saindo de estados finais (ignoradas na execução).
- Arquivo inexistente ou vazio (`FileNotFoundError` convertido em erro claro).

Decisão sobre símbolos multi-caractere: aceitar tokens de qualquer tamanho, mas o alfabeto de **entrada** é fornecido como string e dividido em símbolos de 1 caractere (a entrada `111*11` é lida caractere a caractere).

## 4. Execução (`runner.py`)

```python
@dataclass(frozen=True)
class Snapshot: step: int; state: str; tape: str; head: int  # head = índice dentro de `tape`
class Status(Enum): ACCEPTED, REJECTED, LIMIT_EXCEEDED
@dataclass(frozen=True)
class Result: status: Status; steps: int; tape: str; state: str; reason: str
```

`run(machine, word, max_steps=100_000)` é um **gerador** de `Snapshot` (o passo 0 é a configuração inicial). O `Result` fica disponível ao final, por exemplo via `return` do gerador ou uma classe `Run` com `.result`. O Membro C consome só `Snapshot` e `Result`.

Fluxo:
1. Valida `word`: não vazia e todo símbolo ∈ alfabeto de entrada, senão `InputError`. Escreve a palavra a partir da posição 0.
2. Laço: emite o snapshot da configuração atual.
   - Se o estado está em `finals` → `ACCEPTED`.
   - Se `steps >= max_steps` → `LIMIT_EXCEEDED`.
   - Procura `rules[(state, tape.read())]`; se não existe → `REJECTED` ("sem transição").
   - Aplica `write`, `move`, troca de estado, `steps += 1`.
3. Semântica: **parar em estado final = aceita; parar sem regra em estado não final = rejeita**. No transdutor, o resultado é o conteúdo da fita na parada.

Decisão: o PDF cita "aceitar, rejeitar ou parar (no caso de transdutores)". Tratamos "parada em final" como aceitação e a fita final como saída. Isso precisa ser alinhado com o Membro C para a mensagem de status.

## 5. Testes

- **Fita**: cresce à esquerda e à direita, escrever branco remove a célula, `window()` correto, `S` não move.
- **Parser**: arquivo válido de exemplo do PDF, um teste por erro de validação, com checagem do número da linha, comentários e linhas em branco.
- **Runner**: MTs pequenas escritas à mão (ex.: troca `a`→`X`; aceitar `a*`; loop infinito para o `LIMIT_EXCEEDED`; entrada inválida; rejeição por falta de regra).

## 6. Ordem de implementação

1. `errors.py`, `tape.py` + testes.
2. `machine.py`, `parser.py` + testes (usar o exemplo do PDF).
3. `runner.py` + testes.
4. Avisar o Membro C que a API (`Snapshot`, `Result`, `run`) está estável.
5. Rodar a máquina do Membro B de ponta a ponta.

## Pontos para a arguição
- Por que `dict` esparso e não lista (uso de memória, O(1) nas duas pontas).
- Por que o limite de passos (problema da parada é indecidível; não dá para detectar todo loop).
- Determinismo: uma regra por `(estado, símbolo)`.
- Diferença entre reconhecedor e transdutor.
