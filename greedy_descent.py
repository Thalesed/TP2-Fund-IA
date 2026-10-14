"""Busca local com diferentes vizinhanças e critérios para aceitar uma melhoria."""

import random

from otimizador import Otimizador, OrcamentoEsgotado

SWAP = 'swap'
INSERTION = 'insertion'
TWO_OPT = '2opt'

BEST_IMPROVEMENT = 'best_improvement'
FIRST_IMPROVEMENT = 'first_improvement'
RANDOM = 'random'

class GreedyDescent(Otimizador):
    def __init__(self, arquivo, orcamento, variante=BEST_IMPROVEMENT, vizinhanca=SWAP, incremental=True):
        super().__init__(arquivo, orcamento)
        self.variante = variante
        self.vizinhanca = vizinhanca
        self.incremental = incremental
        self.otimos_locais = set()
        self.passos_melhoria = 0
        self.reinicios = 0

    # Cada vizinhança modifica a ordem das manutenções de uma maneira diferente.
    # Cada vizinhança modifica a ordem das manutenções de uma maneira diferente.
    def sucessores(self, solucao):
        n = len(solucao)
        if self.vizinhanca == SWAP:
            for i in range(n):
                for j in range(i + 1, n):
                    viz = list(solucao)
                    viz[i], viz[j] = viz[j], viz[i]
                    yield viz
        elif self.vizinhanca == INSERTION:
            for i in range(n):
                for j in range(n):
                    if i != j:
                        viz = list(solucao)
                        ativo = viz.pop(i)
                        viz.insert(j, ativo)
                        yield viz
        elif self.vizinhanca == TWO_OPT:
            for i in range(n):
                for j in range(i + 1, n):
                    viz = list(solucao)
                    viz[i:j + 1] = viz[i:j + 1][::-1]
                    yield viz

    def successor_aleatorio(self, solucao):
        n = len(solucao)
        viz = list(solucao)
        if self.vizinhanca == SWAP:
            i, j = random.sample(range(n), 2)
            viz[i], viz[j] = viz[j], viz[i]
        elif self.vizinhanca == INSERTION:
            i, j = random.sample(range(n), 2)
            ativo = viz.pop(i)
            viz.insert(j, ativo)
        elif self.vizinhanca == TWO_OPT:
            i, j = sorted(random.sample(range(n), 2))
            viz[i:j + 1] = viz[i:j + 1][::-1]
        return viz

    # A primeira posição diferente indica de onde precisamos recalcular o custo.
    # A primeira posição diferente indica de onde precisamos recalcular o custo.
    def avaliar_vizinho(self, atual, viz, custo_atual):
        if not self.incremental:
            return self.h(viz)
        inicio = next((i for i, (a, b) in enumerate(zip(atual, viz)) if a != b), len(atual))
        return self.h_incremental(atual, viz, inicio, custo_atual)

    def _busca_local(self, solucao):
        try:
            atual = list(solucao)
            custo_atual = self.h(atual)
            while True:
                melhorou = False
                # No best improvement olhamos todos os vizinhos antes de escolher.
                # No best improvement olhamos todos os vizinhos antes de escolher.
                if self.variante == BEST_IMPROVEMENT:
                    melhor_viz = None
                    melhor_custo_viz = custo_atual
                    for viz in self.sucessores(atual):
                        c = self.avaliar_vizinho(atual, viz, custo_atual)
                        if c < melhor_custo_viz:
                            melhor_custo_viz = c
                            melhor_viz = viz
                    if melhor_viz is not None:
                        atual = melhor_viz
                        custo_atual = melhor_custo_viz
                        melhorou = True
                        self.passos_melhoria += 1
                # No first improvement seguimos com o primeiro vizinho que melhora o custo.
                # No first improvement seguimos com o primeiro vizinho que melhora o custo.
                elif self.variante == FIRST_IMPROVEMENT:
                    for viz in self.sucessores(atual):
                        c = self.avaliar_vizinho(atual, viz, custo_atual)
                        if c < custo_atual:
                            atual = viz
                            custo_atual = c
                            melhorou = True
                            self.passos_melhoria += 1
                            break
                elif self.variante == RANDOM:
                    viz = self.successor_aleatorio(atual)
                    c = self.avaliar_vizinho(atual, viz, custo_atual)
                    if c < custo_atual:
                        atual = viz
                        custo_atual = c
                        melhorou = True
                        self.passos_melhoria += 1
                if not melhorou:
                    if self.variante != RANDOM:
                        self.otimos_locais.add(tuple(atual))
                    break
            return atual, custo_atual
        except OrcamentoEsgotado:
            raise

    # Reiniciamos a busca em ordens aleatórias enquanto houver avaliações disponíveis.
    # Reiniciamos a busca em ordens aleatórias enquanto houver avaliações disponíveis.
    def executar(self):
        try:
            while True:
                sol = self.solucao_aleatoria()
                self.reinicios += 1
                self._busca_local(sol)
        except OrcamentoEsgotado:
            pass
        return self.melhor_solucao, self.melhor_custo