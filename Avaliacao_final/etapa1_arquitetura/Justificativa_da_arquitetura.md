# Etapa 1 — Justificativa da arquitetura

## Síntese

A arquitetura proposta conduz a transação desde os canais digitais da TechPay até um painel orientado à decisão. A rota escolhida é a **rota sem administrador**, com DuckDB local, arquivos Parquet e Plotly. Essa alternativa reproduz as responsabilidades de um ambiente distribuído sem depender de HDFS, Hive, Docker ou serviços que exigiriam privilégios de sistema.

## Fluxo e formatos

Os eventos originados no aplicativo, na web, nos POS e nos caixas eletrônicos chegam inicialmente como CSV. A camada Raw preserva o registro recebido e define um schema explícito para evitar que valores monetários, datas ou booleanos sejam interpretados de forma inconsistente. A cópia operacional é Parquet porque esse formato é colunar, comprimido e adequado a leituras analíticas seletivas.

A Bronze aplica regras de qualidade sem criar lógica de negócio. Ela remove duplicidades, exige identificadores, aceita apenas valores monetários positivos, restringe o score de risco a 0–100, restringe o score de crédito a 300–900 e mantém status válidos. A Silver combina a transação com a dimensão de clientes e cria atributos de análise, como período do dia, faixa de valor e componentes de data. A Gold contém tabelas agregadas para segmento, canal/categoria e série diária. CSV também é exportado na Gold para facilitar inspeção e consumo por ferramentas simples de BI.

## Ingestão e particionamento

DuckDB foi escolhido porque executa SQL analítico diretamente sobre arquivos locais, lê e grava Parquet e não exige um serviço permanente. A alternativa seria HDFS com Hive e Spark, que seria apropriada em um cluster institucional, mas não foi usada porque a rota sem administrador é mais reprodutível neste ambiente e evita dependências de rede, daemon e memória.

O particionamento físico é feito por ano e mês na área Raw. Essa granularidade é adequada ao cenário de consultas que filtra um período, como “qual foi a fraude em março de 2025?”. Particionar por hora produziria muitos arquivos para a base atual, enquanto particionar apenas por ano reduziria o benefício do pruning. O dia e a hora continuam disponíveis como colunas derivadas na Silver para as análises, sem transformar cada dia em uma partição física obrigatória.

## Pontos de falha e escala

Se o volume crescer cem vezes, o primeiro risco é a sobrecarga de um único disco local e de um único processo DuckDB. O segundo é a criação de muitos arquivos pequenos quando o particionamento não for controlado. O terceiro é o tempo de atualização do dashboard e o custo de recomputar toda a série histórica. A mitigação seria mover o armazenamento para objeto ou HDFS, executar ingestão incremental, compactar arquivos por partição, usar Spark para processamento distribuído, aplicar catálogo de tabelas e materializar Gold incremental. Também seria necessário monitorar qualidade, latência e volume por partição.

## Mudança para fraude em tempo real

Para detecção em tempo real, o bloco de entrada deixaria de depender somente de arquivos em lote. Um barramento de eventos, como Kafka, receberia cada transação; um motor de processamento contínuo calcularia atributos e aplicaria regras ou modelo; e uma camada de serving de baixa latência retornaria aprovar, negar ou encaminhar para revisão. O fluxo batch atual continuaria útil para histórico, treinamento e auditoria, mas o dashboard passaria a consumir também uma camada operacional atualizada continuamente.
