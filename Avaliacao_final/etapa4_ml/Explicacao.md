# Etapa 4 — Justificativa e explicação dos modelos de fraude

## Objetivo

Esta etapa implementa modelos supervisionados para apoiar a priorização de transações suspeitas da TechPay. O objetivo não é substituir a decisão antifraude, mas ordenar casos para investigação e comparar um modelo linear com um modelo não linear.

## Dados e preparação

Os modelos usam a tabela `silver_transactions`, depois do enriquecimento com a dimensão de clientes. As variáveis numéricas são `amount`, `risk_score` e `credit_score`. As variáveis categóricas foram convertidas para índices reprodutíveis: `segment_idx`, `channel_idx` e `merchant_idx`.

Foi utilizada divisão estratificada de 75% para treinamento e 25% para teste. A seed `42` foi aplicada à divisão e aos modelos para garantir reprodutibilidade. Não há registro da seed usada para gerar os CSVs originais fornecidos.

## Modelo 1 — Regressão Logística

A Regressão Logística utiliza padronização das variáveis e `class_weight='balanced'`, pois fraude é uma classe minoritária. A AUC está em `metricas_modelos.csv`; a matriz de confusão no limiar padrão de 0,5 está em `matriz_confusao_logistica.csv`; e os coeficientes estão em `coeficientes_logistica.csv`.

Um coeficiente positivo indica associação com maior probabilidade estimada de fraude, mantendo as demais variáveis constantes dentro da especificação. Isso não significa causalidade. A interpretação deve considerar também o recall, a precisão e o custo operacional dos falsos positivos.

## Modelo 2 — Random Forest (numTrees=30)

A Random Forest utiliza 30 árvores, equivalente ao requisito `numTrees=30`. A AUC dos dois modelos está em `metricas_modelos.csv`, enquanto as importâncias das variáveis estão em `importancias_random_forest.csv`.

A comparação entre os modelos permite avaliar se uma relação não linear melhora a ordenação dos casos suspeitos. A AUC mede a capacidade de ranking, mas não determina sozinha o limiar operacional. Antes de uma implantação real, seria necessário estimar custos de fraude não detectada, custo de revisão e impacto na experiência do cliente.

## Artefatos da etapa

- [Código dos modelos](Avaliacao_final/etapa4_ml/modelo_fraude.py)
