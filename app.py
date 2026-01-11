import streamlit as st
from datetime import datetime
import os

# --- 1. CONFIGURAÇÕES E CÁLCULO DE VAGAS ---
st.set_page_config(page_title="Controle de Estacionamento", page_icon="🚗")
TOTAL_VAGAS = 50

# Conta veículos no pátio para atualizar as vagas
if os.path.exists("vagas.csv"):
    with open("vagas.csv", "r", encoding="utf-8") as f:
        linhas_atuais = [line for line in f if line.strip()]
        vagas_ocupadas = len(linhas_atuais)
else:
    vagas_ocupadas = 0
    linhas_atuais = []

vagas_disponiveis = TOTAL_VAGAS - vagas_ocupadas

# --- 2. INTERFACE PRINCIPAL ---
st.title("🚗 Sistema de Estacionamento Profissional")

# Painel de Vagas
col_v1, col_v2 = st.columns(2)
col_v1.metric("Vagas Disponíveis", vagas_disponiveis)
col_v2.metric("Vagas Ocupadas", vagas_ocupadas)

if vagas_disponiveis <= 0:
    st.error("⚠️ ESTACIONAMENTO LOTADO!")

# Criação das Abas
aba1, aba2, aba3 = st.tabs(["📥 Entrada", "📤 Saída", "📊 Histórico do Dia"])

with aba1:
    st.header("Novo Cadastro")
    nome_condutor = st.text_input("Nome do Condutor")
    
    col1, col2 = st.columns(2)
    with col1:
        whatsapp = st.text_input("WhatsApp (com DDD)")
        email = st.text_input("E-mail")
    with col2:
        tipo_veiculo = st.selectbox("Tipo de Veículo", ["Moto", "Carro", "Carro Grande"])
        cor_veiculo = st.text_input("Cor do Veículo")

    col3, col4 = st.columns(2)
    with col3:
        nome_veiculo = st.text_input("Modelo do Veículo")
        placa_veiculo = st.text_input("Placa do Veículo")
    with col4:
        hora_entrada = st.time_input("Hora da Entrada", value=datetime.now().time())

    precos = {"Moto": 1.50, "Carro": 2.00, "Carro Grande": 3.00}
    valor_hora = precos[tipo_veiculo]
    
    st.info(f"💰 Tabela: {tipo_veiculo} - R$ {valor_hora:.2f}/hora")

    if st.button("Confirmar Entrada"):
        if vagas_disponiveis > 0:
            if nome_condutor and placa_veiculo:
                nova_linha = f"{nome_condutor};{whatsapp};{email};{tipo_veiculo};{nome_veiculo};{placa_veiculo};{cor_veiculo};{hora_entrada};{valor_hora}\n"
                with open("vagas.csv", "a", encoding="utf-8") as arquivo:
                    arquivo.write(nova_linha)
                st.success(f"✅ Veículo {placa_veiculo} registrado!")
                st.rerun()
            else:
                st.warning("Preencha o nome e a placa.")

with aba2:
    st.header("Processar Saída")
    if vagas_ocupadas > 0:
        dados_veiculos = [l.strip().split(";") for l in linhas_atuais]
        placas = [d[5] for d in dados_veiculos]
        escolha = st.selectbox("Selecione a Placa", placas)
        
        idx = placas.index(escolha)
        veiculo_sel = dados_veiculos[idx]
        
        hora_saida = st.time_input("Hora da Saída", value=datetime.now().time())
        
        # Cálculo
        h_ent_str = veiculo_sel[7]
        h_ent = datetime.strptime(h_ent_str.split('.')[0], "%H:%M:%S").time()
        inicio = datetime.combine(datetime.today(), h_ent)
        fim = datetime.combine(datetime.today(), hora_saida)
        minutos = max(0, (fim - inicio).total_seconds() / 60)
        
        v_hora = float(veiculo_sel[8])
        valor_pagar = 0.0 if minutos <= 15 else (minutos / 60) * v_hora

        st.warning(f"🕒 Permanência: {int(minutos)} min | **Valor: R$ {valor_pagar:.2f}**")

        if st.button("Finalizar Pagamento"):
            # 1. SALVA NO HISTÓRICO (Linha 89 aprox.)
            linha_hist = f"{veiculo_sel[5]};{veiculo_sel[7]};{hora_saida};{valor_pagar:.2f}\n"
            with open("historico.csv", "a", encoding="utf-8") as f_hist:
                f_hist.write(linha_hist)

            # 2. REMOVE DAS VAGAS ATUAIS
            novas_linhas = [l for l in linhas_atuais if escolha not in l]
            with open("vagas.csv", "w", encoding="utf-8") as f:
                f.writelines(novas_linhas)
            
            st.balloons()
            st.rerun()
    else:
        st.info("Nenhum veículo no pátio.")

with aba3:
    st.header("🏁 Veículos que Saíram")
    if os.path.exists("historico.csv"):
        with open("historico.csv", "r", encoding="utf-8") as f:
            vendas = f.readlines()
        
        if vendas:
            lista_saidas = []
            total_dia = 0.0
            for v in vendas:
                d = v.strip().split(";")
                total_dia += float(d[3])
                lista_saidas.append({"Placa": d[0], "Entrada": d[1], "Saída": d[2], "Pago": f"R$ {d[3]}"})
            
            st.metric("Faturamento Total", f"R$ {total_dia:.2f}")
            st.table(lista_saidas)
        else:
            st.info("Ainda não houve saídas hoje.")
    else:
        st.info("O histórico será criado após a primeira saída.")
