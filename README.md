# 📈 App IngeFinanciera

Esta aplicación permite analizar acciones bursátiles de forma sencilla e interactiva, utilizando datos históricos del mercado para calcular rendimientos y riesgos. Desarrollada con **Python** y **Streamlit**, es ideal para usuarios que desean explorar el comportamiento de una acción a lo largo del tiempo.

---

## 🚀 ¿Qué hace la app?

- Permite ingresar un **ticker bursátil** (ej. `AAPL`, `MSFT`, etc.)
- Muestra información básica de la empresa (nombre, sector, descripción)
- Extrae y visualiza precios históricos de los últimos **5 años**
- Calcula **rendimientos anualizados** acumulados (1, 3 y 5 años)
- Calcula la **volatilidad anualizada** como medida de riesgo
- Incluye explicaciones integradas para facilitar la interpretación de cada sección

---

## 🛠 Tecnologías utilizadas

- Python
- Streamlit
- yFinance
- pandas
- numpy
- matplotlib

---

## 🧪 Cómo ejecutar la app localmente

1. Clona este repositorio:

```bash
git clone https://github.com/JeremiasCanedo/Appingefinanciera.git
cd Appingefinanciera
```

2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

3. Ejecuta la app:

```bash
streamlit run nombre_del_archivo.py
```

(Cambia `nombre_del_archivo.py` por el nombre real del archivo de tu app, por ejemplo `app.py` o `streamlit_app.py`)

---

## 🌐 Despliegue en línea

Puedes ver la aplicación funcionando en:  
🔗 [https://jeremiascanedo-appingefinanciera.streamlit.app](https://jeremiascanedo-appingefinanciera.streamlit.app) (URL de ejemplo)

---

## 📄 Archivo `requirements.txt`

Asegúrate de incluir este archivo para que la app funcione en Streamlit Cloud. Contenido sugerido:

```
streamlit
yfinance
pandas
numpy
matplotlib
```

---

## ✍️ Autor

Jeremías Canedo  
📧 jeremias@email.com  
📅 Abril 2025
