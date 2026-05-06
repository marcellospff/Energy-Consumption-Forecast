# ⚡ EcoWatt — Previsão de Consumo de Energia

[![PT](https://img.shields.io/badge/PT-Português-009C3B?style=flat-square)](README.md) &nbsp;|&nbsp; [![EN](https://img.shields.io/badge/EN-English%20below-012169?style=flat-square)](#english-version)

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-FF6600?style=for-the-badge&logo=xgboost&logoColor=white)](https://xgboost.readthedocs.io/)
[![Gradio](https://img.shields.io/badge/Demo%20ao%20vivo-Gradio-FF7C00?style=for-the-badge&logo=gradio&logoColor=white)](https://huggingface.co/spaces/marcellospff/ecowatt)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-Spaces-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co/spaces/marcellospff/ecowatt)

> Modelo de previsão de consumo de energia elétrica baseado em série temporal horária — XGBoost com feature engineering temporal, app público interativo no Hugging Face Spaces com foco em impacto social.

---

## 🚀 Demo ao vivo

👉 **[Acesse o EcoWatt aqui](https://huggingface.co/spaces/marcellospff/ecowatt)**

O app permite que qualquer pessoa descubra o melhor horário para usar seus aparelhos, calcule o custo estimado de energia e explore padrões históricos de consumo — sem precisar entender nada de ciência de dados.

---

## 📌 Contexto e motivação

Consumo consciente de energia elétrica é um dos maiores desafios ambientais e econômicos da atualidade. A maioria das pessoas não sabe que o custo da energia varia conforme o horário — e que pequenas mudanças de hábito podem gerar economias reais na conta de luz e reduzir a pressão sobre a rede elétrica.

Este projeto usa Machine Learning aplicado a séries temporais para prever o consumo de energia hora a hora, e transforma esse modelo num app público acessível a qualquer pessoa.

---

## 🔍 O que o projeto cobre

- Análise exploratória de série temporal com 145.000+ registros horários
- Decomposição da série em tendência, sazonalidade e resíduo
- Feature engineering temporal — extração de padrões a partir do timestamp
- Divisão cronológica treino/teste — sem data leakage temporal
- Treinamento com XGBoost e avaliação com MAE, RMSE e MAPE
- App público com 4 abas interativas no Hugging Face Spaces

---

## 📊 Resultados do modelo

| Métrica | Valor |
|---|---|
| **MAE** | 380 MW |
| **RMSE** | 500 MW |
| **MAPE** | 1.21% |
| **R²** | 0.9933 |

O modelo erra em média **1.21%** do valor real — excelente para uma série temporal de energia com variações sazonais complexas.

---

## 🔎 Importância das features

| Feature | Importância |
|---|---|
| lag_1h (consumo 1h atrás) | 57.0% |
| lag_24h (mesmo horário ontem) | 16.0% |
| lag_168h (mesmo horário semana passada) | 13.0% |
| Média móvel 24h | 4.0% |
| Hora de pico | 2.5% |
| Demais features temporais | 7.5% |

O passado recente responde por ~86% da importância — confirmando a forte **inércia do consumo de energia**.

---

## 📱 Funcionalidades do app

**🕐 Melhor horário** — selecione o mês e o dia da semana para ver quando a rede opera com menor carga e descobrir os melhores horários para ligar seus aparelhos.

**📊 Consumo agora** — informe a hora e o dia para ver o nível atual de consumo da rede em tempo real com gauge visual.

**💰 Calculadora de custo** — selecione um aparelho doméstico, as horas de uso e o horário para calcular o custo estimado e a economia possível.

**📈 Painel histórico** — explore os padrões históricos de consumo por hora, dia da semana, mês e tendência anual (2002–2018).

---

## 🗂️ Estrutura do projeto

```
Energy-Consumption-Forecast/
│
├── energy_forecast.ipynb   # Notebook completo com EDA, decomposição e treino
├── ecowatt_app.py          # App Gradio com 4 abas interativas
├── app.py                  # Versão deploy (Hugging Face Spaces)
├── energy_model.pkl        # Modelo XGBoost treinado
├── ultimos_valores.pkl     # Últimos valores para features de lag
├── stats_hora.csv          # Estatísticas históricas por hora
├── stats_dia.csv           # Estatísticas históricas por dia da semana
├── stats_mes.csv           # Estatísticas históricas por mês
├── historico_diario.csv    # Histórico diário para visualização
├── PJME_hourly.csv         # Dataset original
├── requirements.txt        # Dependências do projeto
└── README.md               # Este arquivo
```

---

## 🛠️ Tecnologias utilizadas

- **Python 3.14**
- **Pandas / NumPy** — manipulação e feature engineering temporal
- **XGBoost** — modelo de regressão para série temporal
- **Statsmodels** — decomposição sazonal da série
- **Scikit-learn** — métricas de avaliação e divisão cronológica
- **Plotly** — visualizações interativas
- **Gradio** — interface web interativa
- **Joblib** — serialização do modelo

---

## ▶️ Como rodar localmente

```bash
# 1. Clone o repositório
git clone https://github.com/marcellospff/Energy-Consumption-Forecast.git
cd Energy-Consumption-Forecast

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute o app
python ecowatt_app.py
```

---

## 📁 Dataset

**Hourly Energy Consumption — PJM East**
Fonte: [Kaggle](https://www.kaggle.com/datasets/robikscube/hourly-energy-consumption)

145.366 registros horários de consumo de energia (em MW) da região PJM East dos EUA, cobrindo o período de 2002 a 2018.

---

## 👤 Autor

**Marcello Siqueira**
Estudante de Ciência de Dados para Negócios — UFPB

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/marcello-spff/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/marcellospff)

---

<a name="english-version"></a>

# ⚡ EcoWatt — Energy Consumption Forecast

> Time series energy consumption forecasting model — XGBoost with temporal feature engineering, public interactive app on Hugging Face Spaces focused on social impact.

---

## 🚀 Live Demo

👉 **[Access EcoWatt here](https://huggingface.co/spaces/marcellospff/ecowatt)**

The app allows anyone to discover the best time to use their appliances, calculate estimated energy costs and explore historical consumption patterns — no data science knowledge required.

---

## 📌 Context and motivation

Conscious energy consumption is one of the greatest environmental and economic challenges today. Most people don't know that energy costs vary by time of day — and that small habit changes can generate real savings on electricity bills while reducing pressure on the grid.

This project uses Machine Learning applied to time series to forecast hourly energy consumption, and transforms that model into a public app accessible to anyone.

---

## 🔍 What the project covers

- Exploratory analysis of a time series with 145,000+ hourly records
- Series decomposition into trend, seasonality and residual
- Temporal feature engineering — pattern extraction from timestamps
- Chronological train/test split — no temporal data leakage
- XGBoost training with MAE, RMSE and MAPE evaluation
- Public app with 4 interactive tabs on Hugging Face Spaces

---

## 📊 Model results

| Metric | Value |
|---|---|
| **MAE** | 380 MW |
| **RMSE** | 500 MW |
| **MAPE** | 1.21% |
| **R²** | 0.9933 |

The model errs on average **1.21%** of the real value — excellent for an energy time series with complex seasonal variation.

---

## 🔎 Feature importance

| Feature | Importance |
|---|---|
| lag_1h (consumption 1h ago) | 57.0% |
| lag_24h (same time yesterday) | 16.0% |
| lag_168h (same time last week) | 13.0% |
| 24h moving average | 4.0% |
| Peak hour | 2.5% |
| Other temporal features | 7.5% |

Recent past accounts for ~86% of feature importance — confirming the strong **inertia of energy consumption**.

---

## 📱 App features

**🕐 Best time** — select month and day of week to see when the grid operates with lower load and discover the best times to run your appliances.

**📊 Current consumption** — enter the hour and day to see the current grid consumption level with a visual gauge.

**💰 Cost calculator** — select a household appliance, hours of use and time slot to calculate estimated cost and potential savings.

**📈 Historical panel** — explore historical consumption patterns by hour, day of week, month and annual trend (2002–2018).

---

## 🗂️ Project structure

```
Energy-Consumption-Forecast/
│
├── energy_forecast.ipynb   # Full notebook with EDA, decomposition and training
├── ecowatt_app.py          # Gradio app with 4 interactive tabs
├── app.py                  # Deploy version (Hugging Face Spaces)
├── energy_model.pkl        # Trained XGBoost model
├── ultimos_valores.pkl     # Last values for lag features
├── stats_hora.csv          # Historical statistics by hour
├── stats_dia.csv           # Historical statistics by day of week
├── stats_mes.csv           # Historical statistics by month
├── historico_diario.csv    # Daily history for visualisation
├── PJME_hourly.csv         # Original dataset
├── requirements.txt        # Project dependencies
└── README.md               # This file
```

---

## 🛠️ Tech stack

- **Python 3.14**
- **Pandas / NumPy** — data manipulation and temporal feature engineering
- **XGBoost** — regression model for time series
- **Statsmodels** — seasonal decomposition
- **Scikit-learn** — evaluation metrics and chronological split
- **Plotly** — interactive visualisations
- **Gradio** — interactive web interface
- **Joblib** — model serialisation

---

## ▶️ How to run locally

```bash
# 1. Clone the repository
git clone https://github.com/marcellospff/Energy-Consumption-Forecast.git
cd Energy-Consumption-Forecast

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python ecowatt_app.py
```

---

## 📁 Dataset

**Hourly Energy Consumption — PJM East**
Source: [Kaggle](https://www.kaggle.com/datasets/robikscube/hourly-energy-consumption)

145,366 hourly energy consumption records (in MW) from the PJM East region of the USA, covering 2002 to 2018.

---

## 👤 Author

**Marcello Siqueira**
Business Data Science student — UFPB, Brazil

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/marcello-spff/)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/marcellospff)
