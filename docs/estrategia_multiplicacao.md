# Estratégia da máquina de multiplicação

A entrada tem o formato `1^n*1^m`, com pelo menos um `1` de cada lado do `*`. A máquina faz a multiplicação por cópias: para cada `1` do primeiro fator, copia todos os `1`s do segundo fator para a área do resultado.

Por exemplo, em `111*11`, o segundo fator tem dois `1`s e é copiado três vezes. O resultado é `111111`.

## Símbolos da fita

| Símbolo | Uso |
| --- | --- |
| `1` | Representa uma unidade nos fatores e no resultado. |
| `*` | Separa os dois fatores. |
| `X` | Marca uma unidade do primeiro fator que já foi escolhida para uma rodada de cópia. |
| `Y` | Marca uma unidade do segundo fator que está sendo copiada na rodada atual. |
| `#` | Separa o segundo fator da área do resultado. |
| `B` | Representa uma célula em branco. |

A entrada só permite `1` e `*`. Os demais símbolos são usados durante a execução.

## Percurso do cabeçote

Primeiro, a máquina percorre a entrada para conferir se há dois fatores não vazios separados por um único `*`. Ao chegar ao branco depois do segundo fator, escreve `#` e volta ao início.

Em seguida, procura um `1` do primeiro fator e o troca por `X`. O cabeçote segue até o segundo fator, marca seu primeiro `1` com `Y` e vai até o fim da área do resultado para escrever um novo `1`. Depois volta até o `Y` e avança uma posição para copiar a próxima unidade.

Quando chega ao `#` durante essa cópia, o segundo fator inteiro já foi copiado. A máquina volta para a esquerda, troca os `Y`s por `1`s e retorna ao início da fita. Assim, o segundo fator fica pronto para a próxima rodada.

Esse processo se repete até que todos os `1`s do primeiro fator tenham virado `X`. Ao encontrar o `*` nessa busca, a máquina inicia a limpeza: apaga o separador, os `X`s, o segundo fator e o `#`. Só os `1`s do produto permanecem na fita. O cabeçote termina sobre o primeiro `1` do resultado, no estado `q_fim`.

O resultado fica à direita da posição original da entrada. As células anteriores ficam em branco; não é necessário deslocar o produto para a posição zero.

## Função dos estados

| Estado | O que faz |
| --- | --- |
| `q_inicio` | Exige que a entrada comece com `1`. |
| `q_primeiro` | Percorre o primeiro fator até encontrar `*`. |
| `q_valida` | Exige pelo menos um `1` depois do `*`. |
| `q_segundo` | Percorre o segundo fator e escreve `#` no branco seguinte. |
| `q_volta` | Volta ao branco à esquerda da entrada e avança para o primeiro fator. |
| `q_escolhe` | Pula os `X`s e marca o próximo `1` com `X`. Se encontrar `*`, começa a limpeza. |
| `q_busca` | Avança até o `*` para entrar no segundo fator. |
| `q_copia` | Marca o próximo `1` com `Y`. Ao encontrar `#`, encerra a rodada de cópia. |
| `q_anexa` | Vai até o branco no fim do produto e escreve um `1`. |
| `q_produto` | Volta pela área do produto até atravessar o `#`. |
| `q_retorna` | Volta pelo segundo fator até o último `Y` e avança para continuar a cópia. |
| `q_restaura` | Troca os `Y`s por `1`s, voltando até o `*`. |
| `q_reinicia` | Volta pelo primeiro fator até o branco à esquerda e inicia outra busca. |
| `q_apaga_esq` | Apaga os `X`s do primeiro fator. |
| `q_apaga_dir` | Avança pelos brancos, apaga o segundo fator e remove o `#`. |
| `q_fim` | Estado final: o produto está pronto. |

## Exemplo: `111*11`

Estas são algumas situações da fita entre as rodadas, sem mostrar todos os movimentos do cabeçote:

```text
111*11#          entrada validada
X11*11#11        primeira cópia concluída e segundo fator restaurado
XX1*11#1111      segunda cópia concluída e segundo fator restaurado
XXX*11#111111    terceira cópia concluída e segundo fator restaurado
BBBBBBB111111   limpeza concluída
```

Cada rodada acrescenta dois `1`s. Como o primeiro fator tem três unidades, são três rodadas e seis unidades no resultado.

## Rejeição e testes

Entrada vazia, ausência de `*`, separador repetido e fator vazio fazem a máquina parar em estado não final por falta de transição. Uma entrada como `1a1*1` é rejeitada pelo motor antes das transições, porque `a` não pertence ao alfabeto de entrada.

O motor também tem um limite padrão de 100.000 passos. Atingir esse limite é informado separadamente da rejeição.

Os casos de multiplicação ficam em `tests/cases/multiplicacao.json`. Eles cobrem os seis exemplos válidos da issue e seis entradas inválidas. Para executar a suíte na raiz do projeto:

```text
python -m pytest -q
```

Na execução confirmada após a atualização dos testes, os 62 testes da suíte passaram. Esse total inclui os testes do motor, da fita e do parser, além dos testes de multiplicação.
