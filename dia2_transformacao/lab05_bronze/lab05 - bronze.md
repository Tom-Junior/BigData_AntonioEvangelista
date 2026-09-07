# 🧪 Lab 5 — Bronze: limpar sem inventar

**Tempo:** 40 min · **Dia:** 2 · **Pré-requisito:** Lab 3 concluído

## 🎯 Objetivo

Construir a camada Bronze: remover duplicatas, corrigir tipos e descartar linhas impossíveis — sem tocar em lógica de negócio ainda.

---

## 🖥️ ROTA A — Cluster real (Hive)

### Passo 1 — Criar a tabela Bronze de clientes

```sql
CREATE TABLE bronze_customers
STORED AS PARQUET AS
SELECT DISTINCT
  customer_id, name, cpf, email, segment,
  CAST(credit_score AS INT) AS credit_score,
  CAST(created_at AS DATE) AS created_at
FROM raw_customers
WHERE customer_id IS NOT NULL
  AND credit_score BETWEEN 300 AND 900;
```

### Passo 2 — Conferir quantas linhas sobraram

```sql
SELECT COUNT(*) FROM bronze_customers;
SELECT COUNT(*) FROM raw_customers;
```
**Esperado:** os dois números devem ser bem próximos (o dataset é limpo por construção) — a diferença, se houver, mostra o filtro funcionando.

### Passo 3 — Criar a tabela Bronze de transações

```sql
CREATE TABLE bronze_transactions
STORED AS PARQUET AS
SELECT DISTINCT
  transaction_id, customer_id,
  CAST(amount AS FLOAT) AS amount,
  transaction_type, status,
  CAST(risk_score AS FLOAT) AS risk_score,
  CAST(is_fraud AS BOOLEAN) AS is_fraud,
  CAST(ts AS TIMESTAMP) AS ts
FROM raw_transactions
WHERE amount > 0
  AND customer_id IS NOT NULL;
```

### Passo 4 — Validar tipos e ranges

```sql
SELECT MIN(amount), MAX(amount), COUNT(*) FROM bronze_transactions;
SELECT is_fraud, COUNT(*) FROM bronze_transactions GROUP BY is_fraud;
```
**Esperado:** `MIN(amount)` > 0, contagem de fraude perto de 1.833 (1,83%).

### Passo 5 — Checar duplicatas removidas

```sql
SELECT transaction_id, COUNT(*) c
FROM bronze_transactions
GROUP BY transaction_id
HAVING c > 1;
```
**Esperado:** zero linhas — nenhum `transaction_id` duplicado.

---

## 🔓 ROTA B — Sem admin (DuckDB)

### Passo 1 — Bronze de clientes

```python
import duckdb
con = duckdb.connect()

con.sql("""
CREATE TABLE bronze_customers AS
SELECT DISTINCT
  customer_id, name, cpf, email, segment,
  CAST(credit_score AS INT) AS credit_score,
  CAST(created_at AS DATE) AS created_at
FROM read_csv_auto('bigdata/raw/customers/customers_synthetic.csv')
WHERE customer_id IS NOT NULL
  AND credit_score BETWEEN 300 AND 900
""")
con.sql("SELECT COUNT(*) FROM bronze_customers").show()
```

### Passo 2 — Bronze de transações

```python
con.sql("""
CREATE TABLE bronze_transactions AS
SELECT DISTINCT
  transaction_id, customer_id,
  CAST(amount AS FLOAT) AS amount,
  transaction_type, status,
  CAST(risk_score AS FLOAT) AS risk_score,
  CAST(is_fraud AS BOOLEAN) AS is_fraud,
  CAST(timestamp AS TIMESTAMP) AS ts
FROM read_csv_auto('bigdata/raw/transactions/transactions_synthetic.csv')
WHERE amount > 0 AND customer_id IS NOT NULL
""")
con.sql("SELECT MIN(amount), MAX(amount), COUNT(*) FROM bronze_transactions").show()
```

### Passo 3 — Checar duplicatas

```python
con.sql("""
SELECT transaction_id, COUNT(*) c
FROM bronze_transactions
GROUP BY transaction_id
HAVING c > 1
""").show()
```
**Esperado:** tabela vazia.

### Passo 4 — Persistir a camada Bronze em disco (Parquet)

```python
con.sql("COPY bronze_customers TO 'bigdata/bronze/customers.parquet' (FORMAT PARQUET)")
con.sql("COPY bronze_transactions TO 'bigdata/bronze/transactions.parquet' (FORMAT PARQUET)")
print("Bronze layer salva em bigdata/bronze/")
```

---

## ✅ Checkpoint

- [ ] `bronze_customers` e `bronze_transactions` criadas
- [ ] Zero duplicatas de `transaction_id`
- [ ] `amount` sempre > 0
- [ ] Contagem de fraude próxima de 1,83% do total

---

## 🔧 Troubleshooting

| Problema | Rota | Solução |
|----------|------|---------|
| `CAST` falha em `is_fraud` | A/B | Confira se a coluna vem como `True`/`False` (texto) — normalize com `CASE WHEN is_fraud='True' THEN true ELSE false END` |
| Contagem muito menor que 9.993/100.000 | A/B | Revise o filtro `WHERE` — pode estar descartando linhas válidas |
| `STORED AS PARQUET AS SELECT` erro de sintaxe | A | Separe em `CREATE TABLE ... STORED AS PARQUET;` seguido de `INSERT INTO ... SELECT` |

**Próximo lab:** `DIA2_LAB06_SILVER.md` — juntar clientes com transações.