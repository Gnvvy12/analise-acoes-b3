import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import ta

st.set_page_config(page_title="Análise de Ações BR", layout="wide")

st.title("📈 Análise Técnica de Ações da B3")
st.markdown("Escolha uma ação e veja os gráficos com indicadores técnicos (SMA, RSI, MACD, Bollinger).")

# Sidebar
ticker = st.sidebar.text_input("Código da Ação (ex: PETR4.SA)", value="PETR4.SA")
start_date = st.sidebar.date_input("Data Inicial", pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("Data Final", pd.to_datetime("today"))

# Baixar dados
@st.cache_data
def load_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end)
    if df.empty:
        return df
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    
    # RSI
    rsi = ta.momentum.RSIIndicator(close=df['Close'], window=14)
    df['RSI'] = rsi.rsi()
    
    # MACD
    macd = ta.trend.MACD(close=df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    
    # Bollinger Bands
    bb = ta.volatility.BollingerBands(close=df['Close'], window=20)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()
    
    return df

df = load_data(ticker, start_date, end_date)

# Verificar se há dados
if df.empty:
    st.error("❌ Não foram encontrados dados para esse ticker ou período. Tente outro.")
    st.stop()

# Gráfico de Preço + Médias + Bollinger
st.subheader(f"Gráfico de Preço - {ticker}")
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(df.index, df['Close'], label='Fechamento', color='blue', alpha=0.6)
ax.plot(df.index, df['SMA20'], label='SMA 20', color='green')
ax.plot(df.index, df['SMA50'], label='SMA 50', color='red')
ax.fill_between(df.index, df['BB_upper'], df['BB_lower'], color='gray', alpha=0.2, label='Bandas de Bollinger')
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

# Gráfico de MACD
st.subheader("MACD - Convergência e Divergência de Médias")
fig_macd, ax_macd = plt.subplots(figsize=(14, 2.5))
ax_macd.plot(df.index, df['MACD'], label='MACD', color='blue')
ax_macd.plot(df.index, df['MACD_signal'], label='Sinal', color='orange')
ax_macd.axhline(0, color='gray', linestyle='--')
ax_macd.legend()
st.pyplot(fig_macd)

# Baixar dados
st.subheader("📥 Baixar dados")
csv = df.to_csv().encode('utf-8')
st.download_button(
    label="Download CSV",
    data=csv,
    file_name=f'{ticker}_analise.csv',
    mime='text/csv'
)

st.success("Análise completa! Você pode trocar o ticker na barra lateral para ver outros ativos da B3.")
