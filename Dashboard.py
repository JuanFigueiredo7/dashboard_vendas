import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide', page_title=':D')

def formata_numero(valor, prefixo =''):
    for unidade in ['','mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'

st.title('DASHBOARD DE VENDAS :shopping_trolley:')

url ='https://labdados.com/produtos'

regioes = ['Brasil','Centro-Oeste','Nordeste', 'Norte','Sudeste','Sul']
st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)
if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o ano', value=True)
if todos_anos:
    ano=''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao': regiao.lower(), 'ano':ano}
response = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

## tabelas

#tabelas de receitas
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra','lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending  = False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

### tabela de quantidade de vendas
# desafio aula 2

# Construir um gráfico de mapa com a quantidade de vendas por estado.
qtd_vendas_estado = dados.groupby('Local da compra')[['Preço']].count()
qtd_vendas_estado = dados.drop_duplicates(subset='Local da compra')[['Local da compra','lat', 'lon']].merge(qtd_vendas_estado, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending  = False)

#Construir um gráfico de linhas com a quantidade de vendas mensal.
qtd_vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='M'))['Preço'].count().reset_index()
qtd_vendas_mensal['Ano'] = qtd_vendas_mensal['Data da Compra'].dt.year
qtd_vendas_mensal['Mes'] = qtd_vendas_mensal['Data da Compra'].dt.month_name()

#Construir um gráfico de barras com os 5 estados com maior quantidade de vendas. 

#Construir um gráfico de barras com a quantidade de vendas por categoria de produto.

qtd_vendas_categoria = dados.groupby('Categoria do Produto')[['Preço']].count().sort_values('Preço',ascending=False)

# tabela vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum','count']))


## graficos

# gráfico de mapas
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope='south america',
                                  size='Preço',
                                  template='seaborn',
                                  hover_name='Local da compra',
                                  hover_data={'lat': False, 'lon':False},
                                  title = 'Receita por estado'
                                  )


fig_mapa_vendas_estado = px.scatter_geo(qtd_vendas_estado,
                            lat = 'lat',
                            lon = 'lon',
                            scope='south america',
                            size='Preço',
                            template='seaborn',
                            hover_name='Local da compra',
                            hover_data={'lat': False, 'lon':False},
                            title = 'Vendas por estado'
                            )

#grafico de linhas
fig_receita_mensal = px.line(receita_mensal,
                             x='Mes',
                             y='Preço',
                             markers=True,
                             range_y=(0,receita_mensal.max()),
                             color='Ano',
                             line_dash='Ano',
                             title='Receita Mensal'
                             )

fig_receita_mensal.update_layout(yaxis_title='Receita')

#gráfico de barras
fig_receita_estados = px.bar(receita_estados.head(5),
                             x='Local da compra',
                             y='Preço',
                             text_auto=True,
                             title='Top Estados (receita)'
                             )

fig_receita_estados.update_layout(yaxis_title='Receita')

fig_receita_categoria = px.bar(receita_categorias,
                               text_auto=True,
                               title='Receita por categoria')

fig_receita_categoria.update_layout(yaxis_title='Receita')




## Visualização no Streamlit
aba1, aba2, aba3 = st.tabs(['Receita','Quantidade de vendas', 'Vendedores'])

with aba1:

    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita: ', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
        st.plotly_chart(fig_receita_categoria, use_container_width=True)
    


with aba2:

    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita: ', formata_numero(dados['Preço'].sum(), 'R$'))

        st.plotly_chart(fig_mapa_vendas_estado)

        fig_vendas_top_estados = px.bar(qtd_vendas_estado.head(5),
                             x='Local da compra',
                             y='Preço',
                             text_auto=True,
                             title='Top Estados (Vendas)'
                             )

        fig_vendas_top_estados.update_layout(yaxis_title='Vendas')
        st.plotly_chart(fig_vendas_top_estados)



    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        fig_vendas_mensal = px.line(qtd_vendas_mensal,
                             x='Mes',
                             y='Preço',
                             markers=True,
                             range_y=(0,qtd_vendas_mensal.max()),
                             color='Ano',
                             line_dash='Ano',
                             title='Vendas Mensais'
                             )
        fig_vendas_mensal.update_layout(yaxis_title='Vendas')
        st.plotly_chart(fig_vendas_mensal)

        fig_qtd_vendas_categoria = px.bar(qtd_vendas_categoria,
                               text_auto=True,
                               title='Vendas por categoria')

        fig_qtd_vendas_categoria.update_layout(yaxis_title='Vendas', showlegend=False)
        st.plotly_chart(fig_qtd_vendas_categoria)


with aba3:
    qtd_vendedores = st.number_input('Quantidade de vendedores',2,10,5)

    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita: ', formata_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum',ascending=False).head(qtd_vendedores),
                                        x='sum',
                                        y=vendedores[['sum']].sort_values('sum',ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        title=f'Top {qtd_vendedores} vendedores (receita)')
        st.plotly_chart(fig_receita_vendedores)
    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count',ascending=False).head(qtd_vendedores),
                                        x='count',
                                        y=vendedores[['count']].sort_values('count',ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        title=f'Top {qtd_vendedores} vendedores (qtd de vendas)')
        st.plotly_chart(fig_vendas_vendedores)
