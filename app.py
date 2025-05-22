import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

st.set_page_config(page_title="App IngeFinanciera", layout="wide")
st.sidebar.title("📊 Herramientas")
seccion = st.sidebar.radio("Selecciona una sección:", [
    "Información general",
    "Análisis Estadístico",
    "Comparativa contra el índice",
    "Monte Carlo",
    "Medias móviles",
    "Cartera Eficiente",
    "Creator de sector ETFs"
])

if seccion == "Información general":
    st.title("🔍 Análisis individual de una acción")
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
                df = stock.history(period="5y")

            if df.empty:
                st.error("No se encontraron datos históricos para este ticker.")
            else:
                st.subheader("📈 Precio histórico")
                fig, ax = plt.subplots()
                ax.plot(df.index, df['Close'], label="Cierre")
                ax.set_title(f"{ticker} - Precio de cierre ajustado")
                ax.set_xlabel("Fecha")
                ax.set_ylabel("Precio ($)")
                ax.legend()
                st.pyplot(fig)

                df['Daily Return'] = df['Close'].pct_change()

                st.subheader("📈 Rendimientos anualizados")
                rendimientos = {}
                for years in [1, 3, 5]:
                    dias = 252 * years
                    if len(df) >= dias:
                        rendimiento = ((df['Close'].iloc[-1] / df['Close'].iloc[-dias]) ** (1/years)) - 1
                        rendimientos[f"{years} años"] = rendimiento

                st.dataframe(pd.DataFrame.from_dict(rendimientos, orient='index', columns=['Rendimiento anualizado']))

                st.subheader("📉 Volatilidad anualizada")
                std_daily = df['Daily Return'].std()
                vol_anual = std_daily * np.sqrt(252)
                st.write(f"**Volatilidad anualizada:** {vol_anual:.2%}")

                st.subheader("📊 Comparación con el S&P 500")
                try:
                    benchmark = yf.Ticker("^GSPC").history(period="5y")
                    if not benchmark.empty:
                        benchmark['Daily Return'] = benchmark['Close'].pct_change()
                        df = df.loc[df.index.intersection(benchmark.index)]
                        benchmark = benchmark.loc[benchmark.index.intersection(df.index)]

                        cumulative_returns = (1 + df['Daily Return']).cumprod() * 100
                        cumulative_benchmark = (1 + benchmark['Daily Return']).cumprod() * 100

                        fig2, ax2 = plt.subplots()
                        ax2.plot(df.index, cumulative_returns, label=ticker)
                        ax2.plot(df.index, cumulative_benchmark, label="S&P 500")
                        ax2.set_title("Comparación acumulada")
                        ax2.set_xlabel("Fecha")
                        ax2.set_ylabel("Valor acumulado ($)")
                        ax2.legend()
                        st.pyplot(fig2)

                        st.download_button("⬇️ Descargar datos históricos en CSV", df.to_csv().encode('utf-8'), file_name=f"{ticker}_datos_historicos.csv", mime='text/csv')
                    else:
                        st.warning("No se pudieron obtener datos del S&P 500.")
                except Exception as e:
                    st.warning("Error al comparar con el S&P 500")

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")

elif seccion == "Análisis Estadístico":
    st.title("📈 Análisis Estadístico de la acción")

    ticker = st.text_input("Ingresa el ticker bursátil para análisis estadístico:", value="AAPL").upper()
    if ticker:
        try:
            df = yf.download(ticker, period="2y")
            if df.empty:
                st.warning("No se encontraron datos para este ticker.")
            else:
                df['Daily Return'] = df['Close'].pct_change().dropna()
                st.subheader("🔢 Estadísticas descriptivas de los retornos diarios")
                st.write(df['Daily Return'].describe())

                st.subheader("📊 Histograma de retornos")
                fig1, ax1 = plt.subplots()
                ax1.hist(df['Daily Return'], bins=50, color='skyblue', edgecolor='black')
                ax1.set_title(f"Distribución de Retornos Diarios - {ticker}")
                ax1.set_xlabel("Retorno diario")
                ax1.set_ylabel("Frecuencia")
                st.pyplot(fig1)

                st.subheader("📈 Boxplot de retornos")
                fig2, ax2 = plt.subplots()
                ax2.boxplot(df['Daily Return'], vert=False)
                ax2.set_title("Boxplot de retornos diarios")
                st.pyplot(fig2)

                st.subheader("📉 Autocorrelación")
                autocorr = df['Daily Return'].autocorr(lag=1)
                st.write(f"Autocorrelación con lag 1: {autocorr:.3f}")

        except Exception as e:
            st.error(f"Error al obtener datos: {e}")

elif seccion == "Comparativa contra el índice":
    st.title("📉 Comparación con el índice S&P 500")

elif seccion == "Monte Carlo":
    st.title("🎲 Simulación Monte Carlo de precios")

    ticker = st.text_input("Ingresa el ticker para simular (ejemplo: AAPL):", value="AAPL").upper()
    if ticker:
        try:
            data = yf.download(ticker, period="1y")
            if data.empty:
                st.warning("No se pudo descargar la información de precios.")
            else:
                data['Returns'] = data['Close'].pct_change()
                last_price = data['Close'].iloc[-1]
                mu = data['Returns'].mean()
                sigma = data['Returns'].std()
                dias = st.slider("Días a simular", min_value=30, max_value=365, value=180)
                simulaciones = 1000

                resultados = np.zeros((dias, simulaciones))
                for i in range(simulaciones):
                    precios = [last_price]
                    for d in range(1, dias):
                        shock = np.random.normal(loc=mu, scale=sigma)
                        precios.append(precios[-1] * (1 + shock))
                    resultados[:, i] = precios

                st.subheader(f"📉 Simulación de {simulaciones} trayectorias para {dias} días")
                fig, ax = plt.subplots()
                ax.plot(resultados, linewidth=0.5, alpha=0.2)
                ax.set_title(f"Monte Carlo: {ticker}")
                ax.set_xlabel("Día")
                ax.set_ylabel("Precio simulado")
                st.pyplot(fig)

        except Exception as e:
            st.error(f"Error: {e}")

elif seccion == "Medias móviles":
    st.title("📊 Análisis de medias móviles")

    ticker = st.text_input("Ingresa el ticker para analizar (ejemplo: AAPL):", value="AAPL").upper()
    if ticker:
        try:
            df = yf.download(ticker, period="1y")
            if df.empty:
                st.warning("No se encontraron datos para este ticker.")
            else:
                df['SMA50'] = df['Close'].rolling(window=50).mean()
                df['SMA100'] = df['Close'].rolling(window=100).mean()
                df['SMA200'] = df['Close'].rolling(window=200).mean()

                df['Upper Band'] = df['Close'].rolling(window=20).mean() + 2 * df['Close'].rolling(window=20).std()
                df['Lower Band'] = df['Close'].rolling(window=20).mean() - 2 * df['Close'].rolling(window=20).std()

                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(df.index, df['Close'], label='Precio de Cierre', linewidth=1)
                ax.plot(df.index, df['SMA50'], label='SMA 50 días')
                ax.plot(df.index, df['SMA100'], label='SMA 100 días')
                ax.plot(df.index, df['SMA200'], label='SMA 200 días')
                ax.plot(df.index, df['Upper Band'], linestyle='--', color='gray', alpha=0.5, label='Banda superior')
                ax.plot(df.index, df['Lower Band'], linestyle='--', color='gray', alpha=0.5, label='Banda inferior')
                ax.fill_between(df.index, df['Upper Band'], df['Lower Band'], color='gray', alpha=0.1)
                ax.set_title(f"Medias móviles y Bandas de Bollinger - {ticker}")
                ax.set_xlabel("Fecha")
                ax.set_ylabel("Precio ($)")
                ax.legend()
                st.pyplot(fig)

        except Exception as e:
            st.error(f"Error al obtener datos: {e}")

elif seccion == "Cartera Eficiente":
    # (sin cambios aquí, ya está incluido en el estado actual)
    ...

elif seccion == "Creator de sector ETFs":
    st.title("💼 ETFs por sector")
