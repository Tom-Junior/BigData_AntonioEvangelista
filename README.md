# TechPay — Projeto Final de Big Data para Negócios

<p align="center">
Equipe: <strong>Antônio Evangelista Ribeiro Júnior e David Herbet Lima de Paiva</strong>
</p>


<p align="center">
  <strong>Pipeline de dados, análise de risco, dashboard antifraude e modelos de Machine Learning</strong>
</p>


<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/DuckDB-analytical%20database-FFF000?logo=duckdb&logoColor=111111" alt="DuckDB">
  <img src="https://img.shields.io/badge/Parquet-data%20lake-50ABF1" alt="Parquet">
  <img src="https://img.shields.io/badge/Plotly-interactive%20dashboard-3F4F75?logo=plotly&logoColor=white" alt="Plotly">
  <img src="https://img.shields.io/badge/Status-complete-1B998B" alt="Status">
</p>


> ## [Dashboard Interativo](https://tom-junior.github.io/BigData_AntonioEvangelista/Avaliacao_final/etapa3_analise/dashboard.html)



## 1. Visão geral

Este repositório contém a implementação do **Projeto Final de Big Data**, aplicada ao cenário fictício da fintech **TechPay**.

A solução percorre o ciclo completo de dados:

```
CSV de transações
        ↓
Raw — ingestão e schema explícito
        ↓
Bronze — limpeza e regras de qualidade
        ↓
Silver — enriquecimento e variáveis derivadas
        ↓
Gold — agregações para decisão
        ↓
Análises e dashboard
        ↓
Modelos de fraude
```

O projeto foi implementado pela **rota sem administrador**, utilizando DuckDB local, arquivos Parquet, pandas, Plotly e scikit-learn. Essa escolha evita a necessidade de iniciar HDFS, Hive, Docker ou Metabase, mas preserva os conceitos de ingestão, camadas, particionamento, processamento analítico e serving para BI.

## 2. Objetivos da avaliação

A avaliação foi organizada em quatro entregas técnicas principais:

| Etapa | Entrega | Resultado neste projeto |
|---|---|---|
| Etapa 1 | Arquitetura de Big Data | Diagrama, estratégia de dados e justificativa técnica |
| Etapa 2 | Execução do pipeline | Raw, Bronze, Silver, Gold e evidências de qualidade |
| Etapa 3 | Análise e Dashboard | Análises de risco, achados de negócio e dashboard responsivo |
| Etapa 4 | Machine Learning bônus | Regressão Logística, Random Forest, AUC, matriz e coeficientes |


## 3. Estrutura do repositório

```

BigData_AntonioEvangelista/
├── .gitignore
├── README.md
│
├── bigdata/
│   ├── bronze/
│   │   └── customers.parquet
│   │   └── transactions.parquet
│   │
│   ├── gold/
│   │   └── gold_category_risk.parquet
│   │   └── gold_channel_risk.parquet
│   │   └── gold_daily_metrics.parquet
│   │   └── gold_fraud_risk.parquet
│   │
│   ├── output/
│   │   └── gold_category_risk.csv
│   │   └── gold_channel_risk.csv
│   │   └── gold_daily_metrics.csv
│   │   └── gold_fraud_risk.csv
│   │
│   ├── raw/
│   │   │── transactions_partitioned/
│   │   │   └── year=2025/
│   │   │
│   │   └── transactions.parquet
│   │
│   ├── silver/
│       └── transactions_enriched.parquet
│
├── dia1_fundamentos/
│   ├── lab01_hdfs/
│   │   └── comandos.sh
│   └── lab02_sqoop/
│       └── import.sh
│
├── dia2_transformacao/
│   ├── lab03_hive_tabelas/
│   │   └── create_tables.sql
│   ├── lab04_particoes/
│   │   └── particionamento.sql
│   ├── lab05_bronze/
│   │   └── bronze.py
│   ├── lab06_silver/
│   │   └── silver.py
│   ├── lab07_gold/
│   │   └── gold.py
│   └── lab08_eda/
│       └── eda_queries.sql
│
├── dia3_insights_bi/
│   ├── lab09_export/
│   │   └── export.sh
│   ├── lab10_spark/
│   │   └── spark_queries.py
│   ├── lab11_dashboard/
│   │   └── dashboard.py
│   └── lab12_ml_preview/
│       └── modelo_fraude.py
│
└── avaliacao_final/
    ├── etapa1_arquitetura/
    │   ├── diagrama.mmd
    │   ├── diagrama.png
    │   └── justificativa.md
    ├── etapa2_bigdata/
    │   ├── pipeline.py
    │   └── explicacao.md
    ├── etapa3_analise/
    │   ├── analises.py
    │   ├── analises.sql
    │   ├── dashboard.html
    │   └── ideia_bi.md
    └── etapa4_ml/
        ├── modelo_fraude.py
        ├── justificativa.md
        ├── explicacao.md
        ├── metricas_modelos.csv
        ├── matriz_confusao_logistica.csv
        ├── coeficientes_logistica.csv
        └── importancias_random_forest.csv
```

Os arquivos derivados, como Parquet, banco DuckDB local, CSVs de saída e caches Python, são gerados durante a execução e protegidos pelo `.gitignore` quando apropriado.

## 4. Dados utilizados

A base principal é `avaliacao_transactions.csv`, com transações da TechPay. A dimensão `customers_synthetic.csv` fornece informações dos clientes para o enriquecimento da Silver.

### 4.1 Dicionário de dados das transações

| Coluna | Tipo | Descrição |
|---|---|---|
| `transaction_id` | Inteiro | Identificador único da transação |
| `customer_id` | Inteiro | Identificador do cliente |
| `amount` | Decimal | Valor monetário da transação |
| `transaction_type` | Texto | Compra, saque, transferência ou pagamento |
| `channel` | Texto | App, web, POS ou ATM |
| `merchant_category` | Texto | Categoria do estabelecimento |
| `timestamp` | Data/hora | Momento da transação |
| `status` | Texto | `approved` ou `declined` |
| `risk_score` | Decimal | Score de risco entre 0 e 100 |
| `segment` | Texto | Premium, Standard ou High-Risk |
| `credit_score` | Inteiro | Score de crédito entre 300 e 900 |
| `is_fraud` | Booleano | Rótulo de fraude |

### 4.2 Volume e qualidade inicial

| Indicador | Resultado |
|---|---:|
| Transações de entrada | 30.000 |
| Colunas da base de transações | 12 |
| Valores nulos identificados | 0 |
| IDs de transação duplicados | 0 |
| Valor mínimo | R$ 5,00 |
| Score de risco | 0 a 100 |
| Score de crédito | 300 a 900 |

## 5. Etapa 1 — Arquitetura

### 5.1 Artefatos

- [Diagrama em PNG](Avaliacao_final/etapa1_arquitetura/diagrama.png)
- [Diagrama editável Mermaid](Avaliacao_final/etapa1_arquitetura/diagrama.mmd)
- [Justificativa Técnica](Avaliacao_final/etapa1_arquitetura/Justificativa_da_arquitetura.md)

### 5.2 Decisões arquiteturais

A ingestão utiliza DuckDB local porque permite leitura analítica de CSV e Parquet sem serviço persistente ou privilégios administrativos. A alternativa seria HDFS com Hive e Spark, adequada a um cluster real, mas mais dependente de infraestrutura, rede, memória e da disponibilidade de daemons.

A estratégia de particionamento físico utiliza **ano e mês**. Essa granularidade atende consultas como “qual foi o risco de fraude em março de 2025?” sem criar a quantidade excessiva de arquivos que uma partição horária produziria. Dia e hora são preservados como colunas derivadas na Silver para análises temporais.

Os principais pontos de falha quando o volume crescer cem vezes são disco local, processo único de DuckDB, arquivos pequenos e recomputação histórica. As mitigações propostas são armazenamento distribuído ou objeto, ingestão incremental, compactação, Spark, catálogo de tabelas e materialização incremental da Gold.

Para fraude em tempo real, o desenho seria complementado por barramento de eventos, processamento contínuo, modelo ou regras de baixa latência e uma camada de serving operacional. O batch continuaria responsável por histórico, treinamento, auditoria e análises gerenciais.

## 6. Etapa 2 — Pipeline de Big Data

### 6.1 Código principal

O pipeline completo está em [pipeline.py](Avaliacao_final/etapa2_bigdata/pipeline.py).

Ele executa:

1. ingestão dos CSVs;
2. criação das tabelas Raw com schema explícito;
3. particionamento por ano e mês;
4. limpeza da Bronze;
5. enriquecimento da Silver;
6. criação das tabelas Gold;
7. exportação Parquet e CSV;
8. impressão das contagens e dos principais resultados.

O pipeline procura os datasets na raiz do projeto, em `datasets/`, no diretório atual ou em um diretório definido pela variável `TECHPAY_DATA_DIR`.

### 6.2 Camadas geradas

| Camada | Função | Resultado |
|---|---|---:|
| Raw | Preservar a entrada com tipos definidos | 30.000 linhas |
| Bronze | Remover duplicidades e dados impossíveis | 30.000 linhas |
| Silver | Enriquecer com clientes e derivar atributos | 29.975 linhas |
| Gold | Agregar métricas para o BI | Tabelas analíticas |

A Silver possui 25 linhas a menos que a Bronze porque 25 transações não encontraram cliente correspondente na dimensão. Essa perda foi identificada e documentada, em vez de ser ocultada.

### 6.3 Tabelas Gold

O pipeline gera:

- `gold_fraud_risk`: risco por segmento;
- `gold_channel_risk`: risco por canal e categoria;
- `gold_category_risk`: risco por categoria de estabelecimento;
- `gold_daily_metrics`: métricas diárias de volume e fraude.

## 7. Etapa 3 — Análise e Business Intelligence

### 7.1 Código e relatório

- [Código das análises](Avaliacao_final/etapa3_analise/analises.py)
- [Consultas SQL das análises](Avaliacao_final/etapa3_analise/analises.sql)
- [Ideia de BI e achados](Avaliacao_final/etapa3_analise/Relatorio_Analises_IdeiaBI.md)
- [Dashboard HTML](Avaliacao_final/etapa3_analise/dashboard.html)

O layout do dashboard foi configurado para ser responsivo e interativo.

### 7.2 Indicadores gerais

| Indicador | Resultado |
|---|---:|
| Transações analisadas | 29.975 |
| Fraudes | 748 |
| Taxa geral de fraude | 2,50% |
| Valor associado a fraude | R$ 119.252,98 |

### 7.3 Taxa por segmento

| Segmento | Transações | Fraudes | Taxa |
|---|---:|---:|---:|
| High-Risk | 2.913 | 281 | 9,65% |
| Standard | 10.634 | 311 | 2,92% |
| Premium | 16.428 | 156 | 0,95% |

### 7.4 Taxa por canal

| Canal | Transações | Fraudes | Taxa |
|---|---:|---:|---:|
| app | 12.009 | 452 | 3,76% |
| atm | 3.005 | 54 | 1,80% |
| web | 8.997 | 157 | 1,75% |
| pos | 5.964 | 85 | 1,43% |

### 7.5 Taxa por categoria de estabelecimento

| Categoria | Transações | Fraudes | Taxa |
|---|---:|---:|---:|
| viagem | 3.007 | 158 | 5,25% |
| saude | 2.949 | 72 | 2,44% |
| alimentacao | 5.971 | 138 | 2,31% |
| varejo | 9.040 | 203 | 2,25% |
| servicos | 4.574 | 90 | 1,97% |
| eletronico | 4.434 | 87 | 1,96% |

### 7.6 Finding → Insight → Ação

- **Finding:** High-Risk possui taxa de fraude de 9,65%.
- **Insight:** o risco relativo do segmento é muito superior ao de Premium.
- **Ação:** aplicar autenticação reforçada e priorizar revisão manual para High-Risk.

- **Finding:** o canal app possui taxa de 3,76%.
- **Insight:** o app combina a maior taxa com o maior volume absoluto de fraude.
- **Ação:** revisar autenticação, dispositivo, localização e comportamento no app.

- **Finding:** a categoria viagem possui taxa de 5,25%.
- **Insight:** viagens apresentam maior exposição relativa e valor financeiro relevante.
- **Ação:** criar regras específicas para transações de viagem e revisar o valor em risco.

## 8. Etapa 4 — Machine Learning

### 8.1 Modelos

O arquivo principal é [modelo_fraude.py](Avaliacao_final/etapa4_ml/modelo_fraude.py). O Lab 12 possui uma implementação completa e independente em [dia3_insights_bi/lab12_ml_preview/modelo_fraude.py](dia3_insights_bi/lab12_ml_preview/modelo_fraude.py).

Foram implementados:

1. **Regressão Logística**, com padronização, balanceamento de classes e coeficientes interpretáveis;
2. **Random Forest**, com 30 árvores, equivalente ao requisito `numTrees=30`.

As variáveis utilizadas são:

```text
amount
risk_score
credit_score
segment_idx
channel_idx
merchant_idx
```

### 8.2 Resultados

| Modelo | AUC |
|---|---:|
| Regressão Logística | 0,657 |
| Random Forest — 30 árvores | 0,690 |

A AUC mede a capacidade de ordenar casos mais suspeitos, mas não define sozinha o melhor limiar operacional. A decisão de produção deve considerar custo de falsos positivos, custo de fraude não detectada e capacidade da equipe de revisão.

### 8.3 Evidências geradas

- `metricas_modelos.csv`: AUC dos dois modelos;
- `matriz_confusao_logistica.csv`: matriz no limiar 0,5;
- `coeficientes_logistica.csv`: coeficientes das seis variáveis;
- `importancias_random_forest.csv`: importâncias da Random Forest;
- `explicacao.md`: interpretação em prosa.

A seed `42` foi utilizada para tornar a divisão treino/teste e os modelos reprodutíveis. Não há registro da seed usada na geração original dos CSVs fornecidos.

## 9. Como executar no Windows PowerShell

### 9.1 Estrutura recomendada

```
C:\DIRETORIO_PASTA\
├── avaliacao_final\
├── bigdata\
└── datasets\
    ├── avaliacao_transactions.csv
    └── customers_synthetic.csv
```

### 9.2 Instalar dependências

```powershell
& C:\Python\python.exe -m pip install duckdb pyarrow pandas plotly scikit-learn
```

### 9.3 Definir explicitamente o diretório dos dados

```powershell
$env:TECHPAY_DATA_DIR = "C:\DIRETORIO_PASTA\datasets"
```

### 9.4 Executar o pipeline

```powershell
& C:\Python\python.exe `
  "C:\DIRETORIO_PASTA\avaliacao_final\etapa2_bigdata\pipeline.py"
```

A saída inicial deve informar os caminhos encontrados:

```text
Base de transações: C:\DIRETORIO_PASTA\datasets\avaliacao_transactions.csv
Base de clientes: C:\DIRETORIO_PASTA\datasets\customers_synthetic.csv
```

### 9.5 Executar as análises e gerar o dashboard

```powershell
& C:\Python\python.exe `
  "C:\DIRETORIO_PASTA\avaliacao_final\etapa3_analise\analises.py"
```

O dashboard será salvo em:

```text
C:\DIRETORIO_PASTA\avaliacao_final\etapa3_analise\dashboard.html
```

### 9.6 Executar os modelos

```powershell
& C:\Python\python.exe `
  "C:\DIRETORIO_PASTA\avaliacao_final\etapa4_ml\modelo_fraude.py"
```

## 10. Como executar no Jupyter Notebook

No Jupyter, comandos de instalação devem usar `%pip`, e não ser escritos como código Python puro:

```python
%pip install duckdb pyarrow pandas plotly scikit-learn
```

Defina a raiz do projeto:

```python
from pathlib import Path

ROOT = Path(r"C:\DIRETORIO_PASTA")
%cd {ROOT}
```

Execute as três partes principais:

```python
%run avaliacao_final/etapa2_bigdata/pipeline.py
```

```python
%run avaliacao_final/etapa3_analise/analises.py
```

```python
%run avaliacao_final/etapa4_ml/modelo_fraude.py
```

Para visualizar o dashboard dentro do Notebook:

```python
from IPython.display import IFrame

IFrame(
    src="avaliacao_final/etapa3_analise/dashboard.html",
    width="100%",
    height=1000,
)
```

## 11. Troubleshooting

### `FileNotFoundError` para os CSVs

Defina o diretório explicitamente:

```powershell
$env:TECHPAY_DATA_DIR = "C:\DIRETORIO_PASTA\datasets"
```

Depois execute novamente o pipeline.

### `FileNotFoundError` para `modelo_fraude.py`

Confirme que o arquivo existe:

```powershell
Test-Path `
  "C:\DIRETORIO_PASTA\avaliacao_final\etapa4_ml\modelo_fraude.py"
```

O resultado esperado é `True`.

### O banco DuckDB não existe

Execute primeiro o pipeline:

```powershell
& J:\Python\python.exe `
  "C:\DIRETORIO_PASTA\avaliacao_final\etapa2_bigdata\pipeline.py"
```

Somente depois execute as análises e os modelos.

### `SyntaxError` ao instalar pacotes no Jupyter

Use:

```python
%pip install duckdb pyarrow pandas plotly scikit-learn
```

Não use diretamente em uma célula Python:

```text
python3 -m pip install ...
```

### Dashboard não abre

Confirme que o arquivo foi gerado:

```powershell
Test-Path `
  "C:\DIRETORIO_PASTA\avaliacao_final\etapa3_analise\dashboard.html"
```

O dashboard é um HTML standalone e não precisa de servidor web.

## 12. Entregáveis da avaliação

- [Arquitetura e justificativa](Avaliacao_final/etapa1_arquitetura/Justificativa_da_arquitetura.md)
- [Diagrama da arquitetura](Avaliacao_final/etapa1_arquitetura/diagrama.png)
- [Pipeline completo](Avaliacao_final/etapa2_bigdata/pipeline.py)
- [Explicação do pipeline](Avaliacao_final/etapa2_bigdata/Relatorio.md)
- [Código das análises](Avaliacao_final/etapa3_analise/analises.py)
- [Dashboard interativo](https://tom-junior.github.io/BigData_AntonioEvangelista/Avaliacao_final/etapa3_analise/dashboard.html)
- [Ideia de BI e achados](Avaliacao_final/etapa3_analise/Relatorio_Analises_IdeiaBI.md)
- [Modelos de fraude](Avaliacao_final/etapa4_ml/modelo_fraude.py)
- [Explicação dos modelos](Avaliacao_final/etapa4_ml/Explicacao.md)

## 13. Conclusão

O projeto demonstra uma solução completa de Big Data aplicada ao negócio. A TechPay recebe dados, organiza o fluxo em camadas, aplica regras de qualidade, enriquece as transações, cria agregações de risco, apresenta decisões em dashboard e testa modelos preditivos para priorização antifraude.

A principal recomendação de negócio é priorizar controles no segmento **High-Risk**, no canal **app** e na categoria **viagem**, sempre combinando taxa de fraude, volume de transações e valor financeiro em risco.

## 14. Autor e contatos

<p align="center">
  <a href="https://github.com/Tom-Junior">
    <img src="https://img.shields.io/badge/GitHub-Tom--Junior-181717?logo=github&logoColor=white" alt="GitHub — Tom-Junior">
  </a>
  &nbsp;
  <a href="https://www.linkedin.com/in/antonioerjunior/">
    <img src="https://img.shields.io/badge/LinkedIn-antonioerjunior-0A66C2?logo=linkedin&logoColor=white" alt="LinkedIn — antonioerjunior">
  </a>
</p>

<p align="center">
  <a href="https://github.com/Tom-Junior">GitHub: Tom-Junior</a>
  &nbsp; | &nbsp;
  <a href="https://www.linkedin.com/in/antonioerjunior/">LinkedIn: antonioerjunior</a>
</p>

<p align="center">
  <a href="https://github.com/DavidLih">GitHub: DavidLih</a>
  &nbsp; | &nbsp;
  <a href="https://www.linkedin.com/in/david-herbet-2312b02a/">LinkedIn: david-herbet-2312b02a</a>
</p>
