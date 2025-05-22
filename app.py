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

elif seccion == "Comparativa contra el índice":
    st.title("📉 Comparación con el índice S&P 500")

elif seccion == "Monte Carlo":
    st.title("🎲 Simulación Monte Carlo de precios")

elif seccion == "Medias móviles":
    st.title("📊 Análisis de medias móviles")

elif seccion == "Cartera Eficiente":
    st.title("📊 Análisis de portafolio con CAPM y Frontera Eficiente")
    symbols = st.text_input("Ingresa hasta 4 tickers separados por comas (ejemplo: AAPL, MSFT, TSLA, AMZN)", "AAPL, MSFT, TSLA").upper().split(",")
    symbols = [s.strip() for s in symbols if s.strip() != ""]

    if 2 <= len(symbols) <= 4:
        try:
            raw_data = yf.download(symbols, period="5y", interval="1d", group_by='ticker', auto_adjust=False)

            if isinstance(raw_data.columns, pd.MultiIndex):
                prices = pd.DataFrame({ticker: raw_data[ticker]['Adj Close'] for ticker in symbols})
                prices = prices.dropna()
            else:
                if "Adj Close" in raw_data.columns:
                    prices = raw_data["Adj Close"].to_frame()
                else:
                    st.error("No se encontró la columna 'Adj Close'.")
                    st.stop()

            returns = np.log(prices / prices.shift(1)).dropna()
            mean_returns = returns.mean() * 252
            cov_matrix = returns.cov() * 252

            def portfolio_performance(weights, mean_returns, cov_matrix):
                returns = np.dot(weights, mean_returns)
                std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                return std, returns

            def negative_sharpe_ratio(weights, mean_returns, cov_matrix, risk_free_rate=0.02):
                std, returns = portfolio_performance(weights, mean_returns, cov_matrix)
                return -(returns - risk_free_rate) / std

            def check_sum(weights):
                return np.sum(weights) - 1

            num_assets = len(symbols)
            bounds = tuple((0, 1) for _ in range(num_assets))
            initial_weights = [1. / num_assets] * num_assets

            opt = minimize(negative_sharpe_ratio, initial_weights,
                           args=(mean_returns, cov_matrix),
                           method="SLSQP", bounds=bounds, constraints={'type': 'eq', 'fun': check_sum})

            opt_weights = opt.x
            opt_std, opt_return = portfolio_performance(opt_weights, mean_returns, cov_matrix)

            st.write(f"**Sharpe Óptimo:** {(opt_return - 0.02)/opt_std:.2f}")
            st.write("**Pesos del portafolio óptimo:**")
            st.dataframe(pd.DataFrame({"Ticker": symbols, "Peso": opt_weights}))

            num_portfolios = 5000
            rets, stds, sharpes = [], [], []

            for _ in range(num_portfolios):
                weights = np.random.random(num_assets)
                weights /= np.sum(weights)
                std, ret = portfolio_performance(weights, mean_returns, cov_matrix)
                stds.append(std)
                rets.append(ret)
                sharpes.append((ret - 0.02) / std)

            fig3, ax3 = plt.subplots()
            scatter = ax3.scatter(stds, rets, c=sharpes, cmap='viridis')
            ax3.scatter(opt_std, opt_return, c='red', marker='*', s=200, label='Óptimo Sharpe')
            ax3.set_title('Frontera Eficiente')
            ax3.set_xlabel('Riesgo (Volatilidad)')
            ax3.set_ylabel('Retorno Esperado')
            ax3.legend()
            plt.colorbar(scatter, label='Sharpe Ratio')
            st.pyplot(fig3)

            st.download_button("⬇️ Descargar precios del portafolio en CSV", prices.to_csv().encode('utf-8'), file_name="portafolio_precios.csv", mime='text/csv')

        except Exception as e:
            st.error(f"Error al descargar datos o calcular: {e}")

    elif len(symbols) < 2:
        st.info("Por favor, ingresa al menos 2 tickers.")
    elif len(symbols) > 4:
        st.warning("El análisis está limitado a un máximo de 4 activos.")

elif seccion == "Creator de sector ETFs":
    st.title("💼 ETFs por sector")
