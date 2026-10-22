# Simulador de Máquina de Turing - Equipe 1

Este projeto implementa um simulador de Máquina de Turing (MT) Determinística com fita única infinita. Além do motor de simulação genérico, a equipe modelou um **Transdutor de Multiplicação Unária** que calcula $n \times m$ (ex: `111*11` resulta em `111111`).

## Requisitos
* Python 3.10 ou superior.
* Nenhuma biblioteca externa é necessária para rodar a simulação (apenas biblioteca padrão).
* `pytest` (apenas para rodar a suíte de testes).

## Como Executar 

Execute o arquivo `main.py` passando o caminho das regras da máquina e a palavra de entrada. 
Para ver o passo a passo com destaque do cabeçote:

```bash
# Execução interativa (pressione Enter para avançar cada passo)
python src/main.py machines/multiplicacao.txt "11*111" --step

# Execução automática com atraso (delay)
python src/main.py machines/multiplicacao.txt "111*11" --delay 0.1

# Execução silenciosa (mostra apenas o resultado final)
python src/main.py machines/multiplicacao.txt "1111*1111" --quiet