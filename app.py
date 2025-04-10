import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import ta

st.set_page_config(page_title="Análise de Ações BR", layout="wide")

st.title("📈 Análise Técnica de Ações da B3")
st.markdown("Escolha uma ação e veja os gráficos com médias móveis e RSI.")

# Sidebar
ticker = st.sidebar.text_input("Código da Ação (ex: PETR4.SA)", value="PETR4.SA")
start_date = st.sidebar.date_input("Data Inicial", pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("Data Final", pd.to_datetime("today"))

# Baixar dados
@st.cache_data
def load_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end)
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    rsi = ta.momentum.RSIIndicator(close=df['Close'], window=14)
    df['RSI'] = rsi.rsi()
    return df

df = load_data(ticker, start_date, end_date)

# Gráfico de Preço + Médias
st.subheader(f"Gráfico de Preço - {ticker}")
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(df.index, df['Close'], label='Fechamento', color='blue', alpha=0.6)
ax.plot(df.index, df['SMA20'], label='SMA 20', color='green')
ax.plot(df.index, df['SMA50'], label='SMA 50', color='red')
ax.set_ylabel("Preço (R$)")
ax.set_xlabel("Data")
ax.legend()
st.pyplot(fig)

# Gráfico de RSI
st.subheader("RSI - Índice de Força Relativa")
fig_rsi, ax_rsi = plt.subplots(figsize=(14, 2.5))
ax_rsi.plot(df.index, df['RSI'], label='RSI', color='purple')
ax_rsi.axhline(70, color='red', linestyle='--')
ax_rsi.axhline(30, color='green', linestyle='--')
ax_rsi.set_ylabel("RSI")
ax_rsi.legend()
st.pyplot(fig_rsi)

st.success("Pronto! Você pode trocar o ticker na barra lateral para ver outras ações da B3.")
