"""Testes básicos para verificar o cálculo dos custos e os operadores."""

import random
import time
from pathlib import Path
from otimizador import Otimizador
from greedy_descent import GreedyDescent, SWAP, INSERTION, TWO_OPT
from algoritmo_genetico import Genetico, PMX, OX

BASE = Path(__file__).resolve().parent

# Conferimos primeiro um valor conhecido e depois várias mudanças de sequência.
def testar():
    arq = str(BASE / 'inputs/manutencao_pequena.txt')
    gd = GreedyDescent(arq, 10000)
    identidade = list(range(1, 13))
    assert gd.h(identidade, contar=False) == 4366
    print('Teste da identidade: h = 4366 (OK)')
    random.seed(2026)
    for tipo in [SWAP, INSERTION, TWO_OPT]:
        gd.vizinhanca = tipo
        for _ in range(200):
            atual = gd.solucao_aleatoria()
            viz = gd.successor_aleatorio(atual)
            inicio = next(i for i in range(gd.n) if atual[i] != viz[i])
            assert gd.h_incremental(atual, viz, inicio, contar=False) == gd.h(viz, contar=False)
        print(f'Avaliação incremental, {tipo}: 200 testes OK')
    ga = Genetico(arq, 1000, cruzamento=PMX)
    for op in [OX, PMX]:
        ga.cruzamento = op
        for _ in range(300):
            a, b = ga.solucao_aleatoria(), ga.solucao_aleatoria()
            filho = ga._cruzamento(a, b)
            assert sorted(filho) == identidade, (op, filho)
        print(f'Cruzamento {op}: 300 permutações válidas')
    for tipo in [SWAP, INSERTION, TWO_OPT]:
        gd.vizinhanca = tipo
        atual = gd.solucao_aleatoria()
        pares = [gd.successor_aleatorio(atual) for _ in range(10000)]
        ini=time.perf_counter()
        for v in pares: gd.h(v, contar=False)
        t_completo=time.perf_counter()-ini
        ini=time.perf_counter()
        for v in pares:
            indice=next(i for i in range(gd.n) if atual[i]!=v[i])
            gd.h_incremental(atual,v,indice,contar=False)
        t_incremental=time.perf_counter()-ini
        print(f'{tipo}: completo={t_completo:.4f}s incremental={t_incremental:.4f}s (inclui busca pelo índice)')

if __name__ == '__main__':
    testar()
