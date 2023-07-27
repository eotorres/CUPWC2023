import streamlit as st  
import pandas as pd
import numpy as np
import random
import time
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import poisson 


st.set_page_config(
    page_title = 'Predições de Jogos da Copa do Mundo Feminino ',
    page_icon = '⚽',
)

selecoes = pd.read_excel('dados/DadosCopaDoMundoQatar2022.xlsx', sheet_name ='selecoes', index_col = 0)

dados = pd.read_excel('dados/DadosCopaDoMundoQatar2022.xlsx', 
                         sheet_name='selecoes', 
                         index_col='Seleção')


fifa = selecoes['PontosRankingFIFA']
a, b = min(fifa), max(fifa) 
fa, fb = 0.15, 1 
b1 = (fb - fa)/(b-a) 
b0 = fb - b*b1
forca = b0 + b1*fifa 

lista07 = ['0', '1', '2', '3', '4', '5', '6', '7+']

def Resultado(gols1, gols2):
    if gols1 > gols2:
        res = 'V'
    if gols1 < gols2:
        res = 'D' 
    if gols1 == gols2:
        res = 'E'       
    return res

def MediasPoisson(selecao1, selecao2):
    forca1 = forca[selecao1]
    forca2 = forca[selecao2] 
    mgols = 2.75
    l1 = mgols*forca1/(forca1 + forca2)
    l2 = mgols*forca2/(forca1 + forca2)
    return [l1, l2]
    
def Distribuicao(media, tamanho = 7):
	probs = []
	for i in range(tamanho):
		probs.append(poisson.pmf(i,media))
	probs.append(1-sum(probs))
	return pd.Series(probs, index = lista07)

def ProbabilidadesPartida(selecao1, selecao2):
    l1, l2 = MediasPoisson(selecao1, selecao2)
    d1, d2 = Distribuicao(l1), Distribuicao(l2)  
    matriz = np.outer(d1, d2)    #   Monta a matriz de probabilidades

    vitoria = np.tril(matriz).sum()-np.trace(matriz)    #Soma a triangulo inferior
    derrota = np.triu(matriz).sum()-np.trace(matriz)    #Soma a triangulo superior
    probs = np.around([vitoria, 1-(vitoria+derrota), derrota], 3)
    probsp = [f'{100*i:.1f}%' for i in probs]

    nomes = ['0', '1', '2', '3', '4', '5', '6', '7+']
    matriz = pd.DataFrame(matriz, columns = nomes, index = nomes)
    matriz.index = pd.MultiIndex.from_product([[selecao1], matriz.index])
    matriz.columns = pd.MultiIndex.from_product([[selecao2], matriz.columns]) 
    output = {'seleção1': selecao1, 'seleção2': selecao2, 
             'f1': forca[selecao1], 'f2': forca[selecao2], 
             'media1': l1, 'media2': l2, 
             'probabilidades': probsp, 'matriz': matriz}
    return output

def Pontos(gols1, gols2):
    rst = Resultado(gols1, gols2)
    if rst == 'V':
        pontos1, pontos2 = 3, 0
    if rst == 'E':
        pontos1, pontos2 = 1, 1
    if rst == 'D':
        pontos1, pontos2 = 0, 3
    return pontos1, pontos2, rst

def format_percentage(val):
            return f'{val:.2f}%'
        

def Jogo(selecao1, selecao2):
    l1, l2 = MediasPoisson(selecao1, selecao2)
    gols1 = int(np.random.poisson(lam = l1, size = 1))
    gols2 = int(np.random.poisson(lam = l2, size = 1))
    saldo1 = gols1 - gols2
    saldo2 = -saldo1
    pontos1, pontos2, result = Pontos(gols1, gols2)
    placar = '{}x{}'.format(gols1, gols2)
    return [gols1, gols2, saldo1, saldo2, pontos1, pontos2, result, placar]


listaselecoes = selecoes.index.tolist()
listaselecoes.sort()
listaselecoes2 = listaselecoes.copy()

######## COMEÇO DO APP
st.markdown("# 🏆 Copa do Mundo Feminino 2023") 

paginas = ['Partidas', 'Tabelas']
pagina = st.sidebar.radio('Selecione a página', paginas)

if pagina == 'Partidas':
    st.markdown('---')
    st.markdown("<h2 style='text-align: center; color: #0f54c9; font-size: 40px;'>Probabilidades dos Jogos<br>  </h1>", unsafe_allow_html=True)
    st.markdown('---')
    tipojogo = st.radio('Escolha o tipo de jogo', ['Jogo da Fase de Grupos', 'Jogo do Mata-Mata'])
    
    st.markdown('---')
    j1, j2 = st.columns (2)
    selecao1 = j1.selectbox('--- Escolha a primeira Seleção ---', listaselecoes) 
    listaselecoes2.remove(selecao1)
    selecao2 = j2.selectbox('--- Escolha a segunda Seleção ---', listaselecoes2, index = 1)
    
    st.markdown('---') 
    jogo = ProbabilidadesPartida(selecao1, selecao2)
    prob = jogo['probabilidades']
    matriz = jogo['matriz']    
    
    if tipojogo == 'Jogo da Fase de Grupos':
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.image(selecoes.loc[selecao1, 'LinkBandeiraGrande']) 
            col2.markdown(f"<h5 style='text-align: center; color: #1a1a1a; font-weight: bold; font-size: 25px;'>{selecao1}<br>  </h1>", unsafe_allow_html=True)
            col2.markdown(f"<h2 style='text-align: center; color: #0f54c9; font-weight: bold; font-size: 50px;'>{prob[0]}<br>  </h1>", unsafe_allow_html=True)
            col3.markdown(f"<h2 style='text-align: center; color: #6a6a6b; font-weight: 100; font-size: 15px;'>Empate<br>  </h1>", unsafe_allow_html=True)
            col3.markdown(f"<h2 style='text-align: center; color: #6a6a6b;                    font-size: 30px;'>{prob[1]}<br>  </h1>", unsafe_allow_html=True)
            col4.markdown(f"<h5 style='text-align: center; color: #1a1a1a; font-weight: bold; font-size: 25px;'>{selecao2}<br>  </h1>", unsafe_allow_html=True) 
            col4.markdown(f"<h2 style='text-align: center; color: #0f54c9; font-weight: bold; font-size: 50px;'>{prob[2]}<br>  </h1>", unsafe_allow_html=True) 
            col5.image(selecoes.loc[selecao2, 'LinkBandeiraGrande'])
    
    if tipojogo == 'Jogo do Mata-Mata':
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.image(selecoes.loc[selecao1, 'LinkBandeiraGrande']) 
            col2.markdown(f"<h5 style='text-align: center; color: #1a1a1a; font-weight: bold; font-size: 25px;'>{selecao1}<br>  </h1>", unsafe_allow_html=True)
            aux1 = round(float(prob[0][:-1])+float(prob[1][:-1])/2, 1)
            aux2 = str(aux1) + '%' 
            col2.markdown(f"<h2 style='text-align: center; color: #0f54c9; font-weight: bold; font-size: 50px;'>{aux2}<br>  </h1>", unsafe_allow_html=True)
            col3.markdown(f"<h2 style='text-align: center; color: #6a6a6b; font-weight: 100; font-size: 15px;'> <br>  </h1>", unsafe_allow_html=True)
            col3.markdown(f"<h2 style='text-align: center; color: #6a6a6b;                    font-size: 30px;'>vs<br>  </h1>", unsafe_allow_html=True)
            col4.markdown(f"<h5 style='text-align: center; color: #1a1a1a; font-weight: bold; font-size: 25px;'>{selecao2}<br>  </h1>", unsafe_allow_html=True) 
            aux3 = round(100 - aux1, 1)
            aux4 = str(aux3) + '%' 
            col4.markdown(f"<h2 style='text-align: center; color: #0f54c9; font-weight: bold; font-size: 50px;'>{aux4}<br>  </h1>", unsafe_allow_html=True) 
            col5.image(selecoes.loc[selecao2, 'LinkBandeiraGrande'])

    st.markdown('---')

    def aux(x):
        return f'{str(round(100*x,1))}%'

    fig, ax = plt.subplots()
    sns.heatmap(matriz.reset_index(drop=True), ax=ax, cmap = 'Blues', annot = 100*matriz , fmt=".2f", xticklabels = lista07, yticklabels = lista07) 
    ax.tick_params(axis='both', which='major', labelsize=10, labelbottom = False, bottom=False, top = True, labeltop=True )
    ax.xaxis.set_label_position('top')
    ax.set_xlabel('Gols ' + selecao2, fontsize=15, color = 'gray')	
    ax.set_ylabel('Gols ' + selecao1, fontsize=15, color = 'gray')	
    ax.set_xticklabels(ax.get_xticklabels(), rotation = 0, fontsize = 8, color = 'gray')
    ax.set_yticklabels(ax.get_yticklabels(), rotation = 0, fontsize = 8, color = 'gray' )


    st.markdown("<h2 style='text-align: center; color: #0f54c9; font-size: 40px;'> Probabilidades dos Placares<br>  </h1>", unsafe_allow_html=True) 
    st.write(fig)

    st.markdown('---')

    placar = np.unravel_index(np.argmax(matriz, axis=None), matriz.shape) 

    st.markdown("<h2 style='text-align: center; color: #0f54c9; font-size: 40px;'> Placar Mais Provável<br>  </h1>", unsafe_allow_html=True)
        
    st.markdown(' ')

    col1, col2, col3 = st.columns([1,5,1])
    col1.image(selecoes.loc[selecao1, 'LinkBandeiraGrande']) 
    
    col2.markdown(f"<h2 style='text-align: center; color: #1a1a1a; font-size: 40px;'>{selecao1} {placar[0]}x{placar[1]} {selecao2}<br>  </h1>", unsafe_allow_html=True)

    col3.image(selecoes.loc[selecao2, 'LinkBandeiraGrande'])  
    st.markdown('---')
    
if pagina == 'Tabelas':
    
    dados1=pd.read_excel('dados/outputSimulaçõesCopaDoMundo.xlsx')
    dados2=pd.read_excel('dados/outputProbabilidadesPorEtapa.xlsx')
    dados3=pd.read_excel('dados/outputAvançoPorEtapa.xlsx')
    dados4=pd.read_excel('dados/outputSimulaçõesPossiveis_finais.xlsx')
    dados5=pd.read_excel('dados/outputEstimativasJogosCopa.xlsx')
         
    atualizacoes = ['Dados das Seleções', 
                    'Simulações da Copa', 
                    'Probabilidades por Etapa',
                    'Avanço por Etapa',
                    'Probabilidades Finais',
                    'Tabela de Jogos',
                    'Vencedores']
    
    a = st.radio('Selecione a Atualização', atualizacoes) 
    
    if a == 'Dados das Seleções':
        st.write(selecoes)
		
    elif a == 'Simulações da Copa':     
        st.write(dados1)  
        
    elif a == 'Probabilidades por Etapa':
        st.write(dados2)  
        
    elif a == 'Probabilidades Finais':
        st.write(dados4) 
        
    elif a == 'Avanço por Etapa':
        st.write(dados3) 
        
    elif a == 'Tabela de Jogos':
        st.write(dados5[['grupo', 'seleção1', 'Vitória', 'Empate', 'Derrota','seleção2']])  
        #st.write(dados5) 
        
    elif a == 'Vencedores':        
        
        times_vencedores = dados[dados['Copas'] > 0]
        contagem_copas = times_vencedores.groupby('Seleção')['Copas'].sum().reset_index()
        contagem_copas.rename(columns={'Copas': 'Quantidade de Troféus'}, inplace=True)
        contagem_copas = contagem_copas.sort_values(by='Quantidade de Troféus', ascending=False)
        st.title('Quantidade de Troféus de Copa do Mundo')  
        st.table(contagem_copas) 
        
    
    
    


