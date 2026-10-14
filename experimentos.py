"""Experimentos reprodutíveis do TP2. Execute: python experimentos.py --modo completo"""
import argparse
import csv
import math
import random
import statistics
import time
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu
from greedy_descent import GreedyDescent, BEST_IMPROVEMENT, FIRST_IMPROVEMENT, SWAP, INSERTION, TWO_OPT
from simulated_annealing import SimulatedAnnealing
from algoritmo_genetico import Genetico, OX, PMX

ROOT = Path(__file__).resolve().parent
DADOS = {'pequena':(50000,30), 'media':(150000,30),'grande':(300000,10)}
COLUNAS = ['instancia','algoritmo','execucao','semente','h','tempo_s','avaliacoes','passos_melhoria','reinicios','otimos_locais','T0']

def salvar_csv(caminho, linhas):
    with caminho.open('w', newline='',encoding='utf-8') as f:
        if not linhas:return
        w=csv.DictWriter(f,fieldnames=list(linhas[0]));w.writeheader();w.writerows(linhas)

# Mantemos as sementes fixas para reproduzir e comparar as execuções.
def run(modo='completo'):
    destino=ROOT/'outputs'/modo
    destino.mkdir(parents=True,exist_ok=True)
    resumo=[]; curvas=[]; extras=[]
    for instancia,(B,rep) in DADOS.items():
        if modo=='rapido': B=min(B,10000 if instancia=='pequena' else 12000);rep=3
        arq=str(ROOT/'inputs'/f'manutencao_{instancia}.txt')
        configs=[('GD',lambda:GreedyDescent(arq,B,BEST_IMPROVEMENT,INSERTION)),('SA',lambda:SimulatedAnnealing(arq,B,vizinhanca=INSERTION)),('GA',lambda:Genetico(arq,B,cruzamento=OX))]
        # Também testamos três vizinhanças e duas formas de escolher melhorias no GD.
        configs_viz=[('GD_swap',lambda:GreedyDescent(arq,B,BEST_IMPROVEMENT,SWAP)),('GD_2opt',lambda:GreedyDescent(arq,B,BEST_IMPROVEMENT,TWO_OPT)),('GD_first',lambda:GreedyDescent(arq,B,FIRST_IMPROVEMENT,INSERTION))]
        for alg, fabrica in configs+configs_viz:
            for rodada in range(rep):
                seed=20261013+rodada
                random.seed(seed)
                ot=fabrica()
                t=time.perf_counter();sol,custo=ot.executar();duracao=time.perf_counter()-t
                # Uma rodada só é válida quando respeita o orçamento previsto.
                assert ot.avaliacoes==B,(instancia,alg,ot.avaliacoes,B)
                assert ot.h(sol,contar=False)==custo
                resumo.append(dict(instancia=instancia,algoritmo=alg,execucao=rodada+1,semente=seed,h=custo,tempo_s=round(duracao,5),avaliacoes=ot.avaliacoes,passos_melhoria=getattr(ot,'passos_melhoria',''),reinicios=getattr(ot,'reinicios',''),otimos_locais=len(getattr(ot,'otimos_locais',[])) if alg.startswith('GD') else '',T0=getattr(ot,'temperatura_inicial','')))
                for x,y in ot.historico:
                    if x==1 or x==B or x%max(1,B//100)==0:curvas.append(dict(instancia=instancia,algoritmo=alg,execucao=rodada+1,avaliacoes=x,serie='melhor',valor=y))
                for nome,atributo in [('media_populacao','media_populacao'),('diversidade','diversidade'),('taxa_aceitacao','taxa_aceitacao')]:
                    for x,y in getattr(ot,atributo,[]):
                        extras.append(dict(instancia=instancia,algoritmo=alg,execucao=rodada+1,avaliacoes=x,serie=nome,valor=y))
                print(instancia,alg,rodada+1,'h=',custo,'tempo=',round(duracao,2),'s',flush=True)
                salvar_csv(destino/'execucoes.csv',resumo)
        criar_graficos(destino,instancia,resumo,curvas,extras,B)
    salvar_csv(destino/'curvas.csv',curvas)
    salvar_csv(destino/'indicadores.csv',extras)
    # Calculamos as medidas descritivas e comparamos os métodos principais.
    estatisticas=[];testes=[]
    for instancia in DADOS:
        for algoritmo in ['GD','SA','GA','GD_swap','GD_2opt','GD_first']:
            linhas=[r for r in resumo if r['instancia']==instancia and r['algoritmo']==algoritmo]
            valores=[r['h'] for r in linhas]
            if not valores:continue
            estatisticas.append(dict(instancia=instancia,algoritmo=algoritmo,media=statistics.mean(valores),desvio_padrao=statistics.stdev(valores) if len(valores)>1 else 0,minimo=min(valores),mediana=statistics.median(valores),tempo_medio_s=statistics.mean(r['tempo_s'] for r in linhas),avaliacoes=linhas[0]['avaliacoes'],gap_medio_pct=(statistics.mean(valores)-1875)/1875*100 if instancia=='pequena' else ''))
        for a,b in [('GD','SA'),('GD','GA'),('SA','GA')]:
            v1=[r['h'] for r in resumo if r['instancia']==instancia and r['algoritmo']==a]
            v2=[r['h'] for r in resumo if r['instancia']==instancia and r['algoritmo']==b]
            testes.append(dict(instancia=instancia,comparacao=f'{a} x {b}',p_valor=mannwhitneyu(v1,v2,alternative='two-sided').pvalue))
    salvar_csv(destino/'estatisticas.csv',estatisticas)
    salvar_csv(destino/'testes_estatisticos.csv',testes)
    print('Arquivos disponíveis em:',destino)

def interp(curvas,instancia,alg,rodada,x):
    pontos=[r for r in curvas if r['instancia']==instancia and r['algoritmo']==alg and r['execucao']==rodada]
    pontos.sort(key=lambda r:r['avaliacoes'])
    if not pontos:return np.full(len(x),np.nan)
    xx=[r['avaliacoes'] for r in pontos];yy=[r['valor'] for r in pontos]
    return np.interp(x,xx,yy,left=yy[0],right=yy[-1])

# Os gráficos ajudam a observar distribuição, convergência e comportamento da busca.
def criar_graficos(destino,instancia,resumo,curvas,extras,B):
    mapa={'GD':'Greedy Descent','SA':'Simulated Annealing','GA':'Algoritmo Genético'}
    grupos=[[r['h'] for r in resumo if r['instancia']==instancia and r['algoritmo']==alg] for alg in mapa]
    fig,ax=plt.subplots(figsize=(8,5));ax.boxplot(grupos,tick_labels=list(mapa.values()));ax.set_ylabel('Melhor h (menor é melhor)');ax.set_title('Comparação dos algoritmos — '+instancia);ax.grid(axis='y',alpha=.3);fig.tight_layout();fig.savefig(destino/f'boxplot_{instancia}.png',dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5));x=np.linspace(1,B,101)
    for alg,rotulo in mapa.items():
        rodadas=sorted(set(r['execucao'] for r in resumo if r['instancia']==instancia and r['algoritmo']==alg))
        y=np.median([interp(curvas,instancia,alg,rod,x) for rod in rodadas],axis=0)
        ax.plot(x,y,label=rotulo)
    ax.set(xlabel='Avaliações da função h',ylabel='Mediana do melhor h',title=f'Convergência — {instancia}');ax.legend();ax.grid(alpha=.3);fig.tight_layout();fig.savefig(destino/f'convergencia_{instancia}.png',dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5))
    dados=[[r['h'] for r in resumo if r['instancia']==instancia and r['algoritmo']==alg] for alg in ['GD_swap','GD','GD_2opt']]
    ax.boxplot(dados,tick_labels=['swap','insertion','2-opt']);ax.set(xlabel='Vizinhança',ylabel='Melhor h',title=f'Greedy Descent: vizinhanças — {instancia}');ax.grid(axis='y',alpha=.3);fig.tight_layout();fig.savefig(destino/f'vizinhancas_{instancia}.png',dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,5))
    dados=[[r['h'] for r in resumo if r['instancia']==instancia and r['algoritmo']==alg] for alg in ['GD','GD_first']]
    ax.boxplot(dados,tick_labels=['Best improvement','First improvement'])
    ax.set(ylabel='Melhor h',title=f'Greedy Descent: estratégias — {instancia}')
    ax.grid(axis='y',alpha=.3);fig.tight_layout();fig.savefig(destino/f'variantes_gd_{instancia}.png',dpi=170);plt.close(fig)
    fig,axs=plt.subplots(1,2,figsize=(12,4.5))
    for serie,eixo,titulo in [('taxa_aceitacao',axs[0],'SA: aceitação de movimentos piores'),('diversidade',axs[1],'GA: diversidade da população')]:
        linhas=[r for r in extras if r['instancia']==instancia and r['serie']==serie]
        for rod in sorted(set(r['execucao'] for r in linhas)):
            rec=[r for r in linhas if r['execucao']==rod]
            eixo.plot([r['avaliacoes'] for r in rec],[r['valor'] for r in rec],alpha=.24)
        eixo.set(xlabel='Avaliações',ylabel='Taxa',title=titulo);eixo.grid(alpha=.3)
    fig.tight_layout();fig.savefig(destino/f'aceitacao_diversidade_{instancia}.png',dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5))
    for serie,rotulo in [('melhor','Melhor solução do GA'),('media_populacao','Média da população do GA')]:
        fonte=curvas if serie=='melhor' else extras
        rec=[r for r in fonte if r['instancia']==instancia and r['algoritmo']=='GA' and r['serie']==serie and r['execucao']==1]
        if rec:ax.plot([r['avaliacoes'] for r in rec],[r['valor'] for r in rec],label=rotulo)
    ax.set(xlabel='Avaliações',ylabel='h',title=f'Algoritmo Genético: população — {instancia}');ax.legend();ax.grid(alpha=.3);fig.tight_layout();fig.savefig(destino/f'populacao_ga_{instancia}.png',dpi=170);plt.close(fig)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--modo',choices=['rapido','completo'],default='rapido');args=parser.parse_args();run(args.modo)
