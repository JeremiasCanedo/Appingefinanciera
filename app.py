import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from scipy.optimize import minimize

st.set_page_config(page_title="App IngeFinanciera", layout="wide")

st.title("🔍 Información General y Medias Móviles")

ticker = st.text_input("Ingresa el ticker bursátil (por ejemplo, AAPL):", value="AAPL").upper()

if ticker:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        st.subheader("📊 Información de la empresa")
        st.write(f"**Nombre:** {info.get('shortName', 'N/A')}")
        st.write(f"**Sector:** {info.get('sector', 'N/A')}")
        st.write(f"**Industria:** {info.get('industry', 'N/A')}")
        st.write(f"**Descripción:** {info.get('longBusinessSummary', 'No disponible')}")
        st.write(f"**Beta:** {info.get('beta', 'N/A')}")
        st.write(f"**Forward PE:** {info.get('forwardPE', 'N/A')}")
        st.write(f"**Price to Book:** {info.get('priceToBook', 'N/A')}")
        st.write(f"**Market Cap:** {info.get('marketCap', 'N/A')}")

        with st.spinner("Descargando datos históricos..."):
            df = stock.history(period="1y")

        if df.empty:
            st.error("No se encontraron datos históricos para este ticker.")
        else:
            df['SMA50'] = df['Close'].rolling(window=50).mean()
            df['SMA100'] = df['Close'].rolling(window=100).mean()
            df['SMA200'] = df['Close'].rolling(window=200).mean()
            df['Upper Band'] = df['Close'].rolling(window=20).mean() + 2 * df['Close'].rolling(window=20).std()
            df['Lower Band'] = df['Close'].rolling(window=20).mean() - 2 * df['Close'].rolling(window=20).std()

            # Indicadores técnicos adicionales
            df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
            df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

            delta = df['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(window=14).mean()
            loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))

            # Gráfico principal con plotly
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Precio de Cierre'))
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], mode='lines', name='SMA 50 días'))
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA100'], mode='lines', name='SMA 100 días'))
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA200'], mode='lines', name='SMA 200 días'))
            fig.add_trace(go.Scatter(x=df.index, y=df['Upper Band'], mode='lines', name='Banda Superior', line=dict(dash='dot', color='gray')))
            fig.add_trace(go.Scatter(x=df.index, y=df['Lower Band'], mode='lines', name='Banda Inferior', line=dict(dash='dot', color='gray')))
            fig.update_layout(title=f"Medias móviles y Bandas de Bollinger - {ticker}", xaxis_title="Fecha", yaxis_title="Precio ($)", legend_title="Indicadores", hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

            # MACD y Señal
            st.subheader("📉 MACD y Señal")
            fig_macd = go.Figure()
            fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', name='MACD', line=dict(color='blue')))
            fig_macd.add_trace(go.Scatter(x=df.index, y=df['Signal'], mode='lines', name='Señal', line=dict(color='red')))
            fig_macd.update_layout(title="MACD vs Señal", xaxis_title="Fecha", yaxis_title="Valor", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig_macd, use_container_width=True)

            # RSI
            st.subheader("📈 RSI (Relative Strength Index)")
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], mode='lines', name='RSI', line=dict(color='purple')))
            fig_rsi.add_hline(y=70, line=dict(color='red', dash='dash'))
            fig_rsi.add_hline(y=30, line=dict(color='green', dash='dash'))
            fig_rsi.update_layout(title="RSI", xaxis_title="Fecha", yaxis_title="Valor", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig_rsi, use_container_width=True)

            # Conclusión
            st.subheader("📌 Conclusión Técnica")
            conclusiones = []
            if df['RSI'].iloc[-1] > 70:
                conclusiones.append("El RSI está por encima de 70: posible sobrecompra.")
            elif df['RSI'].iloc[-1] < 30:
                conclusiones.append("El RSI está por debajo de 30: posible sobreventa.")
            if df['MACD'].iloc[-1] > df['Signal'].iloc[-1]:
                conclusiones.append("MACD está por encima de la señal: tendencia alcista.")
            elif df['MACD'].iloc[-1] < df['Signal'].iloc[-1]:
                conclusiones.append("MACD está por debajo de la señal: tendencia bajista.")
            if not conclusiones:
                conclusiones.append("No se detectan señales claras actualmente.")
            for conclusion in conclusiones:
                st.markdown(f"- {conclusion}")

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
