"""Recozimento simulado para testar trocas com aceitação probabilística."""

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
        self.temperatura_inicial = None

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

    # Antes da busca, estimamos uma temperatura inicial a partir de mudanças de custo.
    # Antes da busca, estimamos uma temperatura inicial a partir de mudanças de custo.
    def _calibrar_T0(self):
        """Amostra diferenças de custo, contando TODAS as avaliações no orçamento.

        Escolhemos T0 para aceitar aproximadamente 95% das pioras típicas.
        A amostragem faz uma caminhada aleatória curta para obter deltas variados.
        """
        if self.T0 is not None:
            return float(self.T0)
        sol = self.solucao_aleatoria()
        custo = self.h(sol)
        amostras = []
        for _ in range(min(200, max(0, self.orcamento // 100))):
            viz = self.successor_aleatorio(sol)
            cv = self.h(viz)
            if cv > custo:
                amostras.append(cv - custo)
            sol, custo = viz, cv
        if not amostras:
            return 1.0
        # Mediana é menos sensível aos saltos extremos que a média.
        amostras.sort()
        delta = amostras[len(amostras) // 2]
        return max(1.0, -delta / math.log(0.95))

    # No início aceitamos algumas pioras para explorar soluções diferentes;
            # depois a temperatura diminui e a busca fica mais seletiva.
    # No início aceitamos algumas pioras para explorar soluções diferentes;
            # depois a temperatura diminui e a busca fica mais seletiva.
    def executar(self):
        T0 = self._calibrar_T0()
        self.temperatura_inicial = T0
        # Resfriamento geométrico distribuído por todo o orçamento restante.
        # Temperatura final relativa, para funcionar com todas as escalas.
        Tf = max(self.Tf, T0 * 0.0001)
        restantes = max(1, self.orcamento - self.avaliacoes - 1)
        alpha_efetivo = (Tf / T0) ** (1 / restantes) if T0 > Tf else 1.0
        self.alpha_efetivo = alpha_efetivo
        T = T0
        sol = self.solucao_aleatoria()
        custo_atual = self.h(sol)
        melhor, melhor_custo = list(self.melhor_solucao), self.melhor_custo
        janela_piores = janela_aceitos = 0
        try:
            while True:
                viz = self.successor_aleatorio(sol)
                c_viz = self.h(viz)
                delta = c_viz - custo_atual
                aceita = delta <= 0
                if delta > 0:
                    janela_piores += 1
                    if random.random() < math.exp(-delta / max(T, 1e-12)):
                        aceita = True
                        janela_aceitos += 1
                if aceita:
                    sol, custo_atual = viz, c_viz
                    if c_viz < melhor_custo:
                        melhor, melhor_custo = list(viz), c_viz
                if self.avaliacoes % max(1, self.orcamento // 100) == 0:
                    self.taxa_aceitacao.append((self.avaliacoes, janela_aceitos / janela_piores if janela_piores else 0))
                    janela_piores = janela_aceitos = 0
                T = max(T * alpha_efetivo, Tf)
        except OrcamentoEsgotado:
            pass
        return melhor, melhor_custo
