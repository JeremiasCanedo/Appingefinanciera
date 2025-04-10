import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="App IngeFinanciera", layout="centered")
st.title("📈 App IngeFinanciera")

# Entrada de ticker
ticker = st.text_input("Ingresa el ticker bursátil (por ejemplo, AAPL):").upper()

if ticker:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Mostrar información básica
        st.subheader("📊 Información de la empresa")
        st.markdown("""
        Esta sección presenta información general sobre la empresa asociada al ticker ingresado, como su nombre, sector económico y una breve descripción de su actividad.
        """)
        st.write(f"**Nombre:** {info.get('shortName', 'N/A')}")
        st.write(f"**Sector:** {info.get('sector', 'N/A')}")
        st.write(f"**Descripción:** {info.get('longBusinessSummary', 'No disponible')}")

        # Descargar precios históricos (últimos 5 años)
        df = stock.history(period="5y")

        if df.empty:
            st.error("No se encontraron datos históricos para este ticker.")
        else:
            # Mostrar gráfica de precios
            st.subheader("📈 Precio de cierre ajustado (últimos 5 años)")
            st.markdown("""
            A continuación se muestra una gráfica con la evolución del precio de cierre ajustado de la acción durante los últimos cinco años.
            Esto permite analizar tendencias generales del comportamiento del activo.
            """)
            fig, ax = plt.subplots()
            ax.plot(df.index, df["Close"], label="Precio de cierre")
            ax.set_xlabel("Fecha")
            ax.set_ylabel("Precio ($)")
            ax.set_title(f"{ticker} - Precio histórico")
            ax.legend()
            st.pyplot(fig)

            # Calcular rendimientos anuales acumulados
            st.subheader("📈 Rendimientos históricos")
            st.markdown("""
            Esta tabla muestra los rendimientos totales anualizados acumulados para periodos de 1, 3 y 5 años.
            Es útil para evaluar el desempeño histórico del activo.
            """)
            df["Daily Return"] = df["Close"].pct_change()
            rendimientos = {}
            for years in [1, 3, 5]:
                dias = 252 * years
                if len(df) >= dias:
                    rendimiento = ((df["Close"].iloc[-1] / df["Close"].iloc[-dias]) ** (1/years)) - 1
                    rendimientos[f"{years} años"] = rendimiento

            st.dataframe(pd.DataFrame.from_dict(rendimientos, orient='index', columns=['Rendimiento anualizado']))
            st.markdown("_Fórmula usada: ((Precio final / Precio inicial)^(1/años)) - 1_")

            # Calcular riesgo (volatilidad)
            st.subheader("📉 Riesgo histórico (volatilidad anualizada)")
            st.markdown("""
            Esta medida representa la volatilidad histórica del activo, calculada como la desviación estándar de los rendimientos diarios anualizada (x √252).
            Cuanto mayor sea este valor, mayor es el riesgo asociado al activo.
            """)
            std_daily = df["Daily Return"].std()
            vol_anual = std_daily * np.sqrt(252)
            st.write(f"**Volatilidad anualizada:** {vol_anual:.2%}")
            st.markdown("_Calculada como desviación estándar diaria x √252_")

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
