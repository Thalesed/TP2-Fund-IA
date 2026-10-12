import random

from otimizador import Otimizador, OrcamentoEsgotado

SWAP = 'swap'
INSERTION = 'insertion' 
TWO_OPT = '2opt'

OX = 'order_crossover'
PMX = 'partially_mapped_crossover'

TORNEIO = 'torneio'
ROULETTE = 'roleta'

class Genetico(Otimizador):
    def __init__(self, arquivo, orcamento, N=50, Pc=0.8, Pm=0.1,
                 selecao=TORNEIO, cruzamento=OX, mutacao=SWAP, elitismo=2):
        super().__init__(arquivo, orcamento)
        self.N = N
        self.Pc = Pc
        self.Pm = Pm
        self.selecao = selecao
        self.cruzamento = cruzamento
        self.mutacao = mutacao
        self.elitismo = elitismo
        self.diversidade = []

    def populacao_inicial(self):
        return [self.solucao_aleatoria() for _ in range(self.N)]

    def _selecao_torneio(self, populacao, custos, k=3):
        indices = random.sample(range(len(populacao)), k)
        melhor = min(indices, key=lambda i: custos[i])
        return list(populacao[melhor])

    def _selecao_roleta(self, populacao, custos):
        max_c = max(custos)
        aptidoes = [max_c - c + 1 for c in custos]
        total = sum(aptidoes)
        r = random.random() * total
        acumulado = 0
        for i, a in enumerate(aptidoes):
            acumulado += a
            if acumulado >= r:
                return list(populacao[i])
        return list(populacao[-1])

    def _selecionar(self, populacao, custos):
        if self.selecao == TORNEIO:
            return self._selecao_torneio(populacao, custos)
        else:
            return self._selecao_roleta(populacao, custos)

    def _order_crossover(self, p1, p2):
        n = len(p1)
        i, j = sorted(random.sample(range(n), 2))
        filho = [None] * n
        filho[i:j + 1] = p1[i:j + 1]
        restantes = [x for x in p2 if x not in filho]
        pos = 0
        for k in range(n):
            if filho[k] is None:
                filho[k] = restantes[pos]
                pos += 1
        return filho

    def _partially_mapped_crossover(self, p1, p2):
        n = len(p1)
        i, j = sorted(random.sample(range(n), 2))
        filho = [None] * n
        filho[i:j + 1] = p1[i:j + 1]
        for k in range(i, j + 1):
            if p2[k] not in filho:
                pos = k
                while True:
                    pos = p2.index(p1[pos])
                    if filho[pos] is None:
                        filho[pos] = p2[k]
                        break
        for k in range(n):
            if filho[k] is None:
                filho[k] = p2[k]
        return filho

    def _cruzamento(self, p1, p2):
        if self.cruzamento == OX:
            return self._order_crossover(p1, p2)
        else:
            return self._partially_maped_crossover(p1, p2)

    def _mutacao(self, individuo):
        if random.random() > self.Pm:
            return individuo
        n = len(individuo)
        viz = list(individuo)
        if self.mutacao == SWAP:
            i, j = random.sample(range(n), 2)
            viz[i], viz[j] = viz[j], viz[i]
        elif self.mutacao == INSERTION:
            i, j = random.sample(range(n), 2)
            ativo = viz.pop(i)
            viz.insert(j, ativo)
        elif self.mutacao == TWO_OPT:
            i, j = sorted(random.sample(range(n), 2))
            viz[i:j + 1] = viz[i:j + 1][::-1]
        return viz

    def _calcular_diversidade(self, populacao):
        distintas = len(set(tuple(ind) for ind in populacao))
        return distintas

    def executar(self):
        try:
            populacao = self.populacao_inicial()
            custos = [self.h(ind) for ind in populacao]
            while True:
                nova_pop = []
                ordenados = sorted(range(self.N), key=lambda i: custos[i])
                for i in range(self.elitismo):
                    nova_pop.append(list(populacao[ordenados[i]]))
                while len(nova_pop) < self.N:
                    p1 = self._selecionar(populacao, custos)
                    p2 = self._selecionar(populacao, custos)
                    if random.random() < self.Pc:
                        filho = self._cruzamento(p1, p2)
                    else:
                        filho = list(p1)
                    filho = self._mutacao(filho)
                    nova_pop.append(filho)
                populacao = nova_pop
                custos = [self.h(ind) for ind in populacao]
                self.diversidade.append((self.avaliacoes, self._calcular_diversidade(populacao)))
        except OrcamentoEsgotado:
            pass
        return self.melhor_solucao, self.melhor_custo