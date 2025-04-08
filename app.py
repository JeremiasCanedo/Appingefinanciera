import streamlit as st

import pandas as pd
import numpy as np
import yfinance as yf
import seaborn as sns

print("¡Todo se importó correctamente!")

prompt = st.text_area("Escribe tu prompt")
st.text(prompt)
