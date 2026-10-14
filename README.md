
# TP2 — Fundamentos de Inteligência Artificial

Trabalho Prático 2 da disciplina de Fundamentos de Inteligência Artificial, da Universidade Federal de Minas Gerais (UFMG).

O trabalho consiste na implementação e comparação de algoritmos de otimização aplicados ao problema de sequenciamento de manutenção de ativos de uma concessionária de energia.

Foram utilizadas três instâncias de diferentes tamanhos, com o objetivo de analisar o desempenho dos algoritmos, a qualidade das soluções encontradas e o custo computacional das buscas.

## 1. Algoritmos implementados

### Greedy Descent (GD)

Implementação de busca local com reinícios aleatórios, considerando:

- Best Improvement;
- First Improvement;
- Vizinhança Swap;
- Vizinhança Insertion;
- Vizinhança 2-opt.

As diferentes estratégias e vizinhanças foram utilizadas para comparar a qualidade das soluções e o comportamento da busca.

### Simulated Annealing (SA)

Implementação de recozimento simulado com:

- Calibração da temperatura inicial;
- Resfriamento geométrico;
- Aceitação probabilística de movimentos de piora;
- Registro da taxa de aceitação durante a execução;
- Controle do orçamento de avaliações.

### Algoritmo Genético (GA)

Implementação de algoritmo genético para permutações, utilizando:

- População inicial;
- Seleção de indivíduos;
- Cruzamentos Order Crossover (OX) e Partially Mapped Crossover (PMX);
- Mutação;
- Elitismo;
- Acompanhamento da evolução e diversidade populacional.

## 2. Organização do projeto

```text
TP2-Fund-IA/
├── inputs/
│   ├── manutencao_pequena.txt
│   ├── manutencao_media.txt
│   └── manutencao_grande.txt
│
├── outputs/
│   ├── completo/
│   └── benchmark_incremental.csv
│
├── algoritmo_genetico.py
├── greedy_descent.py
├── simulated_annealing.py
├── otimizador.py
├── experimentos.py
├── benchmark_incremental.py
├── testes.py
├── main.py
├── requirements.txt
├── .gitignore
└── README.md
```

### Descrição dos arquivos

| Arquivo | Descrição |
|---|---|
| `otimizador.py` | Leitura das instâncias, função objetivo e avaliação das soluções |
| `greedy_descent.py` | Busca local, estratégias de melhoria e operadores de vizinhança |
| `simulated_annealing.py` | Implementação do recozimento simulado |
| `algoritmo_genetico.py` | Implementação do algoritmo genético e seus operadores |
| `experimentos.py` | Execução dos experimentos, geração de estatísticas e gráficos |
| `testes.py` | Testes de funcionamento e consistência |
| `benchmark_incremental.py` | Comparação entre avaliação completa e incremental |
| `main.py` | Rotina original de execução, preservada do desenvolvimento inicial |
| `inputs/` | Instâncias utilizadas nos experimentos |
| `outputs/` | Resultados, dados estatísticos e gráficos |

**Observação:** o arquivo `experimentos.py` é o responsável pela execução oficial dos experimentos apresentados neste trabalho. O `main.py` foi mantido como parte do desenvolvimento inicial do grupo.

## 3. Requisitos

Para executar o projeto, é necessário ter instalado:

- Python 3.10 ou superior;
- NumPy;
- Matplotlib;
- SciPy.

As bibliotecas utilizadas estão listadas em `requirements.txt`.

## 4. Instalação

Clone o repositório:

```bash
git clone https://github.com/Thalesed/TP2-Fund-IA.git
```

Acesse a pasta:

```bash
cd TP2-Fund-IA
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

## 5. Testes automatizados

Antes de executar os experimentos, é possível verificar o funcionamento dos principais componentes:

```bash
python testes.py
```

Os testes incluem:

- Conferência da função objetivo;
- Validação do valor de referência `h = 4366`;
- Comparação entre avaliação completa e incremental;
- Verificação dos operadores Swap, Insertion e 2-opt;
- Validação das permutações produzidas pelos cruzamentos OX e PMX.

Para comparar o desempenho das avaliações:

```bash
python benchmark_incremental.py
```

Os resultados são armazenados em `outputs/benchmark_incremental.csv`.

Esse benchmark mede o tempo das funções de avaliação, sem incluir todos os custos envolvidos na geração e aplicação dos movimentos.

## 6. Execução dos experimentos

Os experimentos são executados pelo arquivo `experimentos.py`.

### Execução rápida

```bash
python experimentos.py --modo rapido
```

Utilizada para verificar o funcionamento dos algoritmos e a geração dos arquivos, com três repetições por configuração e instância, utilizando orçamentos reduzidos.

Os resultados são armazenados em:

```text
outputs/rapido/
```

### Execução completa

```bash
python experimentos.py --modo completo
```

Executa o protocolo experimental utilizado no trabalho.

| Instância | Orçamento de avaliações | Repetições |
|---|---:|---:|
| Pequena | 50.000 | 30 |
| Média | 150.000 | 30 |
| Grande | 300.000 | 10 |

Foram consideradas seis configurações:

1. GD — Best Improvement com Insertion;
2. GD — First Improvement com Insertion;
3. GD — Best Improvement com Swap;
4. GD — Best Improvement com 2-opt;
5. Simulated Annealing;
6. Algoritmo Genético.

No total, foram realizadas **420 execuções experimentais**, com sementes registradas para permitir a reprodução.

O orçamento contabiliza as avaliações das soluções iniciais e, no Simulated Annealing, as avaliações utilizadas na calibração de temperatura.

Os resultados completos são armazenados em:

```text
outputs/completo/
```

## 7. Resultados gerados

A execução completa produz os seguintes arquivos:

| Arquivo | Conteúdo |
|---|---|
| `execucoes.csv` | Resultados individuais, sementes, tempos e avaliações |
| `estatisticas.csv` | Estatísticas descritivas dos experimentos |
| `testes_estatisticos.csv` | Comparações estatísticas entre os algoritmos |
| `curvas.csv` | Dados das curvas de convergência |
| `indicadores.csv` | Indicadores do Simulated Annealing e Algoritmo Genético |

Também são gerados 18 gráficos, distribuídos entre as três instâncias:

- Boxplots dos resultados;
- Curvas de convergência;
- Comparações entre as vizinhanças do Greedy Descent;
- Comparações entre Best Improvement e First Improvement;
- Taxa de aceitação do Simulated Annealing e diversidade do Algoritmo Genético;
- Evolução da população do Algoritmo Genético.

Os testes estatísticos utilizam o método bilateral de Mann–Whitney para comparar GD, SA e GA. Os p-valores registrados não possuem correção para múltiplas comparações.

## 8. Considerações sobre os experimentos

A qualidade das soluções é medida pela função objetivo `h`, sendo considerados melhores os menores valores encontrados.

Os experimentos foram realizados nas três instâncias com os orçamentos estabelecidos, permitindo observar diferenças entre os algoritmos e suas configurações.

A avaliação incremental foi implementada e comparada à avaliação completa. Embora tenha apresentado resultados equivalentes nos testes de correção, sua eficiência computacional variou conforme a instância e a vizinhança utilizada.

Os algoritmos estocásticos foram executados com diferentes sementes para permitir a análise da variabilidade dos resultados.

Os arquivos disponíveis em `outputs/completo/` correspondem aos experimentos realizados com a versão corrigida do projeto.

Caso sejam alterados os algoritmos, seus parâmetros ou a função objetivo, os experimentos afetados deverão ser executados novamente para atualizar os resultados.

## 9. Relatório

A descrição detalhada da modelagem, das escolhas de implementação, da metodologia experimental e da análise dos resultados será apresentada no relatório acadêmico do TP2.

Os dados e gráficos utilizados nessa análise estão disponíveis na pasta `outputs/completo/`.
