import gradio as gr
import joblib
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# === DADOS ===
modelo     = joblib.load("energy_model.pkl")
ultimos    = joblib.load("ultimos_valores.pkl")
stats_hora = pd.read_csv("stats_hora.csv", index_col=0)
stats_dia  = pd.read_csv("stats_dia.csv", index_col=0)
stats_mes  = pd.read_csv("stats_mes.csv", index_col=0)
historico  = pd.read_csv("historico_diario.csv", parse_dates=["data"])

DIAS_SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
MESES       = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
               "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
APARELHOS   = {
    "Ar-condicionado (1.5 ton)": 1500,
    "Chuveiro elétrico":          5500,
    "Máquina de lavar":            700,
    "Ferro de passar":            1200,
    "Geladeira":                   150,
    "TV LED 50\"":                 100,
    "Computador + monitor":        300,
    "Micro-ondas":                1200,
}

TARIFA_BASE  = 0.75
TARIFA_PICO  = 1.20
MEDIA_GERAL  = stats_hora["mean"].mean()
MW_POR_CASA  = 0.0015

def nivel_consumo(hora, dia_semana):
    media = stats_hora.loc[hora, "mean"]
    pct   = (media / MEDIA_GERAL - 1) * 100
    fim   = dia_semana in [5, 6]
    if fim or hora in list(range(0, 6)) + list(range(22, 24)):
        return "baixo", media, pct
    elif hora in list(range(7, 10)) + list(range(17, 21)):
        return "alto", media, pct
    else:
        return "moderado", media, pct

# =============================================
# ABA 1 — Melhor horário
# =============================================
def melhor_horario(mes_nome, dia_nome):
    mes        = MESES.index(mes_nome) + 1
    dia_semana = DIAS_SEMANA.index(dia_nome)

    consumos = []
    for hora in range(24):
        features = pd.DataFrame([{
            "hora": hora, "dia_semana": dia_semana,
            "dia_mes": 15, "dia_ano": (mes-1)*30+15,
            "mes": mes, "trimestre": (mes-1)//3+1,
            "ano": 2017,
            "fim_semana":  1 if dia_semana in [5,6] else 0,
            "hora_pico":   1 if hora in [7,8,9,17,18,19] else 0,
            "verao":       1 if mes in [6,7,8] else 0,
            "inverno":     1 if mes in [12,1,2] else 0,
            "lag_1h":      ultimos["lag_1h"],
            "lag_24h":     ultimos["lag_24h"],
            "lag_168h":    ultimos["lag_168h"],
            "media_movel_24h":  ultimos["media_movel_24h"],
            "media_movel_168h": ultimos["media_movel_168h"]
        }])
        consumos.append(modelo.predict(features)[0])

    consumos = np.array(consumos)
    relativo = ((consumos - MEDIA_GERAL) / MEDIA_GERAL * 100).round(1)

    def cor_hora(h):
        n, _, _ = nivel_consumo(h, dia_semana)
        return {"baixo": "#00b894", "moderado": "#f0a500", "alto": "#e8473f"}[n]

    cores = [cor_hora(h) for h in range(24)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[f"{h}h" for h in range(24)],
        y=relativo,
        marker_color=cores,
        hovertemplate="<b>%{x}</b><br>%{customdata}<extra></extra>",
        customdata=[
            f"{'🟢 Ótimo' if c == '#00b894' else '🟡 Moderado' if c == '#f0a500' else '🔴 Pico'} — "
            f"{'abaixo' if r < 0 else 'acima'} da média em {abs(r):.0f}%"
            for c, r in zip(cores, relativo)
        ]
    ))

    fig.add_hline(y=0, line_color="white", line_width=1.5, opacity=0.4,
                  annotation_text="Média", annotation_position="right")

    idx_min = int(np.argmin(consumos))
    fig.add_annotation(
        x=f"{idx_min}h", y=relativo[idx_min] - 5,
        text=f"✅ Melhor: {idx_min}h",
        showarrow=False,
        font=dict(size=12, color="#00b894"),
        bgcolor="rgba(0,0,0,0.5)",
        borderpad=4
    )

    fig.update_layout(
        title=dict(text=f"Nível de consumo — {dia_nome}, {mes_nome}", font=dict(size=14)),
        xaxis_title="Hora do dia",
        yaxis_title="Variação em relação à média (%)",
        xaxis=dict(tickangle=0),
        template="plotly_dark",
        height=380,
        showlegend=False,
        margin=dict(t=50, b=40, l=60, r=20),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )

    melhores = sorted(range(24), key=lambda h: consumos[h])[:5]
    piores   = sorted(range(24), key=lambda h: consumos[h], reverse=True)[:3]

    rec = f"""
## 🟢 Melhores horários
**{', '.join([f'{h}h' for h in sorted(melhores)])}**
Rede opera abaixo da média — menor custo e menor impacto ambiental.

## 🔴 Evite nesses horários
**{', '.join([f'{h}h' for h in sorted(piores)])}**
Pico de consumo — rede sobrecarregada e tarifas maiores.

## 💡 Dica
{"Como é fim de semana, o consumo é menor o dia todo — ótimo para tarefas pesadas!" if dia_semana in [5, 6] else "Prefira lavar roupa e usar o chuveiro antes das 7h ou após as 21h."}
"""
    return fig, rec

# =============================================
# ABA 2 — Consumo agora
# =============================================
def consumo_agora(hora, dia_nome):
    dia_semana        = DIAS_SEMANA.index(dia_nome)
    nivel, media, pct = nivel_consumo(hora, dia_semana)

    cor   = {"baixo": "#00b894", "moderado": "#f0a500", "alto": "#e8473f"}[nivel]
    emoji = {"baixo": "🟢", "moderado": "🟡", "alto": "🔴"}[nivel]
    label = {"baixo": "BAIXO", "moderado": "MODERADO", "alto": "ALTO"}[nivel]
    casas = int(media / MW_POR_CASA / 1000)

    pct_gauge = min(max((media / stats_hora["mean"].max()) * 100, 0), 100)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct_gauge,
        number={"suffix": "%", "font": {"size": 40, "color": cor}, "valueformat": ".0f"},
        gauge={
            "axis": {"range": [0, 100], "ticksuffix": "%",
                     "tickvals": [0, 33, 66, 100],
                     "ticktext": ["Mínimo", "Baixo", "Alto", "Máximo"]},
            "bar":  {"color": cor, "thickness": 0.25},
            "steps": [
                {"range": [0,  33], "color": "rgba(0,184,148,0.2)"},
                {"range": [33, 66], "color": "rgba(240,165,0,0.2)"},
                {"range": [66, 100],"color": "rgba(232,71,63,0.2)"},
            ],
            "threshold": {"line": {"color": "white", "width": 2},
                          "thickness": 0.8, "value": pct_gauge}
        },
        title={"text": f"Nível de consumo às {hora}h<br><span style='font-size:0.8em;color:gray'>{dia_nome}</span>",
               "font": {"size": 14}}
    ))

    fig.update_layout(
        height=320, template="plotly_dark",
        margin=dict(t=60, b=20, l=30, r=30),
        paper_bgcolor="rgba(0,0,0,0)"
    )

    status = f"""
## {emoji} Consumo: **{label}**

Às **{hora}h de {dia_nome}**, a rede abastece o equivalente a **{casas} mil residências**.

O consumo está **{abs(pct):.0f}% {"acima" if pct > 0 else "abaixo"}** da média histórica.

---

{"🔴 **Horário de pico** — considere adiar tarefas pesadas como chuveiro prolongado, ferro ou máquina de lavar." if nivel == "alto" else "🟡 **Consumo moderado** — bom para tarefas leves. Evite ligar vários aparelhos ao mesmo tempo." if nivel == "moderado" else "🟢 **Ótimo momento** — consumo baixo! Hora ideal para aparelhos de alto consumo."}
"""
    return fig, status

# =============================================
# ABA 3 — Calculadora
# =============================================
def calcular_custo(aparelho, horas_uso, hora_inicio, dia_nome):
    dia_semana  = DIAS_SEMANA.index(dia_nome)
    nivel, _, _ = nivel_consumo(hora_inicio, dia_semana)
    potencia_w  = APARELHOS[aparelho]
    consumo_kwh = (potencia_w / 1000) * horas_uso
    tarifa      = TARIFA_PICO if nivel == "alto" else TARIFA_BASE
    custo_atual = consumo_kwh * tarifa

    melhor_h    = int(np.argmin([stats_hora.loc[h, "mean"] for h in range(24)]))
    custo_melhor= consumo_kwh * TARIFA_BASE
    economia    = custo_atual - custo_melhor

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Agora", f"Melhor horário\n({melhor_h}h)"],
        y=[custo_atual, custo_melhor],
        marker_color=["#e8473f", "#00b894"],
        text=[f"R$ {custo_atual:.2f}", f"R$ {custo_melhor:.2f}"],
        textposition="outside",
        textfont=dict(size=16, color="white"),
        width=0.35,
        hovertemplate="<b>%{x}</b><br>Custo: R$ %{y:.2f}<extra></extra>"
    ))

    if economia > 0.01:
        fig.add_annotation(
            x=1, y=custo_melhor / 2,
            text=f"💰 Economia de R$ {economia:.2f}",
            showarrow=False, font=dict(size=13, color="#00b894"),
            bgcolor="rgba(0,0,0,0.5)", borderpad=6
        )

    fig.update_layout(
        title=f"{aparelho} — {horas_uso}h de uso",
        yaxis_title="Custo estimado (R$)",
        yaxis=dict(range=[0, max(custo_atual, custo_melhor) * 1.4]),
        template="plotly_dark", height=340, showlegend=False,
        margin=dict(t=50, b=40, l=60, r=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
    )

    resultado = f"""
## 💰 Resultado

| | |
|---|---|
| **Aparelho** | {aparelho} |
| **Consumo** | {consumo_kwh:.2f} kWh em {horas_uso}h |
| **Custo agora ({hora_inicio}h)** | R$ {custo_atual:.2f} |
| **Melhor horário ({melhor_h}h)** | R$ {custo_melhor:.2f} |
| **Economia possível** | R$ {economia:.2f} |

---

{"⚠️ Você está no **horário de pico**. Aguarde até as **" + str(melhor_h) + "h** e economize **R$ " + f"{economia:.2f}**." if economia > 0.01 else "✅ Você já está usando no **horário mais econômico disponível**. Nenhuma economia adicional possível nesse horário."}

> 💡 Usando todo dia nesse horário, o custo mensal seria ~**R$ {custo_atual*30:.0f}**. No melhor horário: ~**R$ {custo_melhor*30:.0f}**.
"""
    return fig, resultado

# =============================================
# ABA 4 — Histórico
# =============================================
def painel_historico(visualizacao):
    bg = "rgba(0,0,0,0)"

    if visualizacao == "Por hora do dia":
        dados = stats_hora["mean"]
        cores = []
        for h in range(24):
            n, _, _ = nivel_consumo(h, 0)
            cores.append({"baixo": "#00b894", "moderado": "#f0a500", "alto": "#e8473f"}[n])

        fig = go.Figure(go.Bar(
            x=[f"{h}h" for h in range(24)],
            y=dados.values, marker_color=cores,
            text=[f"{v/1000:.1f}k" for v in dados.values],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>%{y:,.0f} MW<extra></extra>"
        ))
        fig.update_layout(title="Consumo médio histórico por hora do dia",
                          xaxis_title="Hora", yaxis_title="Consumo médio (MW)",
                          xaxis=dict(tickangle=0, tickmode="array",
                                     tickvals=list(range(0, 24, 2)),
                                     ticktext=[f"{h}h" for h in range(0, 24, 2)]),
                          template="plotly_dark", height=400,
                          paper_bgcolor=bg, plot_bgcolor=bg, showlegend=False)

    elif visualizacao == "Por dia da semana":
        dados = stats_dia["PJME_MW"]
        fig   = go.Figure(go.Bar(
            x=DIAS_SEMANA, y=dados.values,
            marker_color=["#1a78cf"]*5 + ["#00b894"]*2,
            text=[f"{v/1000:.1f}k MW" for v in dados.values],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>%{y:,.0f} MW<extra></extra>"
        ))
        fig.add_annotation(x="Sábado", y=dados.values[5]*1.05,
                           text="Fim de semana = menor consumo",
                           showarrow=False, font=dict(color="#00b894", size=11))
        fig.update_layout(title="Consumo médio por dia da semana",
                          yaxis_title="Consumo médio (MW)",
                          template="plotly_dark", height=400,
                          paper_bgcolor=bg, plot_bgcolor=bg, showlegend=False)

    elif visualizacao == "Por mês do ano":
        dados = stats_mes["PJME_MW"]
        cores = ["#e8473f" if v > dados.mean() else "#1a78cf" for v in dados.values]
        fig   = go.Figure(go.Bar(
            x=MESES, y=dados.values, marker_color=cores,
            text=[f"{v/1000:.1f}k" for v in dados.values],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>%{y:,.0f} MW<extra></extra>"
        ))
        fig.add_hline(y=dados.mean(), line_dash="dot", line_color="white",
                      opacity=0.5, annotation_text="Média anual")
        fig.update_layout(title="Consumo médio por mês — verão em destaque",
                          yaxis_title="Consumo médio (MW)",
                          template="plotly_dark", height=400,
                          paper_bgcolor=bg, plot_bgcolor=bg, showlegend=False)

    else:
        df_ano = historico.copy()
        df_ano["ano"] = df_ano["data"].dt.year
        df_ano = df_ano.groupby("ano")["consumo_mw"].mean().reset_index()

        fig = go.Figure(go.Scatter(
            x=df_ano["ano"], y=df_ano["consumo_mw"],
            mode="lines+markers",
            line=dict(color="#1a78cf", width=3),
            marker=dict(size=8, color="#1a78cf"),
            fill="tozeroy", fillcolor="rgba(26,120,207,0.15)",
            hovertemplate="<b>%{x}</b><br>%{y:,.0f} MW<extra></extra>"
        ))
        fig.add_annotation(
            x=2008,
            y=df_ano[df_ano["ano"]==2008]["consumo_mw"].values[0],
            text="📉 Crise de 2008", showarrow=True,
            arrowhead=2, font=dict(color="#f0a500")
        )
        fig.update_layout(title="Tendência anual de consumo (2002–2018)",
                          xaxis_title="Ano", yaxis_title="Consumo médio (MW)",
                          template="plotly_dark", height=400,
                          paper_bgcolor=bg, plot_bgcolor=bg)

    return fig

# =============================================
# INTERFACE
# =============================================
css = """
.gradio-container {
    max-width: 960px !important;
    margin: 0 auto !important;
}
.tab-nav button { font-size: 0.95rem !important; }
footer { display: none !important; }
"""

with gr.Blocks(title="EcoWatt") as app:

    gr.HTML("""
    <div style='text-align:center; padding: 1.5rem 0 0.5rem'>
        <h1 style='font-size:2.4rem; margin:0'>⚡ EcoWatt</h1>
        <p style='color:#888; margin-top:0.3rem; font-size:1rem'>
            Inteligência de dados para um consumo de energia mais consciente
        </p>
    </div>
    """)

    with gr.Tabs():

        with gr.Tab("🕐 Melhor horário"):
            gr.Markdown("**Descubra quando a rede elétrica está mais livre — e economize.**")
            with gr.Row():
                inp_mes = gr.Dropdown(MESES, label="Mês", value="Janeiro", scale=1)
                inp_dia = gr.Dropdown(DIAS_SEMANA, label="Dia da semana", value="Segunda", scale=1)
            btn1 = gr.Button("🔍 Analisar horários", variant="primary", size="lg")
            with gr.Row():
                out_g1 = gr.Plot(show_label=False, scale=2)
                out_r1 = gr.Markdown()
            btn1.click(melhor_horario, [inp_mes, inp_dia], [out_g1, out_r1])

        with gr.Tab("📊 Consumo agora"):
            gr.Markdown("**Veja o nível de consumo da rede no horário que você escolher.**")
            with gr.Row():
                inp_h2 = gr.Slider(0, 23, value=datetime.now().hour, step=1, label="Hora", scale=2)
                inp_d2 = gr.Dropdown(DIAS_SEMANA, label="Dia da semana",
                                     value=DIAS_SEMANA[datetime.now().weekday()], scale=1)
            btn2 = gr.Button("⚡ Ver consumo", variant="primary", size="lg")
            with gr.Row():
                out_gauge  = gr.Plot(show_label=False, scale=1)
                out_status = gr.Markdown()
            btn2.click(consumo_agora, [inp_h2, inp_d2], [out_gauge, out_status])

        with gr.Tab("💰 Calculadora"):
            gr.Markdown("**Calcule o custo de usar seus aparelhos e descubra o melhor horário.**")
            with gr.Row():
                inp_ap = gr.Dropdown(list(APARELHOS.keys()), label="Aparelho",
                                     value="Ar-condicionado (1.5 ton)", scale=2)
                inp_hs = gr.Slider(0.5, 8, value=2, step=0.5, label="Horas de uso", scale=1)
            with gr.Row():
                inp_h3 = gr.Slider(0, 23, value=12, step=1, label="Horário de uso", scale=2)
                inp_d3 = gr.Dropdown(DIAS_SEMANA, label="Dia da semana", value="Segunda", scale=1)
            btn3 = gr.Button("💡 Calcular", variant="primary", size="lg")
            with gr.Row():
                out_g3 = gr.Plot(show_label=False, scale=1)
                out_r3 = gr.Markdown()
            btn3.click(calcular_custo, [inp_ap, inp_hs, inp_h3, inp_d3], [out_g3, out_r3])

        with gr.Tab("📈 Histórico"):
            gr.Markdown("**Explore os padrões históricos de consumo de 2002 a 2018.**")
            inp_vis = gr.Radio(
                ["Por hora do dia", "Por dia da semana", "Por mês do ano", "Tendência anual"],
                value="Por hora do dia", label="Visualização"
            )
            out_hist = gr.Plot(show_label=False)
            inp_vis.change(painel_historico, inp_vis, out_hist)
            app.load(lambda: painel_historico("Por hora do dia"), outputs=out_hist)

    gr.HTML("""
    <div style='text-align:center; color:#555; font-size:0.78rem; padding:1rem 0'>
        ⚡ EcoWatt — dados históricos PJM East (2002–2018) | Modelo XGBoost |
        Projeto educacional de ciência de dados
    </div>
    """)

if __name__ == "__main__":
    app.launch(
        share=False,
        css=css,
        theme=gr.themes.Soft(
            primary_hue="emerald",
            secondary_hue="blue",
            font=gr.themes.GoogleFont("Inter")
        )
    )