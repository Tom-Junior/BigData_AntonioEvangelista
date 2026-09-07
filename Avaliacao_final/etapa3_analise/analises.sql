-- Etapa 3 — Consultas analíticas da avaliação TechPay
-- Pré-requisito: executar avaliacao_final/etapa2_bigdata/pipeline.py
-- Banco DuckDB: bigdata/techpay.duckdb
-- As consultas usam a tabela silver_transactions.

-- 1) Taxa de fraude por segmento e score médio.
SELECT
    segment,
    ROUND(AVG(credit_score), 1) AS score_medio,
    COUNT(DISTINCT customer_id) AS clientes,
    COUNT(*) AS transacoes,
    SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) AS fraudes,
    ROUND(100.0 * SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) / COUNT(*), 2) AS taxa_fraude_pct
FROM silver_transactions
GROUP BY segment
ORDER BY taxa_fraude_pct DESC;

-- 2) Taxa de fraude por canal.
SELECT
    channel,
    COUNT(*) AS total,
    SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) AS fraudes,
    ROUND(100.0 * SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) / COUNT(*), 2) AS taxa_fraude_pct
FROM silver_transactions
GROUP BY channel
ORDER BY taxa_fraude_pct DESC;

-- 3) Taxa de fraude e valor em risco por categoria de estabelecimento.
SELECT
    merchant_category,
    COUNT(*) AS total,
    SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) AS fraudes,
    ROUND(100.0 * SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) / COUNT(*), 2) AS taxa_fraude_pct,
    ROUND(SUM(CASE WHEN is_fraud THEN amount ELSE 0 END), 2) AS valor_em_risco
FROM silver_transactions
GROUP BY merchant_category
ORDER BY taxa_fraude_pct DESC;

-- 4) Tendência diária de fraude.
SELECT
    CAST(ts AS DATE) AS dia,
    COUNT(*) AS total,
    SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) AS fraudes,
    ROUND(100.0 * SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) / COUNT(*), 2) AS taxa_fraude_pct
FROM silver_transactions
GROUP BY CAST(ts AS DATE)
ORDER BY dia;

-- 5) Pergunta de negócio: qual combinação de período do dia e faixa de valor
-- apresenta a maior taxa de fraude?
SELECT
    time_period,
    amount_band,
    COUNT(*) AS total,
    SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) AS fraudes,
    ROUND(100.0 * SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) / COUNT(*), 2) AS taxa_fraude_pct
FROM silver_transactions
GROUP BY time_period, amount_band
ORDER BY taxa_fraude_pct DESC;

-- 6) Risco cruzado: faixa de valor versus segmento, usado no heatmap.
SELECT
    segment,
    amount_band,
    COUNT(*) AS total,
    SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) AS fraudes,
    ROUND(100.0 * SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) / COUNT(*), 2) AS taxa_fraude_pct
FROM silver_transactions
GROUP BY segment, amount_band
ORDER BY segment, amount_band;
