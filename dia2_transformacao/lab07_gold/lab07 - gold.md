# 🧪 Lab 7 — Gold: agregações e KPIs

**Tempo:** 35 min · **Dia:** 2 · **Pré-requisito:** Lab 6 concluído

## 🎯 Objetivo

Construir a tabela Gold que o BI vai consumir amanhã — uma linha por segmento, com os KPIs prontos.

---

## 🖥️ ROTA A — Cluster real (Hive)

### Passo 1 — Criar a Gold layer principal

```sql
CREATE TABLE gold_fraud_risk
STORED AS PARQUET AS
SELECT
  segment,
  COUNT(*) AS total_transacoes,
  SUM(amount) AS valor_total,
  ROUND(AVG(amount), 2) AS ticket_medio,
  SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) AS qtd_fraudes,
  ROUND(100.0 * SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) / COUNT(*), 2) AS taxa_fraude_pct,
  SUM(CASE WHEN is_fraud THEN amount ELSE 0 END) AS valor_em_risco
FROM silver_transactions
GROUP BY segment;
```

### Passo 2 — Conferir o resultado

```sql
SELECT * FROM gold_fraud_risk ORDER BY taxa_fraude_pct DESC;
```
**Esperado:** 3 linhas (Premium, Standard, High-Risk), High-Risk no topo em taxa de fraude.

### Passo 3 — Criar uma segunda Gold: métricas diárias

```sql
CREATE TABLE gold_daily_metrics
STORED AS PARQUET AS
SELECT
  year, month, day,
  COUNT(*) AS transacoes,
  SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) AS fraudes
FROM silver_transactions
GROUP BY year, month, day;
```

### Passo 4 — Conferir os dias com mais fraude

```sql
SELECT year, month, day, fraudes
FROM gold_daily_metrics
ORDER BY fraudes DESC
LIMIT 5;
```
**Esperado:** dias perto do fim do mês concentrando mais fraude — reflete a sazonalidade do dataset.

---

## 🔓 ROTA B — Sem admin (DuckDB)

### Passo 1 — Gold principal por segmento

```python
import duckdb
con = duckdb.connect()
# recarregue a silver se necessário:
con.sql("CREATE TABLE silver_transactions AS SELECT * FROM read_parquet('bigdata/silver/transactions_enriched.parquet')")

con.sql("""
CREATE TABLE gold_fraud_risk AS
SELECT
  segment,
  COUNT(*) AS total_transacoes,
  SUM(amount) AS valor_total,
  ROUND(AVG(amount), 2) AS ticket_medio,
  SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) AS qtd_fraudes,
  ROUND(100.0 * SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) / COUNT(*), 2) AS taxa_fraude_pct,
  SUM(CASE WHEN is_fraud THEN amount ELSE 0 END) AS valor_em_risco
FROM silver_transactions
GROUP BY segment
""")
con.sql("SELECT * FROM gold_fraud_risk ORDER BY taxa_fraude_pct DESC").show()
```

### Passo 2 — Gold de métricas diárias

```python
con.sql("""
CREATE TABLE gold_daily_metrics AS
SELECT year, month, day,
  COUNT(*) AS transacoes,
  SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) AS fraudes
FROM silver_transactions
GROUP BY year, month, day
""")
con.sql("""
SELECT year, month, day, fraudes
FROM gold_daily_metrics ORDER BY fraudes DESC LIMIT 5
""").show()
```

### Passo 3 — Persistir as duas Golds (para o Lab 9 de export)

```python
con.sql("COPY gold_fraud_risk TO 'bigdata/gold/fraud_risk.parquet' (FORMAT PARQUET)")
con.sql("COPY gold_daily_metrics TO 'bigdata/gold/daily_metrics.parquet' (FORMAT PARQUET)")

# versão CSV também, para abrir em Excel/Metabase direto
con.sql("COPY gold_fraud_risk TO 'bigdata/gold/fraud_risk.csv' (HEADER, DELIMITER ',')")
print("Gold layer salva em bigdata/gold/")
```

---

## ✅ Checkpoint

- [ ] `gold_fraud_risk` com 3 linhas (uma por segmento)
- [ ] `gold_daily_metrics` com ~730 linhas (uma por dia)
- [ ] High-Risk aparece com a maior `taxa_fraude_pct`
- [ ] (Rota B) Arquivos Parquet + CSV salvos em `bigdata/gold/`

---

## 🔧 Troubleshooting

| Problema | Rota | Solução |
|----------|------|---------|
| `valor_em_risco` sempre zero | A/B | Confira se `is_fraud` está sendo comparado como boolean, não string `'true'` |
| Poucas linhas em `gold_daily_metrics` | A/B | Verifique se `year`/`month`/`day` foram calculados corretamente na Silver (Lab 6) |
| `Table silver_transactions does not exist` | B | Recarregue do Parquet salvo no Lab 6 |

**Próximo lab:** `DIA2_LAB08_EDA.md` — as 5 perguntas de negócio.