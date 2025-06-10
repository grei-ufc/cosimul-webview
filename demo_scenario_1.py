# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
# biblioteca
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime,time
from PIL import Image

def processar_dados():
    csv_path = "dataset_des1/results.csv"
    hdf5_path = "results_1.h5"
    
    try:
        # Tenta ler o CSV
        df = pd.read_csv(csv_path)
        print("CSV encontrado. Convertendo para HDF5...")
        
        # Salva como HDF5 (sobrescreve se existir)
        df.to_hdf(
            hdf5_path,
            key="dataset_to_sc1",
            mode="w",
            format="table"
        )
        
    except FileNotFoundError:
        print("CSV não encontrado. Lendo diretamente do HDF5...")
        try:
            # Tenta ler o HDF5 existente
            df = pd.read_hdf(hdf5_path, key="dataset_to_sc1")
        except Exception as e:
            print(f"Erro ao ler HDF5: {str(e)}")
            return None
            
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        return None
        
    return df

# Uso
df = processar_dados()
if df is not None:
    print("Dados carregados com sucesso!")
else:
    print("Não foi possível carregar os dados.")



df = pd.read_csv('dataset_des1/results.csv')




df1 = df.copy()
#Convertendo date para Datetime
df1[['Data','Hora']] = df1['date'].str.split(' ',expand=True)
df1['Data'] = pd.to_datetime(df1['Data']).dt.strftime('%d-%m-%Y')
df1['date'] = pd.to_datetime(df1['date'])





#============================================
#            BARRA LATERAL STREAMIT LIT
#===========================================
st.header('Mosaik')
st.header('Análise de dados para Cenário 1')

#image_path = 'imagens/Grei2.png'
image = Image.open( 'Grei2.png' )
st.sidebar.image(image, width=160)


st.sidebar.markdown('# Filtros')
st.sidebar.markdown("""---""")

# Converter para datetime.datetime
min_time = time(4, 0, 0)   # 04:00:00
max_time = time(19, 59, 0) # 19:59:00

# Slider apenas para horários
start_time, end_time = st.sidebar.slider(
    'Selecione um intervalo',
    min_value=min_time,
    max_value=max_time,
    value=(min_time,max_time),  # Horário inicial
    format="HH:mm:ss"
)

# Criando um datetime com a data fixa
start_datetime = datetime(2021, 5, 21, start_time.hour, start_time.minute, start_time.second)
end_datetime = datetime(2021, 5, 21, end_time.hour, end_time.minute, end_time.second)


st.write("Horário start:", start_datetime)
st.write("Horário end:", end_datetime)

linha_selecionada = ((df1['date'] <= end_datetime) & (df1['date'] >= start_datetime ))
df1= df1.loc[linha_selecionada,:]
#st.dataframe(df1)

# ============================================
#           LAYOUT STREAMLIT
#=============================================
tab1,tab2,tab3 = st.tabs(['Cenário 1','-','-'])
with tab1:
    with st.container():
        st.title('Informações relevantes:')
        col1,col2,col3,col4 = st.columns(4, gap='small')

        with col1:
            col1.metric('Média de PV-gen:','{:.3f}'.format(df1.loc[:,'PV-0.PV_0-P_gen'].mean()))
        with col2:
            col2.metric('Média do Controlador:','{:.3f}'.format(df1.loc[:,'PV-0.PV_0-mod'].mean()))
        with col3:
            col3.metric('Média da carga:','{:.3f}'.format(df1.loc[:,'Grid-0.0-Bus R17-p_mw'].mean()))
        with col4:
            col4.metric('Média de tensão:','{:.3f}'.format(df1.loc[:,'Grid-0.0-Bus R17-vm_pu'].mean()))
            
    with st.container():
        col1,col2 = st.columns(2)
        
        with col1:
            df2=df1.copy()
            df2_n = df2.loc[:,['Grid-0.0-Bus R17-p_mw','date']].groupby(['Grid-0.0-Bus R17-p_mw','date']).count().sort_values(['date'],ascending=True).reset_index()
            # Criando o gráfico de linha
            fig = px.line(df2_n, x="date", y="Grid-0.0-Bus R17-p_mw", title="Gráfico de Grid-0.0-Bus R17-p_mw ao Longo do Tempo")
            
            # Ajustando o eixo X para exibir horários a cada 180 minutos
            horarios_marcados = df2_n["date"][::180]  # Pegando os horários a cada 180 minutos
            fig.update_layout(
                xaxis=dict(
                    tickmode="array",
                    tickvals=horarios_marcados,  # Define os valores dos ticks
                    ticktext=horarios_marcados.dt.strftime("%H:%M"),  # Formata para exibir apenas a hora
                    showgrid=True
                ),
                xaxis_title="Horas",
                yaxis_title="Valor"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            df_g = df1.loc[:,['PV-0.PV_0-P_gen','date']].groupby('date').sum().reset_index()
            fig = px.line(df_g, x='date', y='PV-0.PV_0-P_gen', title='Gráfico de Geração foto-voltaica ao Longo do Tempo')

            horarios= df_g['date'][::180]
            fig.update_layout(
                xaxis=dict(
                    tickmode='array',
                    tickvals=horarios,
                    ticktext=horarios.dt.strftime('%H:%M'),
                    showgrid=True
                ),
                xaxis_title='Horas',
                yaxis_title='Valor'
            )
            st.plotly_chart(fig, use_container_width=True)

    with st.container():
        df_mod = df1.loc[:,['PV-0.PV_0-mod','date']].groupby('date').sum().reset_index()
        fig = px.line(df_mod, x='date', y='PV-0.PV_0-mod')
        horarios= df_mod['date'][::180]
        fig.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=horarios,
                ticktext=horarios.dt.strftime('%H:%M'),
                showgrid=True,
            ),
        title={
                'x':0.5,
                'text':'Gráfico de PV-0.PV_0-mod ao Longo do Tempo - Atuação do Controlador',
                'xanchor': 'center',
        },
            xaxis_title='Horas',
            yaxis_title='Valor'
        )
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1,col2 = st.columns(2)
        with col1:
            #df1['date'] = pd.to_datetime(df1['date'])  # Garantindo que 'date' seja datetime
            
            # Criando a figura e o eixo
            fig, ax = plt.subplots()            
            # Plotando a tensão no barramento
            sns.lineplot(x=df1['date'], y=df1['Grid-0.0-Bus R17-p_mw'], label="Carga", color="blue", linewidth=2, ax=ax)
            
            # Plotando a geração fotovoltaica
            sns.lineplot(x=df1['date'], y=df1['Grid-0.0-Bus R17-vm_pu'], label="Tensão", color="red", linewidth=2, ax=ax)
            
            # Configuração do eixo X para exibir horários a cada 3 horas
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=3))  
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            
            # Personalização do gráfico
            ax.set_xlabel("Horário")
            ax.set_ylabel("Valores")
            ax.set_title("Comparação entre Carga e Tensão")
            ax.legend()
            plt.xticks(rotation=45)
            plt.grid(True)
            
            # Exibindo no Streamlit
            st.pyplot(fig,use_container_width=True)

        with col2:
            #st.markdown("##### Comparação entre Tensão no Barramento e Geração Fotovoltaica")
            fig, ax = plt.subplots()            
            # Plotando a tensão no barramento
            sns.lineplot(x=df1['date'], y=df1['Grid-0.0-Bus R17-p_mw'], label="Carga", color="blue", linewidth=2, ax=ax)
            
            # Plotando a geração fotovoltaica
            sns.lineplot(x=df1['date'], y=df1['PV-0.PV_0-P_gen'], label="Geração Fotovoltaica", color="red", linewidth=2, ax=ax)
            
            # Configuração do eixo X para exibir horários a cada 3 horas
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=3))  
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            
            # Personalização do gráfico
            ax.set_xlabel("Horário")
            ax.set_ylabel("Valores")
            ax.set_title("Comparação entre Carga e Geração Fotovoltaica")
            ax.legend()
            plt.xticks(rotation=45)
            plt.grid(True)
            
            # Exibindo no Streamlit
            st.pyplot(fig,use_container_width=True)

    with st.container():
        #st.markdown("#### Comparação entre Controlador e Geração Fotovoltaica")
        fig, ax = plt.subplots(figsize=(12,5))  
        ax.fill_between(df1['date'], df1['PV-0.PV_0-P_gen'], alpha=0.5, label="Geração FV")
        ax.plot(df1['date'], df1['Grid-0.0-Bus R17-p_mw'], label="Controlador", color='red')
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=3))  # Marca de 3 em 3 horas
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.set_xlabel("Horário")
        ax.set_ylabel("Valores")
        ax.set_title("Comparação entre Controlador e Geração Fotovoltaica")
        ax.legend()
        ax.grid(True)
        
        # Exibindo o gráfico no Streamlit
        st.pyplot(fig, use_container_width=True)




        
        

    
