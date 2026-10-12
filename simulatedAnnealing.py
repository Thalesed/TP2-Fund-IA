import random
import math

from otimizador import Otimizador, OrcamentoEsgotado

SWAP = 'swap'
INSERTION = 'insertion' 
TWO_OPT = '2opt'

class SimulatedAnnealing(Otimizador):
    def __init__(self, arquivo, orcamento, T0=None, Tf=0.01, alpha=0.995, vizinhanca=SWAP):
        super().__init__(arquivo, orcamento)
        self.vizinhanca = vizinhanca
        self.T0 = T0
        self.Tf = Tf
        self.alpha = alpha
        self.taxa_aceitacao = []

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

    def _calibrar_T0(self):
        if self.T0 is not None:
            return self.T0
        amostras = []
        sol = self.solucao_aleatoria()
        c_atual = self.h(sol, contar=False)
        for _ in range(100):
            viz = self.successor_aleatorio(sol)
            c_viz = self.h(viz, contar=False)
            if c_viz > c_atual:
                amostras.append(c_viz - c_atual)
        if not amostras:
            return 1.0
        media = sum(amostras) / len(amostras)
        return -media / math.log(0.8) if media > 0 else 1.0

    def executar(self):
        T = self._calibrar_T0()
        try:
            sol = self.solucao_aleatoria()
            self.h(sol)
            custo_atual = self.h(sol, contar=False)
            melhor = list(sol)
            melhor_custo = custo_atual
            aceitos_piores = 0
            total_piores = 0
            while True:
                viz = self.successor_aleatorio(sol)
                c_viz = self.h(viz)
                delta = c_viz - custo_atual
                aceita = False
                if delta <= 0:
                    aceita = True
                else:
                    total_piores += 1
                    if random.random() < math.exp(-delta / T):
                        aceita = True
                        aceitos_piores += 1
                if aceita:
                    sol = viz
                    custo_atual = c_viz
                    if c_viz < melhor_custo:
                        melhor = list(viz)
                        melhor_custo = c_viz
                if total_piores > 0:
                    self.taxa_aceitacao.append((self.avaliacoes, aceitos_piores / total_piores))
                T = max(T * self.alpha, self.Tf)
        except OrcamentoEsgotado:
            pass
        return melhor, melhor_custo