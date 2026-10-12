import random
import math
from abc import ABC, abstractmethod


class OrcamentoEsgotado(Exception):
    pass

def ler_arquivo(arquivo):
    with open(arquivo, 'r') as f:
        linhas = [l.strip() for l in f if l.strip()]
    n = int(linhas[0])
    x0, y0 = map(float, linhas[1].split())
    ativos = []
    for i in range(2, 2 + n):
        x, y, p, d, w = map(float, linhas[i].split())
        ativos.append({'id': i - 1, 'x': x, 'y': y, 'p': p, 'd': d, 'w': w})
    return {'n': n, 'base': (x0, y0), 'ativos': ativos}


class Otimizador(ABC):
    def __init__(self, arquivo, orcamento):
        if isinstance(arquivo, str):
            instancia = ler_arquivo(arquivo)
        else:
            instancia = arquivo

        self.instancia = instancia
        self.orcamento = orcamento
        self.avaliacoes = 0
        self.n = instancia['n']
        self.base = instancia['base']
        self.ativos = instancia['ativos']
        self.matriz_t = self.calcular_tempos()
        self.melhor_solucao = None
        self.melhor_custo = float('inf')
        self.historico = []

    def calcular_tempos(self):
        pontos = [self.base] + [(a['x'], a['y']) for a in self.ativos]
        n = len(pontos)
        t = [[0] * (n + 1) for _ in range(n + 1)]
        for i in range(n):
            for j in range(n):
                if i != j:
                    dx = pontos[i][0] - pontos[j][0]
                    dy = pontos[i][1] - pontos[j][1]
                    t[i][j] = int(round(math.sqrt(dx * dx + dy * dy)))
        return t

    def h(self, solucao, contar=True):
        if contar:
            self.avaliacoes += 1
            if self.avaliacoes > self.orcamento:
                raise OrcamentoEsgotado()
        custo = 0
        C = 0
        anterior = 0
        for idx in solucao:
            C += self.matriz_t[anterior][idx] + self.ativos[idx - 1]['p']
            atraso = C - self.ativos[idx - 1]['d']
            if atraso > 0:
                custo += self.ativos[idx - 1]['w'] * atraso
            anterior = idx
        if contar:
            if custo < self.melhor_custo:
                self.melhor_custo = custo
                self.melhor_solucao = list(solucao)
            self.historico.append((self.avaliacoes, self.melhor_custo))
        return custo

    def solucao_aleatoria(self):
        sol = list(range(1, self.n + 1))
        random.shuffle(sol)
        return sol

    @abstractmethod
    def executar(self):
        pass