import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import ta

st.set_page_config(page_title="Análise de Ações BR", layout="wide")

st.title("📈 Análise Técnica de Ações da B3")
st.markdown("Escolha uma ação e veja os gráficos com Médias Móveis, RSI, MACD e Bandas de Bollinger.")

# Sidebar
ticker = st.sidebar.text_input("Código da Ação (ex: PETR4.SA)", value="PETR4.SA")
start_date = st.sidebar.date_input("Data Inicial", pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("Data Final", pd.to_datetime("today"))

# Baixar dados
@st.cache_data
def load_data(ticker, start, end):
    try:
        df = yf.download(ticker, start=start, end=end)
        if df.empty:
            return df

        close_prices = df['Close'].squeeze()  # Garante que é 1D

        df['SMA20'] = close_prices.rolling(window=20).mean()
        df['SMA50'] = close_prices.rolling(window=50).mean()

        rsi = ta.momentum.RSIIndicator(close=close_prices, window=14)
        df['RSI'] = rsi.rsi()

        macd = ta.trend.MACD(close=close_prices)
        df['MACD'] = macd.macd()
        df['MACD_signal'] = macd.macd_signal()

        bb = ta.volatility.BollingerBands(close=close_prices, window=20)
        df['BB_upper'] = bb.bollinger_hband()
        df['BB_lower'] = bb.bollinger_lband()

        df.dropna(inplace=True)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df = load_data(ticker, start_date, end_date)

# Verifica se dados foram carregados
if df.empty:
    st.warning("Não foi possível carregar os dados para esse ticker e período.")
    st.stop()

# Gráfico de Preço + Médias + Bandas
st.subheader(f"📊 Gráfico de Preço - {ticker}")
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(df.index, df['Close'], label='Fechamento', color='blue', alpha=0.6)
ax.plot(df.index, df['SMA20'], label='SMA 20', color='green')
ax.plot(df.index, df['SMA50'], label='SMA 50', color='red')
ax.plot(df.index, df['BB_upper'], label='Banda Superior', color='gray', linestyle='--', alpha=0.5)
ax.plot(df.index, df['BB_lower'], label='Banda Inferior', color='gray', linestyle='--', alpha=0.5)
ax.fill_between(df.index, df['BB_lower'], df['BB_upper'], color='gray', alpha=0.1)
ax.set_ylabel("Preço (R$)")
ax.set_xlabel("Data")
ax.legend()
st.pyplot(fig)

# Gráfico de RSI
st.subheader("📉 RSI - Índice de Força Relativa")
fig_rsi, ax_rsi = plt.subplots(figsize=(14, 2.5))
ax_rsi.plot(df.index, df['RSI'], label='RSI', color='purple')
ax_rsi.axhline(70, color='red', linestyle='--', label='Sobrecompra')
ax_rsi.axhline(30, color='green', linestyle='--', label='Sobrevenda')
ax_rsi.set_ylabel("RSI")
ax_rsi.legend()
st.pyplot(fig_rsi)

# Gráfico de MACD
st.subheader("📉 MACD - Convergência e Divergência de Médias")
fig_macd, ax_macd = plt.subplots(figsize=(14, 3))
ax_macd.plot(df.index, df['MACD'], label='MACD', color='orange')
ax_macd.plot(df.index, df['MACD_signal'], label='Sinal', color='blue')
ax_macd.axhline(0, color='black', linestyle='--', linewidth=1)
ax_macd.set_ylabel("MACD")
ax_macd.legend()
st.pyplot(fig_macd)

st.success("Pronto! Você pode trocar o ticker na barra lateral para ver outras ações da B3.")
