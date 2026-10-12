from greedyDescent import GreedyDescent
from algoritimoGenetico import Genetico
from simulatedAnnealing import SimulatedAnnealing
import time
import os
import csv
import statistics

from greedyDescent import (
    GreedyDescent,
    SWAP, INSERTION, TWO_OPT,
    BEST_IMPROVEMENT, FIRST_IMPROVEMENT, RANDOM
)
from simulatedAnnealing import SimulatedAnnealing
from algoritimoGenetico import (
    Genetico,
    OX, PMX, TORNEIO, ROULETTE
)

DIR_OUTPUTS = 'outputs'
os.makedirs(DIR_OUTPUTS, exist_ok=True)

INSTANCIAS = {
    'pequena': ('inputs/manutencao_pequena.txt', 50000, 30),
    'media':   ('inputs/manutencao_media.txt',   150000, 30),
    'grande':  ('inputs/manutencao_grande.txt',  300000, 10),
}


def rodar(nome, otimizador):
    inicio = time.time()
    sol, custo = otimizador.executar()
    tempo = time.time() - inicio
    print(f"{nome:30s} h={custo:8.1f}  aval={otimizador.avaliacoes:7d}  tempo={tempo:6.2f}s")
    return custo, tempo, otimizador.avaliacoes


def matriz_metodos(nome_instancia):
    arquivo, orcamento, _ = INSTANCIAS[nome_instancia]
    return {
        'GD_best_swap':      lambda a=arquivo, o=orcamento: GreedyDescent(a, o, BEST_IMPROVEMENT, SWAP),
        'GD_best_insertion': lambda a=arquivo, o=orcamento: GreedyDescent(a, o, BEST_IMPROVEMENT, INSERTION),
        'GD_best_2opt':      lambda a=arquivo, o=orcamento: GreedyDescent(a, o, BEST_IMPROVEMENT, TWO_OPT),
        'GD_first_swap':     lambda a=arquivo, o=orcamento: GreedyDescent(a, o, FIRST_IMPROVEMENT, SWAP),
        'GD_random_swap':    lambda a=arquivo, o=orcamento: GreedyDescent(a, o, RANDOM, SWAP),
        'SA_swap':           lambda a=arquivo, o=orcamento: SimulatedAnnealing(a, o, vizinhanca=SWAP),
        'SA_insertion':      lambda a=arquivo, o=orcamento: SimulatedAnnealing(a, o, vizinhanca=INSERTION),
        'SA_2opt':           lambda a=arquivo, o=orcamento: SimulatedAnnealing(a, o, vizinhanca=TWO_OPT),
        'GA_ox_torneio':     lambda a=arquivo, o=orcamento: Genetico(a, o, selecao=TORNEIO, cruzamento=OX),
        'GA_pmx_torneio':    lambda a=arquivo, o=orcamento: Genetico(a, o, selecao=TORNEIO, cruzamento=PMX),
        'GA_ox_roleta':      lambda a=arquivo, o=orcamento: Genetico(a, o, selecao=ROULETTE, cruzamento=OX),
    }


def experimento_completo():
    linhas = []
    for nome_inst, (arquivo, orcamento, n_exec) in INSTANCIAS.items():
        print(f"\n=== Instancia {nome_inst} (B={orcamento}, {n_exec} execucoes) ===")
        fabricas = matriz_metodos(nome_inst)
        for nome_alg, fabrica in fabricas.items():
            custos, tempos, avals = [], [], []
            for _ in range(n_exec):
                ot = fabrica()
                c, t, a = rodar(f"{nome_inst}/{nome_alg}", ot)
                custos.append(c)
                tempos.append(t)
                avals.append(a)
            linha = {
                'instancia': nome_inst,
                'algoritmo': nome_alg,
                'media': statistics.mean(custos),
                'desvio': statistics.pstdev(custos) if len(custos) > 1 else 0.0,
                'minimo': min(custos),
                'mediana': statistics.median(custos),
                'maximo': max(custos),
                'tempo_medio': statistics.mean(tempos),
                'avaliacoes_media': statistics.mean(avals),
            }
            linhas.append(linha)
    return linhas


def salvar_csv(linhas):
    caminho = os.path.join(DIR_OUTPUTS, 'resultados.csv')
    with open(caminho, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=[
            'instancia', 'algoritmo', 'media', 'desvio',
            'minimo', 'mediana', 'maximo', 'tempo_medio', 'avaliacoes_media'
        ])
        w.writeheader()
        for l in linhas:
            w.writerow(l)
    print(f"\nResultados salvos em {caminho}")


if __name__ == '__main__':
    linhas = experimento_completo()
    salvar_csv(linhas)