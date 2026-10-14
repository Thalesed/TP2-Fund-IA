"""Compara tempo de avaliação completa e incremental nas três instâncias."""
import csv
import random
import time
from pathlib import Path
from greedy_descent import GreedyDescent, SWAP, INSERTION, TWO_OPT

BASE = Path(__file__).resolve().parent

# Medimos as duas formas de avaliação para observar onde a incremental ajuda.
def executar(amostras=2000):
    random.seed(20261013)
    linhas = []
    for tamanho in ('pequena', 'media', 'grande'):
        gd = GreedyDescent(str(BASE / 'inputs' / f'manutencao_{tamanho}.txt'), 1000000)
        for tipo in (SWAP, INSERTION, TWO_OPT):
            gd.vizinhanca = tipo
            origem = gd.solucao_aleatoria()
            vizinhos = [gd.successor_aleatorio(origem) for _ in range(amostras)]
            inicios = [next(i for i, (a, b) in enumerate(zip(origem, v)) if a != b) for v in vizinhos]
            custo_origem = gd.h(origem, contar=False)
            ini = time.perf_counter()
            completos = [gd.h(v, contar=False) for v in vizinhos]
            tempo_completo = time.perf_counter() - ini
            ini = time.perf_counter()
            incrementais = [gd.h_incremental(origem, v, p, custo_origem, contar=False) for v, p in zip(vizinhos, inicios)]
            tempo_incremental = time.perf_counter() - ini
            assert completos == incrementais, (tamanho, tipo)
            linhas.append(dict(instancia=tamanho, vizinhanca=tipo, amostras=amostras,
                               tempo_completo_s=round(tempo_completo, 6),
                               tempo_incremental_s=round(tempo_incremental, 6),
                               razao_incremental_completo=round(tempo_incremental / tempo_completo, 4)))
            print(tamanho, tipo, 'completo=', round(tempo_completo, 4),
                  'incremental=', round(tempo_incremental, 4), flush=True)
    destino = BASE / 'outputs' / 'benchmark_incremental.csv'
    destino.parent.mkdir(exist_ok=True)
    with destino.open('w', newline='', encoding='utf-8') as arquivo:
        w = csv.DictWriter(arquivo, fieldnames=list(linhas[0]))
        w.writeheader()
        w.writerows(linhas)
    print('Benchmark salvo em:', destino)

if __name__ == '__main__':
    executar()
