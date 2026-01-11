import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Controle de Estacionamento", page_icon="🚗", layout="wide")

st.title("🚗 Sistema de Estacionamento Profissional")

# Conexão com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Lendo os dados atuais para calcular vagas
df_atual = conn.read(ttl=0)
vagas_totais = 50
vagas_ocupadas = len(df_atual)
vagas_disponiveis = vagas_totais - vagas_ocupadas

# Exibição das vagas no topo
col1, col2 = st.columns(2)
col1.metric("Vagas Disponíveis", vagas_disponiveis)
col2.metric("Vagas Ocupadas", vagas_ocupadas)

aba1, aba2, aba3 = st.tabs(["📥 Entrada", "📤 Saída", "📊 Histórico do Dia"])

with aba1:
    st.header("Novo Cadastro")
    
    with st.form("form_entrada", clear_on_submit=True):
        nome = st.text_input("Nome do Condutor")
        whatsapp = st.text_input("WhatsApp (com DDD)")
        veiculo_tipo = st.selectbox("Tipo de Veículo", ["Carro", "Moto"])
        placa = st.text_input("Placa do Veículo")
        cor = st.text_input("Cor do Veículo")
        modelo = st.text_input("Modelo do Veículo")
        hora_entrada = st.time_input("Hora da Entrada", datetime.now())

        if st.form_submit_button("Confirmar Entrada"):
            if nome and placa:
                # Criar nova linha de dados
                nova_linha = pd.DataFrame([{
                    "Nome": nome,
                    "WhatsApp": whatsapp,
                    "Tipo": veiculo_tipo,
                    "Placa": placa,
                    "Cor": cor,
                    "Modelo": modelo,
                    "Entrada": hora_entrada.strftime("%H:%M"),
                    "Data": datetime.now().strftime("%d/%m/%Y")
                }])
                
                # Adicionar aos dados existentes
                df_final = pd.concat([df_atual, nova_linha], ignore_index=True)
                
                # Atualizar a planilha
                conn.update(data=df_final)
                
                # AVISO DE SUCESSO E BALÕES
                st.success(f"✅ Entrada de {nome} (Placa: {placa}) confirmada!")
                st.balloons()
                st.rerun()
            else:
                st.error("Por favor, preencha pelo menos o Nome e a Placa.")

with aba2:
    st.header("Registrar Saída")
    if not df_atual.empty:
        veiculo_para_saida = st.selectbox("Selecione o veículo pela Placa", df_atual["Placa"].tolist())
        if st.button("Confirmar Saída"):
            df_pos_saida = df_atual[df_atual["Placa"] != veiculo_para_saida]
            conn.update(data=df_pos_saida)
            st.warning(f"Saída de {veiculo_para_saida} registrada!")
            st.rerun()
    else:
        st.info("Nenhum veículo no pátio.")

with aba3:
    st.header("Veículos no Pátio")
    st.dataframe(df_atual)
