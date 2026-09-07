from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location
import duckdb
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "bigdata" / "techpay.duckdb"
OUT = ROOT / "avaliacao_final" / "etapa3_analise"
ML = ROOT / "avaliacao_final" / "etapa4_ml"
OUT.mkdir(parents=True, exist_ok=True)

con = duckdb.connect(str(DB), read_only=True)

def save(name, sql):
    data = con.execute(sql).df()
    data.to_csv(OUT / name, index=False)
    return data

segment = save("analise_segmento.csv", """
SELECT segment, ROUND(AVG(credit_score),1) score_medio,
COUNT(DISTINCT customer_id) clientes, COUNT(*) transacoes,
SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) fraudes,
ROUND(100.0*SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END)/COUNT(*),2) taxa_fraude_pct
FROM silver_transactions GROUP BY segment ORDER BY taxa_fraude_pct DESC
""")
channel = save("analise_canal.csv", """
SELECT channel, COUNT(*) total, SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) fraudes,
ROUND(100.0*SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END)/COUNT(*),2) taxa_fraude_pct
FROM silver_transactions GROUP BY channel
ORDER BY CASE channel WHEN 'app' THEN 1 WHEN 'atm' THEN 2 WHEN 'web' THEN 3 WHEN 'pos' THEN 4 ELSE 5 END
""")
category = save("analise_categoria.csv", """
SELECT merchant_category, COUNT(*) total,
SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) fraudes,
ROUND(100.0*SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END)/COUNT(*),2) taxa_fraude_pct,
SUM(CASE WHEN is_fraud THEN amount ELSE 0 END) valor_em_risco
FROM silver_transactions GROUP BY merchant_category ORDER BY taxa_fraude_pct DESC
""")
daily = save("analise_temporal.csv", """
SELECT CAST(ts AS DATE) AS dia, COUNT(*) total,
SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) fraudes,
ROUND(100.0*SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END)/COUNT(*),2) taxa_fraude_pct
FROM silver_transactions GROUP BY CAST(ts AS DATE) ORDER BY dia
""")
period = save("analise_periodo.csv", """
SELECT time_period AS periodo, COUNT(*) total,
SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) fraudes,
ROUND(100.0*SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END)/COUNT(*),2) taxa_fraude_pct
FROM silver_transactions GROUP BY time_period
ORDER BY CASE time_period WHEN 'madrugada' THEN 1 WHEN 'manha' THEN 2 WHEN 'tarde' THEN 3 WHEN 'noite' THEN 4 ELSE 5 END
""")
question = save("analise_pergunta_negocio.csv", """
SELECT time_period, amount_band, COUNT(*) total,
SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) fraudes,
ROUND(100.0*SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END)/COUNT(*),2) taxa_fraude_pct
FROM silver_transactions GROUP BY time_period, amount_band ORDER BY taxa_fraude_pct DESC
""")
heatmap = save("analise_heatmap.csv", """
SELECT segment, amount_band,
ROUND(100.0*SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END)/COUNT(*),2) taxa_fraude_pct
FROM silver_transactions GROUP BY segment, amount_band
""")
all_rows = con.execute("""SELECT COUNT(*) n,
SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) fraud,
SUM(amount) volume, SUM(CASE WHEN is_fraud THEN amount ELSE 0 END) risk
FROM silver_transactions""").fetchone()
con.close()

# Importa a função de treinamento sem executar o bloco principal duas vezes.
spec = spec_from_file_location("fraud_models", ML / "modelo_fraude.py")
fraud_models = module_from_spec(spec)
spec.loader.exec_module(fraud_models)
metrics, confusion, coefficients, importances = fraud_models.train_models()
metrics.to_csv(ML / "metricas_modelos.csv", index=False)
confusion.to_csv(ML / "matriz_confusao_logistica.csv", index=False)
coefficients.to_csv(ML / "coeficientes_logistica.csv", index=False)
importances.to_csv(ML / "importancias_random_forest.csv", index=False)

log_auc = float(metrics.loc[metrics.modelo == "Regressão Logística", "auc"].iloc[0])
rf_auc = float(metrics.loc[metrics.modelo.str.startswith("Random Forest"), "auc"].iloc[0])

# ---------- Gráficos ----------
def base_fig(fig, title=None):
    fig.update_layout(
        template="plotly_white", height=350, title=title,
        margin=dict(t=50, l=48, r=24, b=48),
        font=dict(family="Arial, sans-serif", color="#243447"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#ffffff",
        hoverlabel=dict(bgcolor="#102a43", font_color="white"),
    )
    return fig

fig_channel = base_fig(go.Figure(go.Bar(
    x=channel.channel, y=channel.taxa_fraude_pct,
    text=[f"{x:.2f}%" for x in channel.taxa_fraude_pct], textposition="outside",
    marker_color=["#ef6f6c", "#f4a261", "#2a9d8f", "#457b9d"],
    customdata=channel[["total", "fraudes"]],
    hovertemplate="Canal: %{x}<br>Taxa: %{y:.2f}%<br>Transações: %{customdata[0]:,}<br>Fraudes: %{customdata[1]:,}<extra></extra>"
)), "Taxa de fraude por canal")
fig_channel.update_yaxes(title="Taxa (%)", range=[0, max(channel.taxa_fraude_pct) * 1.35])

fig_period = base_fig(go.Figure(go.Scatter(
    x=period.periodo, y=period.taxa_fraude_pct, mode="lines+markers+text",
    text=[f"{x:.2f}%" for x in period.taxa_fraude_pct], textposition="top center",
    line=dict(color="#e76f51", width=3), marker=dict(size=10, color="#e76f51"),
    hovertemplate="Período: %{x}<br>Taxa: %{y:.2f}%<extra></extra>"
)), "Tendência temporal por período do dia")
fig_period.update_yaxes(title="Taxa (%)")

fig_category = base_fig(go.Figure(go.Bar(
    x=category.merchant_category, y=category.taxa_fraude_pct,
    text=[f"{x:.2f}%" for x in category.taxa_fraude_pct], textposition="outside",
    marker_color=["#e76f51", "#f4a261", "#e9c46a", "#2a9d8f", "#457b9d", "#6d597a"],
    customdata=category[["total", "fraudes", "valor_em_risco"]],
    hovertemplate="Categoria: %{x}<br>Taxa: %{y:.2f}%<br>Transações: %{customdata[0]:,}<br>Fraudes: %{customdata[1]:,}<br>Valor em risco: R$ %{customdata[2]:,.2f}<extra></extra>"
)), "Taxa de fraude por categoria de estabelecimento")
fig_category.update_yaxes(title="Taxa (%)", range=[0, max(category.taxa_fraude_pct) * 1.35])

fig_segment = base_fig(go.Figure(go.Bar(
    x=segment.segment, y=segment.taxa_fraude_pct,
    text=[f"{x:.2f}%" for x in segment.taxa_fraude_pct], textposition="outside",
    marker_color=["#d62828", "#f4a261", "#2a9d8f"],
    customdata=segment[["transacoes", "fraudes"]],
    hovertemplate="Segmento: %{x}<br>Taxa: %{y:.2f}%<br>Transações: %{customdata[0]:,}<br>Fraudes: %{customdata[1]:,}<extra></extra>"
)), "Composição do risco por segmento")
fig_segment.update_yaxes(title="Taxa (%)", range=[0, max(segment.taxa_fraude_pct) * 1.3])

pivot = heatmap.pivot(index="amount_band", columns="segment", values="taxa_fraude_pct").reindex(["baixo", "medio", "alto"])
fig_heat = base_fig(go.Figure(go.Heatmap(
    z=pivot.values, x=list(pivot.columns), y=list(pivot.index),
    text=[[f"{v:.2f}%" if pd.notna(v) else "" for v in row] for row in pivot.values],
    texttemplate="%{text}", colorscale=[[0, "#fff3b0"], [0.45, "#f4a261"], [1, "#c1121f"]],
    colorbar=dict(title="Taxa %"), hovertemplate="Faixa: %{y}<br>Segmento: %{x}<br>Taxa: %{z:.2f}%<extra></extra>"
)), "Risco cruzado: faixa de valor x segmento")

fig_trend = base_fig(go.Figure(go.Scatter(
    x=daily.dia, y=daily.fraudes, mode="lines", fill="tozeroy",
    line=dict(color="#264653", width=2), fillcolor="rgba(42,157,143,.20)",
    hovertemplate="Data: %{x}<br>Fraudes: %{y}<extra></extra>"
)), "Tendência diária de fraudes")
fig_trend.update_yaxes(title="Fraudes")

fig_coef = base_fig(go.Figure(go.Bar(
    x=coefficients.coefficient, y=coefficients.feature, orientation="h",
    marker_color=["#d62828" if x > 0 else "#457b9d" for x in coefficients.coefficient],
    text=[f"{x:.3f}" for x in coefficients.coefficient], textposition="outside",
    hovertemplate="Variável: %{y}<br>Coeficiente: %{x:.4f}<extra></extra>"
)), "Coeficientes — Regressão Logística")
fig_coef.update_layout(height=430, margin=dict(l=120, r=50, t=50, b=45))
fig_imp = base_fig(go.Figure(go.Bar(
    x=importances.importance, y=importances.feature, orientation="h",
    marker_color="#2a9d8f", text=[f"{x:.3f}" for x in importances.importance], textposition="outside",
    hovertemplate="Variável: %{y}<br>Importância: %{x:.4f}<extra></extra>"
)), "Importância — Random Forest")
fig_imp.update_layout(height=430, margin=dict(l=120, r=50, t=50, b=45))

# ---------- HTML executivo ----------
def html_fig(fig, include_js=False):
    return pio.to_html(fig, full_html=False, include_plotlyjs=True if include_js else False, config={"responsive": True, "displaylogo": False})

summary = pd.DataFrame([
    {"kpi": "recebidas", "valor": 30000},
    {"kpi": "válidas analisadas", "valor": int(all_rows[0])},
    {"kpi": "fraudes", "valor": int(all_rows[1])},
    {"kpi": "taxa_fraude_pct", "valor": round(100 * all_rows[1] / all_rows[0], 2)},
    {"kpi": "valor_em_risco", "valor": round(all_rows[3], 2)},
])
summary.to_csv(OUT / "kpis.csv", index=False)

cards = f"""
<section class="kpis">
  <div class="kpi"><span>TRANSAÇÕES RECEBIDAS</span><strong>{30000:,}</strong><small>base de entrada</small></div>
  <div class="kpi"><span>TRANSAÇÕES ANALISADAS</span><strong>{int(all_rows[0]):,}</strong><small>Silver layer</small></div>
  <div class="kpi danger"><span>TOTAL DE FRAUDES</span><strong>{int(all_rows[1]):,}</strong><small>casos rotulados</small></div>
  <div class="kpi warning"><span>TAXA GLOBAL DE FRAUDE</span><strong>{100*all_rows[1]/all_rows[0]:.2f}%</strong><small>risco observado</small></div>
  <div class="kpi money"><span>VALOR EM RISCO</span><strong>R$ {all_rows[3]:,.2f}</strong><small>fraudes identificadas</small></div>
</section>
"""

ml_table = confusion.to_html(index=False, classes="mini-table", border=0)
coef_table = coefficients.assign(coefficient=coefficients.coefficient.round(4)).to_html(index=False, classes="mini-table", border=0)

html = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>TechPay — Dashboard Analítico de Monitoramento de Fraudes</title>
<style>
:root {{ --navy:#102a43; --blue:#1d4e89; --cyan:#00b4d8; --teal:#2a9d8f; --coral:#e76f51; --ink:#243447; --paper:#f4f8fb; --line:#d9e2ec; }}
* {{ box-sizing:border-box; }} body {{ margin:0; background:linear-gradient(135deg,#eef5f8,#f8fbfd); color:var(--ink); font-family:Arial,Helvetica,sans-serif; }}
.container {{ max-width:1500px; margin:auto; padding:22px; }}
.hero {{ background:linear-gradient(120deg,#102a43 0%,#1d4e89 58%,#007c91 100%); color:white; border-radius:20px; padding:30px 34px; box-shadow:0 12px 28px rgba(16,42,67,.20); position:relative; overflow:hidden; }}
.hero:after {{ content:""; position:absolute; width:240px; height:240px; right:-50px; top:-90px; border:35px solid rgba(255,255,255,.10); border-radius:50%; }}
.hero h1 {{ margin:0 0 8px; font-size:clamp(25px,4vw,42px); letter-spacing:-1px; }} .hero p {{ margin:0; opacity:.86; font-size:15px; }}
.tag {{ display:inline-block; margin-top:18px; background:#00b4d8; color:#06283d; font-weight:bold; padding:8px 13px; border-radius:999px; font-size:12px; }}
.kpis {{ display:grid; grid-template-columns:repeat(5,1fr); gap:14px; margin:20px 0; }}
.kpi {{ background:white; border:1px solid var(--line); border-top:5px solid var(--blue); border-radius:14px; padding:18px; min-height:125px; box-shadow:0 5px 15px rgba(16,42,67,.07); }}
.kpi.danger {{ border-top-color:#d62828; }} .kpi.warning {{ border-top-color:#f4a261; }} .kpi.money {{ border-top-color:#2a9d8f; }}
.kpi span {{ display:block; color:#627d98; font-size:11px; font-weight:bold; letter-spacing:.6px; }} .kpi strong {{ display:block; color:var(--navy); font-size:26px; margin:14px 0 5px; }} .kpi small {{ color:#829ab1; }}
.section-title {{ margin:30px 0 12px; color:var(--navy); font-size:22px; }} .section-title span {{ color:var(--teal); }}
.grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:18px; }}
.card {{ background:white; border:1px solid var(--line); border-radius:16px; padding:10px 12px; box-shadow:0 5px 15px rgba(16,42,67,.06); min-width:0; }}
.card h3 {{ margin:8px 12px 0; color:var(--navy); font-size:16px; }} .model-cards {{ display:grid; grid-template-columns:repeat(2,1fr); gap:18px; }}
.auc {{ font-size:42px; font-weight:bold; color:var(--blue); padding:18px 12px 4px; }} .auc-label {{ padding:0 12px 12px; color:#627d98; }}
.mini-table {{ border-collapse:collapse; width:100%; margin:10px 0 20px; font-size:13px; }} .mini-table th {{ background:#102a43; color:white; padding:9px; text-align:left; }} .mini-table td {{ padding:8px; border-bottom:1px solid var(--line); }}
.footer {{ margin:30px 0 10px; color:#627d98; text-align:center; font-size:13px; }}
@media(max-width:1000px) {{ .kpis {{ grid-template-columns:repeat(3,1fr); }} }}
@media(max-width:700px) {{ .container {{ padding:12px; }} .kpis,.grid,.model-cards {{ grid-template-columns:1fr; }} .hero {{ padding:24px; }} .kpi strong {{ font-size:24px; }} }}
</style></head><body><main class="container">
<header class="hero"><h1>Dashboard Analítico de Monitoramento de Fraudes</h1><p>Visão executiva • TechPay Risk Intelligence • Atualizado a partir da Silver layer</p><span class="tag">DADOS + TECNOLOGIA + SUSTENTABILIDADE</span></header>
{cards}
<h2 class="section-title">Visão de risco <span>por dimensão</span></h2>
<div class="grid"><article class="card">{html_fig(fig_channel, True)}</article><article class="card">{html_fig(fig_period)}</article><article class="card">{html_fig(fig_category)}</article><article class="card">{html_fig(fig_segment)}</article><article class="card">{html_fig(fig_heat)}</article><article class="card">{html_fig(fig_trend)}</article></div>
<h2 class="section-title">Modelos de fraude <span>e explicabilidade</span></h2>
<div class="model-cards"><article class="card"><h3>Modelo 1 — Regressão Logística</h3><div class="auc">{log_auc:.3f}</div><div class="auc-label">AUC no conjunto de teste</div>{ml_table}</article><article class="card"><h3>Modelo 2 — Random Forest (numTrees=30)</h3><div class="auc">{rf_auc:.3f}</div><div class="auc-label">AUC no conjunto de teste</div>{html_fig(fig_imp)}</article><article class="card">{html_fig(fig_coef)}</article><article class="card"><h3>Coeficientes da Regressão Logística</h3>{coef_table}</article></div>
<footer class="footer">TechPay • Monitoramento antifraude orientado a dados • Dashboard HTML responsivo e interativo</footer>
</main></body></html>"""
(OUT / "dashboard.html").write_text(html, encoding="utf-8")
print("Dashboard executivo responsivo gerado:", OUT / "dashboard.html")
print("Canal:", channel.to_dict("records"))
print("Categoria:", category.to_dict("records"))
print("AUC Logistic:", log_auc, "AUC Random Forest:", rf_auc)
