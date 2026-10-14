# TP2 — Fundamentos de Inteligência Artificial

Implementação e comparação de algoritmos de otimização para o problema de **sequenciamento de manutenção de ativos**. O trabalho utiliza três instâncias (pequena, média e grande) e compara a qualidade das soluções por meio da função objetivo `h` (quanto menor, melhor).

## Algoritmos implementados

- **Greedy Descent (GD)** com reinícios aleatórios, estratégias *Best Improvement* e *First Improvement* e vizinhanças **Swap**, **Insertion** e **2-opt**.
- **Simulated Annealing (SA)** com calibração da temperatura inicial e resfriamento geométrico ao longo do orçamento de avaliações.
- **Algoritmo Genético (GA)** com seleção, cruzamento, mutação e elitismo.

Na comparação principal, `GD` corresponde a Best Improvement com Insertion. `GD_first` usa First Improvement com Insertion. `GD_swap` e `GD_2opt` utilizam Best Improvement com as respectivas vizinhanças.

## Requisitos e instalação

É necessário **Python 3.10 ou superior**. Abra o terminal na pasta do projeto e instale as dependências:

```bash
python -m pip install -r requirements.txt
```

## Testes e execução

Para conferir a implementação antes dos experimentos:

```bash
python testes.py
python benchmark_incremental.py
```

O primeiro comando verifica o valor de referência `h = 4366` da instância pequena, a equivalência da avaliação incremental e a validade das permutações geradas pelos cruzamentos. O segundo mede os tempos das avaliações completa e incremental para cada vizinhança e instância, salvando `outputs/benchmark_incremental.csv`. As medições não incluem a geração prévia dos vizinhos nem a busca pelo índice inicial do trecho afetado; portanto, não representam necessariamente o tempo total de uma iteração do algoritmo.

Para conferir rapidamente se o conjunto de experimentos está funcionando:

```bash
python experimentos.py --modo rapido
```

Para executar o protocolo completo utilizado no trabalho:

```bash
python experimentos.py --modo completo
```

O modo rápido faz **3 repetições por instância**, com orçamentos reduzidos, apenas para exploração e depuração. O modo completo utiliza:

| Instância | Avaliações por execução | Repetições por configuração |
|---|---:|---:|
| Pequena | 50.000 | 30 |
| Média | 150.000 | 30 |
| Grande | 300.000 | 10 |

São **6 configurações × (30 + 30 + 10) = 420 execuções**. O orçamento inclui as avaliações de soluções iniciais e, no SA, as avaliações da calibração de temperatura. Cada execução registra sua semente, permitindo reproduzir os resultados. A calibração do SA busca uma aceitação inicial próxima de 95% para movimentos de piora típicos, mas isso não garante a mesma taxa observada em cada janela.

## Arquivos do projeto

| Arquivo/pasta | Conteúdo |
|---|---|
| `otimizador.py` | Leitura das instâncias, função objetivo e operações de avaliação |
| `greedy_descent.py` | Busca local, estratégias de melhoria e vizinhanças |
| `simulated_annealing.py` | Recozimento simulado e temperatura |
| `algoritmo_genetico.py` | Operadores e execução do algoritmo genético |
| `experimentos.py` | Execução das repetições, estatísticas e geração de gráficos |
| `testes.py` | Testes básicos e de consistência |
| `benchmark_incremental.py` | Comparação de tempos de avaliação |
| `main.py` | Código original de entrada do projeto |
| `inputs/` | Instâncias pequena, média e grande |
| `outputs/` | Arquivos produzidos nos experimentos |

Os nomes dos arquivos Python foram mantidos conforme a organização usada pelo grupo.

## Resultados e gráficos

A execução completa salva os resultados em `outputs/completo/`, e a rápida em `outputs/rapido/`.

- `execucoes.csv`: valor final de `h`, semente, tempo e número de avaliações de cada execução.
- `estatisticas.csv`: média, desvio-padrão, mediana, mínimo e indicadores agregados.
- `testes_estatisticos.csv`: comparações bilaterais de Mann–Whitney entre GD, SA e GA; os p-valores **não** foram ajustados para comparações múltiplas.
- `curvas.csv` e `indicadores.csv`: dados das curvas de convergência e dos indicadores do SA e GA.
- Arquivos `.png`: boxplots, convergência, comparação de vizinhanças e estratégias, aceitação do SA, diversidade e evolução da população do GA.

Os resultados já incluídos em `outputs/completo/` correspondem à versão corrigida dos experimentos. Os testes e comentários adicionados posteriormente não modificam a lógica dos algoritmos. Se forem feitas alterações nos algoritmos ou nos parâmetros, os experimentos afetados devem ser executados novamente.

## Observações

- Os valores de referência do enunciado não foram utilizados para fabricar dados experimentais.
- A avaliação incremental é conferida quanto ao valor calculado, mas pode não ser mais rápida em todas as instâncias: isso depende do movimento e do custo adicional da implementação em Python.
- O arquivo `.gitignore` exclui caches, ambientes virtuais e resultados exploratórios. Mantivemos os resultados oficiais em `outputs/completo/` para consulta do grupo e para o relatório.
