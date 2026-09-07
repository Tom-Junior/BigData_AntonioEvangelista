# 🧪 Lab 11 — Dashboard: visualizar para decidir

**Tempo:** 45 min · **Dia:** 3 · **Pré-requisito:** Lab 9 concluído (dados exportados)

## 🎯 Objetivo

Montar um dashboard com os 4 blocos do slide "Anatomia" (DIA 3, slide 10): KPIs, tendência, composição, detalhe.

> ⚠️ **Nota de honestidade:** o Metabase da rota A roda via **Docker, que também costuma exigir admin** para o daemon funcionar. Por isso, a rota "sem admin" aqui **não** é Metabase mais simples — é uma ferramenta genuinamente diferente (Plotly, gera um HTML sozinho, zero servidor) que **não precisa de privilégio nenhum**.

---

## 🖥️ ROTA A — Cluster real / com admin (Metabase via Docker)

### Passo 1 — Subir o Metabase

```bash
sudo docker run -d -p 3000:3000 --name metabase metabase/metabase
```
Aguarde ~1 minuto e abra `http://localhost:3000`.

### Passo 2 — Conectar ao banco com os dados exportados

Na tela inicial do Metabase: **Add your data** → escolha MySQL (ou SQLite, se foi o caminho do Lab 9) → informe host/porta/usuário/senha do `bigdata_course`.

### Passo 3 — Criar o KPI de topo

**New → Question → fraud_risk_bi** → Summarize → `Sum of qtd_fraudes`. Salve como "Total de Fraudes".

### Passo 4 — Criar o gráfico de composição

**New → Question → fraud_risk_bi** → Visualize as **Bar chart** → eixo X = `segment`, eixo Y = `taxa_fraude_pct`.

### Passo 5 — Montar o dashboard

**New → Dashboard** → arraste as questions criadas → organize KPI no topo, gráfico de composição abaixo → **Save**.

### Passo 6 — Adicionar um filtro

No dashboard, **Add a filter** → tipo "Category" → conecte à coluna `segment` da tabela.

---

## 🔓 ROTA B — Sem admin (Plotly, dashboard HTML standalone)

### Passo 1 — Instalar

```bash
pip install plotly pandas --user
```

### Passo 2 — Carregar os dados exportados no Lab 9

```python
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

fraud_risk = pd.read_csv('fraud_risk_export.csv')
print(fraud_risk)
```

### Passo 3 — Montar as 4 seções do template de dashboard

```python
fig = make_subplots(
    rows=2, cols=2,
    specs=[[{"type":"indicator"}, {"type":"indicator"}],
           [{"type":"bar"}, {"type":"table"}]],
    subplot_titles=("", "", "Taxa de fraude por segmento", "Detalhe por segmento")
)

# 1) KPI — total de transações
fig.add_trace(go.Indicator(
    mode="number", value=fraud_risk['total_transacoes'].sum(),
    title={"text": "Total de Transações"}
), row=1, col=1)

# 2) KPI — taxa de fraude geral
taxa_geral = 100 * fraud_risk['qtd_fraudes'].sum() / fraud_risk['total_transacoes'].sum()
fig.add_trace(go.Indicator(
    mode="number", value=round(taxa_geral, 2),
    number={"suffix": "%"},
    title={"text": "Taxa de Fraude Geral"}
), row=1, col=2)

# 3) Composição — barras por segmento
fig.add_trace(go.Bar(
    x=fraud_risk['segment'], y=fraud_risk['taxa_fraude_pct'],
    marker_color=['#2ecc71','#f5a623','#e5484d']
), row=2, col=1)

# 4) Detalhe — tabela navegável
fig.add_trace(go.Table(
    header=dict(values=list(fraud_risk.columns)),
    cells=dict(values=[fraud_risk[c] for c in fraud_risk.columns])
), row=2, col=2)

fig.update_layout(height=650, title_text="Dashboard — Risco de Fraude", showlegend=False)
fig.write_html("dashboard_fraude.html")
print("Salvo em dashboard_fraude.html — abra no navegador")
```

### Passo 4 — Abrir e conferir

```bash
# Linux
xdg-open dashboard_fraude.html
# ou simplesmente abra o arquivo manualmente no navegador
```
**Esperado:** um dashboard interativo com 2 KPIs, 1 gráfico de barras e 1 tabela — os mesmos 4 blocos do template visto no slide.

### Passo 5 — Adicionar interatividade (hover já vem de graça no Plotly)

```python
fig.update_traces(hovertemplate="%{x}: %{y:.2f}%", row=2, col=1)
fig.write_html("dashboard_fraude.html")
```
**O que ganhou:** passar o mouse na barra agora mostra o valor exato — o "tooltip" do slide de interatividade (11), sem precisar de servidor.

---

## ✅ Checkpoint

- [ ] Dashboard tem os 4 blocos: KPI, KPI, composição, detalhe
- [ ] (Rota A) Filtro por segmento funcionando no Metabase
- [ ] (Rota B) Arquivo `dashboard_fraude.html` abre no navegador e o hover mostra valores
- [ ] Você consegue apontar, em 1 frase, o que cada gráfico responde

---

## 🔧 Troubleshooting

| Problema | Rota | Solução |
|----------|------|---------|
| `docker: permission denied` | A | Precisa de `sudo` ou usuário no grupo `docker` — ambos exigem admin |
| Metabase não conecta ao banco | A | Confirme host `localhost` vs `127.0.0.1` — dentro do container pode precisar do IP da máquina host |
| `ModuleNotFoundError: plotly` | B | `pip install plotly --user`, depois reinicie o terminal |
| Gráfico não renderiza no navegador | B | Confirme que o arquivo `.html` foi realmente gerado (`ls -la dashboard_fraude.html`) |

**Próximo lab:** `DIA3_LAB12_ML_PREVIEW.md` — o último: um modelo simples de fraude.