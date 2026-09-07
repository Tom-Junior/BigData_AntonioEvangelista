# 🧪 Lab 8 — EDA: 5 perguntas de negócio

**Tempo:** 50 min · **Dia:** 2 · **Pré-requisito:** Lab 6 concluído (usa a Silver)

## 🎯 Objetivo

Rodar as 5 análises exploratórias vistas no slide 18-19 do DIA 2, registrando o insight de negócio de cada uma — não só o número.

> Nos dois blocos abaixo, troque `EXECUTAR:` pelo SQL indicado. As queries são as mesmas nas duas rotas (Hive e DuckDB entendem o mesmo SQL padrão) — só muda como você chama.

---

## 🖥️ ROTA A — Cluster real: abra `hive` e rode cada query

## 🔓 ROTA B — Sem admin: abra `python3`, `import duckdb`, `con = duckdb.connect()` e recarregue a Silver:
```python
con.sql("CREATE TABLE silver_transactions AS SELECT * FROM read_parquet('bigdata/silver/transactions_enriched.parquet')")
```

---

### 1️⃣ Segmentação por score

```sql
SELECT segment,
       ROUND(AVG(credit_score), 1) AS score_medio,
       COUNT(DISTINCT customer_id) AS clientes
FROM silver_transactions
GROUP BY segment
ORDER BY score_medio;
```
**Registre:** qual segmento tem o menor score médio? Isso confirma a lógica de risco do dataset?

---

### 2️⃣ Análise de risco por tipo de transação

```sql
SELECT transaction_type,
       SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) AS fraudes,
       COUNT(*) AS total,
       ROUND(100.0*SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END)/COUNT(*), 2) AS taxa_pct
FROM silver_transactions
GROUP BY transaction_type
ORDER BY taxa_pct DESC;
```
**Registre:** qual tipo de transação concentra a maior taxa de fraude? Faz sentido priorizar verificação extra nele?

---

### 3️⃣ Padrões temporais

```sql
SELECT day,
       COUNT(*) AS total_transacoes,
       SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) AS fraudes
FROM silver_transactions
GROUP BY day
ORDER BY fraudes DESC
LIMIT 10;
```
**Registre:** os dias com mais fraude coincidem com os dias de mais volume (fim de mês)? Ou fraude tem padrão próprio?

---

### 4️⃣ Cohort — clientes antigos vs novos

> Rota A (Hive):
```sql
SELECT
  CASE WHEN DATEDIFF(CURRENT_DATE, credit_score) IS NULL THEN 'n/a' END AS x; -- ver nota abaixo
```
> **Nota:** o Hive não tem `created_at` na Silver por padrão neste lab — para o cohort, faça o JOIN direto com `bronze_customers`:
```sql
SELECT
  CASE WHEN DATEDIFF(CURRENT_DATE, c.created_at) > 365 THEN 'cliente antigo'
       ELSE 'cliente novo' END AS cohort,
  ROUND(AVG(t.amount), 2) AS ticket_medio,
  COUNT(*) AS transacoes
FROM silver_transactions t
JOIN bronze_customers c ON t.customer_id = c.customer_id
GROUP BY CASE WHEN DATEDIFF(CURRENT_DATE, c.created_at) > 365 THEN 'cliente antigo'
              ELSE 'cliente novo' END;
```

> Rota B (DuckDB) — mesma lógica:
```python
con.sql("CREATE TABLE bronze_customers AS SELECT * FROM read_parquet('bigdata/bronze/customers.parquet')")
con.sql("""
SELECT
  CASE WHEN DATEDIFF('day', c.created_at, CURRENT_DATE) > 365 THEN 'cliente antigo'
       ELSE 'cliente novo' END AS cohort,
  ROUND(AVG(t.amount), 2) AS ticket_medio,
  COUNT(*) AS transacoes
FROM silver_transactions t
JOIN bronze_customers c ON t.customer_id = c.customer_id
GROUP BY 1
""").show()
```
**Registre:** clientes antigos gastam mais por transação? A diferença é grande o suficiente para virar uma ação de negócio?

---

### 5️⃣ Cross-sell — clientes Premium de alta frequência

```sql
SELECT customer_id, COUNT(*) AS compras
FROM silver_transactions
WHERE segment = 'Premium' AND transaction_type = 'compra'
GROUP BY customer_id
HAVING COUNT(*) > 10
ORDER BY compras DESC
LIMIT 10;
```
**Registre:** quantos clientes se qualificam? Isso é uma lista pequena o suficiente para uma campanha direcionada, ou grande demais?

---

## 📝 Consolidando os 5 achados (o framework do DIA 3)

Para cada pergunta acima, complete a tabela — isso vai direto para a apresentação final:

| # | Raw Finding (o número) | Business Insight (por que importa) | Ação proposta |
|---|------------------------|-------------------------------------|----------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

---

## ✅ Checkpoint

- [ ] As 5 queries rodaram sem erro
- [ ] Você preencheu a tabela de Raw Finding → Insight → Ação para pelo menos 3 das 5
- [ ] Os números fazem sentido com o que já vimos nos labs anteriores (fraude ~1,83%, High-Risk concentrando mais risco)

---

## 🔧 Troubleshooting

| Problema | Rota | Solução |
|----------|------|---------|
| `DATEDIFF` com sintaxe diferente | A/B | Hive usa `DATEDIFF(data1, data2)`; DuckDB usa `DATEDIFF('day', data1, data2)` — ordem dos argumentos muda |
| Cohort sem `created_at` | A/B | Confirme que fez o JOIN com `bronze_customers`, não só `silver_transactions` |
| Query 5 retorna vazio | A/B | O corte `> 10` pode ser exigente demais para uma amostra sintética — teste com `> 5` |

**Próximo lab:** `DIA3_LAB09_EXPORT.md` — tirar a Gold layer do Hive.