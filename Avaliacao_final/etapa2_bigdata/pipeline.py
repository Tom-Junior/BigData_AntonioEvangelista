import os
from pathlib import Path
import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "bigdata"
for folder in [OUT / "raw", OUT / "bronze", OUT / "silver", OUT / "gold", OUT / "output"]:
    folder.mkdir(parents=True, exist_ok=True)

def find_input(filename: str) -> Path:
    """Localiza a base na raiz ou na pasta datasets do projeto."""
    configured_dir = os.environ.get("TECHPAY_DATA_DIR")
    candidates = ([Path(configured_dir) / filename] if configured_dir else []) + [
        ROOT / filename,
        ROOT / "datasets" / filename,
        Path.cwd() / filename,
        Path.cwd() / "datasets" / filename,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    searched = "\n".join(str(path) for path in candidates)
    raise FileNotFoundError(
        f"Não foi possível localizar {filename}. Caminhos verificados:\n{searched}"
    )


transactions = find_input("avaliacao_transactions.csv")
customers = find_input("customers_synthetic.csv")
print(f"Base de transações: {transactions}")
print(f"Base de clientes: {customers}")
con = duckdb.connect(str(OUT / "techpay.duckdb"))

# Ingestão e tabela raw: schema explícito, sem alterar o arquivo de origem.
con.execute("DROP TABLE IF EXISTS raw_transactions")
con.execute("DROP TABLE IF EXISTS raw_customers")
con.execute("""CREATE TABLE raw_transactions AS SELECT * FROM read_csv(?, header=true, auto_detect=false,
    columns={'transaction_id':'INTEGER','customer_id':'INTEGER','amount':'DOUBLE','transaction_type':'VARCHAR',
    'channel':'VARCHAR','merchant_category':'VARCHAR','timestamp':'TIMESTAMP','status':'VARCHAR',
    'risk_score':'DOUBLE','segment':'VARCHAR','credit_score':'INTEGER','is_fraud':'BOOLEAN'})""", [str(transactions)])
con.execute("""CREATE TABLE raw_customers AS SELECT * FROM read_csv(?, header=true, auto_detect=false,
    columns={'customer_id':'INTEGER','name':'VARCHAR','cpf':'VARCHAR','email':'VARCHAR','segment':'VARCHAR',
    'credit_score':'INTEGER','created_at':'DATE'})""", [str(customers)])
con.execute("COPY raw_transactions TO ? (FORMAT PARQUET, COMPRESSION ZSTD)", [str(OUT/'raw'/'transactions.parquet')])

# Particionamento físico para consultas temporais.
con.execute("DROP TABLE IF EXISTS raw_transactions_partitioned")
con.execute("""CREATE TABLE raw_transactions_partitioned AS
    SELECT *, year(timestamp) AS year, month(timestamp) AS month, day(timestamp) AS day
    FROM raw_transactions""")
part_dir = OUT / "raw" / "transactions_partitioned"
if part_dir.exists():
    import shutil; shutil.rmtree(part_dir)
con.execute("COPY raw_transactions_partitioned TO ? (FORMAT PARQUET, PARTITION_BY (year, month), OVERWRITE_OR_IGNORE true)", [str(part_dir)])

# Bronze: tipagem já garantida na raw; filtros documentam regras de qualidade.
con.execute("DROP TABLE IF EXISTS bronze_transactions")
con.execute("""CREATE TABLE bronze_transactions AS
    SELECT DISTINCT transaction_id, customer_id, CAST(amount AS DOUBLE) AS amount,
      transaction_type, channel, merchant_category, CAST(timestamp AS TIMESTAMP) AS ts,
      status, CAST(risk_score AS DOUBLE) AS risk_score, segment,
      CAST(credit_score AS INTEGER) AS credit_score, CAST(is_fraud AS BOOLEAN) AS is_fraud
    FROM raw_transactions
    WHERE transaction_id IS NOT NULL AND customer_id IS NOT NULL AND amount > 0
      AND risk_score BETWEEN 0 AND 100 AND credit_score BETWEEN 300 AND 900
      AND status IN ('approved','declined')""")
con.execute("COPY bronze_transactions TO ? (FORMAT PARQUET, COMPRESSION ZSTD)", [str(OUT/'bronze'/'transactions.parquet')])

# Dimensão de clientes sem duplicidade de chave.
con.execute("DROP TABLE IF EXISTS bronze_customers")
con.execute("""CREATE TABLE bronze_customers AS SELECT DISTINCT customer_id, name, cpf, email,
    segment, CAST(credit_score AS INTEGER) AS credit_score, CAST(created_at AS DATE) AS created_at
    FROM raw_customers WHERE customer_id IS NOT NULL AND credit_score BETWEEN 300 AND 900""")
con.execute("COPY bronze_customers TO ? (FORMAT PARQUET, COMPRESSION ZSTD)", [str(OUT/'bronze'/'customers.parquet')])

# Silver: mantém channel e merchant_category por serem dimensões acionáveis de risco.
con.execute("DROP TABLE IF EXISTS silver_transactions")
con.execute("""CREATE TABLE silver_transactions AS
    SELECT t.*, c.created_at AS customer_created_at,
      year(t.ts) AS year, month(t.ts) AS month, day(t.ts) AS day,
      dayofweek(t.ts) AS day_of_week, hour(t.ts) AS hour,
      CASE WHEN hour(t.ts) BETWEEN 6 AND 11 THEN 'manha'
           WHEN hour(t.ts) BETWEEN 12 AND 17 THEN 'tarde'
           WHEN hour(t.ts) BETWEEN 18 AND 23 THEN 'noite' ELSE 'madrugada' END AS time_period,
      CASE WHEN t.amount < 100 THEN 'baixo' WHEN t.amount < 1000 THEN 'medio' ELSE 'alto' END AS amount_band
    FROM bronze_transactions t JOIN bronze_customers c USING (customer_id)""")
con.execute("COPY silver_transactions TO ? (FORMAT PARQUET, COMPRESSION ZSTD)", [str(OUT/'silver'/'transactions_enriched.parquet')])

# Gold: agregações distintas para risco, canal/categoria e tendência temporal.
for t in ['gold_fraud_risk','gold_channel_risk','gold_category_risk','gold_daily_metrics']:
    con.execute(f'DROP TABLE IF EXISTS {t}')
con.execute("""CREATE TABLE gold_fraud_risk AS SELECT segment, COUNT(*) AS total_transacoes,
    SUM(amount) AS valor_total, ROUND(AVG(amount),2) AS ticket_medio,
    SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) AS qtd_fraudes,
    ROUND(100.0*SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END)/COUNT(*),2) AS taxa_fraude_pct,
    SUM(CASE WHEN is_fraud THEN amount ELSE 0 END) AS valor_em_risco
    FROM silver_transactions GROUP BY segment""")
con.execute("""CREATE TABLE gold_channel_risk AS SELECT channel, merchant_category,
    COUNT(*) AS total_transacoes, SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) AS qtd_fraudes,
    ROUND(100.0*SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END)/COUNT(*),2) AS taxa_fraude_pct,
    SUM(amount) AS valor_total FROM silver_transactions GROUP BY channel, merchant_category""")
con.execute("""CREATE TABLE gold_category_risk AS SELECT merchant_category,
    COUNT(*) AS total_transacoes, SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) AS qtd_fraudes,
    ROUND(100.0*SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END)/COUNT(*),2) AS taxa_fraude_pct,
    SUM(CASE WHEN is_fraud THEN amount ELSE 0 END) AS valor_em_risco
    FROM silver_transactions GROUP BY merchant_category""")
con.execute("""CREATE TABLE gold_daily_metrics AS SELECT CAST(ts AS DATE) AS data,
    COUNT(*) AS transacoes, SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) AS fraudes,
    ROUND(100.0*SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END)/COUNT(*),2) AS taxa_fraude_pct
    FROM silver_transactions GROUP BY CAST(ts AS DATE) ORDER BY data""")
for name in ['gold_fraud_risk','gold_channel_risk','gold_category_risk','gold_daily_metrics']:
    con.execute(f"COPY {name} TO ? (FORMAT PARQUET, COMPRESSION ZSTD)", [str(OUT/'gold'/f'{name}.parquet')])
    con.execute(f"COPY {name} TO ? (HEADER, DELIMITER ',')", [str(OUT/'output'/f'{name}.csv')])

counts = {}
for name in ['raw_transactions','bronze_transactions','silver_transactions']:
    counts[name] = con.execute(f'SELECT COUNT(*) FROM {name}').fetchone()[0]
print('CONTAGENS', counts)
print('GOLD_SEGMENT')
print(con.execute('SELECT * FROM gold_fraud_risk ORDER BY taxa_fraude_pct DESC').df().to_string(index=False))
con.close()