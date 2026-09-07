# 📋 Avaliação Final — Big Data para Negócios

**Curso:** Big Data para Negócios

**Instituição:** UFC / MPCE

**Professor responsável:** Luiz Alexandre Moreira Barros

**Formato:** Individual · Relatório + repositório de código + dashboard

**Aluno(a):** 
> - Antônio Evangelista Ribeiro Júnior
> - David Herbet Lima de Paiva

**Data de entrega:** 07 de setembro de 2026

**Link do repositório:** https://github.com/Tom-Junior/BigData_AntonioEvangelista

---

## 📐 Composição da nota final

| Componente | Peso |
|------------|------|
| **Laboratórios (Labs 1 a 12)** | 30% |
| **Atividade Final** | 70% |

A Atividade Final se divide em 3 etapas:

| Etapa | Peso | Entregável central |
|-------|------|---------------------|
| 1 · Arquitetura de Big Data | 15% | Diagrama + justificativa |
| 2 · Big Data (execução) | 30% | Código + explicação em prosa |
| 3 · Análise & Dashboard | 25% | EDA + dashboard funcional + descrição do BI |

---

## 🎯 Regra de ouro da entrega

Em **todas as 3 etapas**, o relatório escrito segue esta regra:

> **Não cole código no relatório.** Explique em português, em prosa, o que cada etapa fez e por quê. O código em si vai no **repositório Git** — pasta correspondente à etapa (veja `00_ESTRUTURA_REPOSITORIO.md`). Você entrega **um link só**, cobrindo os 12 labs e as 3 etapas.

Esta regra existe porque a avaliação mede se você entendeu o que fez — não se sabe copiar e formatar um bloco de código. Um relatório cheio de `SELECT * FROM` colado não pontua; um parágrafo explicando *"eu limpei os dados removendo transações com valor negativo, porque isso indicaria erro de sistema, não fraude real"* pontua.

---

## 🏢 O Cenário

A fintech fictícia **TechPay** processa transações via aplicativo, site, POS e caixas eletrônicos. A área de risco quer três coisas de você:

1. Um **desenho de arquitetura** de como os dados devem fluir, da origem até a decisão de negócio
2. A **implementação real** desse fluxo — ingestão, limpeza, organização em camadas
3. **Análises que viram ação**, apresentadas num dashboard que a diretoria consegue usar sozinha

---

## 📊 A Base de Dados

Arquivo: `avaliacao_transactions.csv` (30.000 transações).

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `transaction_id` | INT | Identificador único |
| `customer_id` | INT | Cliente (1 a 8.000) |
| `amount` | FLOAT | Valor em R$ |
| `transaction_type` | STRING | compra / saque / transferencia / pagamento |
| `channel` | STRING | app / web / pos / atm |
| `merchant_category` | STRING | varejo / viagem / eletronico / alimentacao / servicos / saude |
| `timestamp` | DATETIME | Data e hora (2025) |
| `status` | STRING | approved / declined |
| `risk_score` | FLOAT | 0-100 |
| `segment` | STRING | Premium / Standard / High-Risk |
| `credit_score` | INT | 300-900 |
| `is_fraud` | BOOLEAN | Rótulo de fraude |

---

## 🖥️🔓 Sobre o ambiente técnico

As duas rotas ensinadas no curso valem nota cheia:

| Rota | O que é |
|------|---------|
| 🖥️ Cluster real | HDFS + Hive + Spark instalados |
| 🔓 Sem admin | DuckDB + PySpark local + Plotly |

Infraestrutura de Big Data configurada do zero é notoriamente instável — problemas de rede, memória, motor de execução ou serviço que não sobe são situações **reais e esperadas**, não falha de quem está aprendendo. A avaliação mede o entendimento do pipeline, não a sorte com configuração de cluster. Se o seu cluster travar, documente o que você tentou (mesmo sem sucesso) na Etapa 2 e finalize com a rota sem admin — isso **não reduz sua nota**.

---

# 1️⃣ Etapa 1 — Arquitetura de Big Data (15%)

## Objetivo

Antes de programar qualquer coisa, desenhe **como os dados devem fluir** da origem (TechPay) até a decisão de negócio.

## O que entregar

1. **Um diagrama** (ferramenta livre: draw.io, Excalidraw, Lucidchart, ou papel fotografado — o que importa é clareza)
2. **Um texto** (1-2 páginas) explicando as escolhas do diagrama

## O que o diagrama precisa mostrar

- [X] **Origem dos dados** — de onde vêm as transações da TechPay
- [X] **Camada de ingestão** — como os dados chegam ao ambiente de Big Data
- [X] **Camada de armazenamento** — onde ficam os dados brutos
- [X] **Camadas de processamento** — Bronze → Silver → Gold, com a ferramenta usada em cada uma
- [X] **Camada de serving/BI** — como o dado sai do pipeline e chega no dashboard
- [X] **Formato de arquivo em cada camada** (CSV? Parquet? Por quê?)
- [X] **Estratégia de particionamento**

## Perguntas que o texto precisa responder

1. Por que você escolheu a ferramenta de ingestão que escolheu? Qual seria a alternativa, e por que não usou ela?
2. Qual sua estratégia de particionamento (coluna, granularidade)? Justifique com um cenário de consulta real.
3. Onde estão os **pontos de falha** do seu desenho — o que quebra primeiro se o volume de dados multiplicar por 100? Como você mitigaria?
4. Se a TechPay pedisse **detecção de fraude em tempo real** (não em batch), o que mudaria no seu diagrama?

## Critérios de avaliação

| Critério | O que será observado |
|----------|------------------------|
| Completude | Todas as camadas do checklist estão no diagrama |
| Coerência do fluxo | Setas fazem sentido — dado não "pula" camada sem explicação |
| Justificativa técnica | Escolhas têm razão declarada, não são só "porque o curso usou" |
| Pensamento crítico | A pergunta sobre pontos de falha mostra reflexão real, não resposta genérica |

---

# 2️⃣ Etapa 2 — Big Data: Execução do Pipeline (30%)

## Objetivo

Sair do papel — executar de verdade a ingestão e as transformações sobre `avaliacao_transactions.csv`.

## O que entregar

1. **Código-fonte completo** (scripts `.sql`/`.py` ou notebook `.ipynb`) — na pasta `avaliacao_final/etapa2_bigdata/` do repositório
2. **Relatório em prosa** explicando cada etapa executada (o que foi feito, por quê, o que foi encontrado)

## Etapas esperadas no pipeline

1. **Ingestão** — trazer `avaliacao_transactions.csv` para o ambiente (HDFS ou pasta local)
2. **Criação de tabela raw** — schema definido, tipos corretos
3. **Particionamento** — aplique a estratégia desenhada na Etapa 1
4. **Bronze** — limpeza (duplicatas, tipos, valores impossíveis)
5. **Silver** — enriquecimento (avalie quais colunas fazem sentido derivar — ex.: faixa de valor, período do dia)
6. **Gold** — pelo menos 2 tabelas agregadas diferentes, pensando no que a Etapa 3 vai precisar

## O que o relatório precisa explicar (sem código colado)

Para **cada uma das 6 etapas acima**, escreva um parágrafo respondendo:

- O que essa etapa fez, em português simples?
- Que decisão você tomou (ex.: incluiu `channel`/`merchant_category` na Silver? Por quê?)
- Que problema real apareceu (dado sujo, erro de tipo, etc.) e como foi resolvido?

## Perguntas que o relatório precisa responder

1. Quantas linhas sobreviveram da Bronze em diante? Alguma foi descartada — por quê?
2. Sua Silver layer usa as colunas `channel` e `merchant_category`? Justifique a decisão de incluir ou não.
3. Que agregações você colocou na Gold, e por que essas — o que elas respondem que a Etapa 3 vai usar?

## Critérios de avaliação

| Critério | O que será observado |
|----------|------------------------|
| Pipeline completo | As 6 etapas foram executadas, com evidência (print, contagem de linhas) |
| Qualidade da limpeza | Bronze realmente removeu problemas, não só copiou os dados |
| Adaptação ao dado | Uso (ou justificativa de não uso) das colunas `channel`/`merchant_category` |
| Clareza da explicação | Um leitor sem ver o código entende o que foi feito e por quê |

---

# 3️⃣ Etapa 3 — Análise & Dashboard (25%)

## Objetivo

Transformar a Gold layer em **decisão visível**.

## O que entregar

1. **Código das análises** (queries/notebook) — na pasta `avaliacao_final/etapa3_analise/` do repositório
2. **Relatório dos achados** — cada análise, traduzida em insight de negócio
3. **Dashboard funcional** — arquivo `.html` ou link/print do Metabase, com pelo menos 4 blocos (KPI, tendência, composição, detalhe)
4. **Descrição da ideia do BI** — texto explicando o dashboard como produto, não como gráfico

## Análises mínimas esperadas

Pelo menos 3 destas:

1. Segmentação por score/segmento
2. Risco por canal (`channel`)
3. Risco por categoria de estabelecimento (`merchant_category`)
4. Padrão temporal (dia, hora, ou dia da semana)
5. Uma pergunta de negócio formulada por você

## Sobre a descrição da ideia do BI (obrigatório, texto, sem código)

Responda no relatório:

1. **Para quem** é esse dashboard — analista de risco? Diretoria? Atendimento?
2. **Que decisão** ele ajuda a tomar?
3. **Por que esses KPIs** e não outros — o que foi descartado, e por quê?
4. **Quem seria o dono** desse painel — quem olharia toda semana e agiria sobre ele?

## Bônus (pontos extras, não obrigatório)

Inclua um modelo preditivo simples (Regressão Logística) treinado nesta mesma base, com interpretação dos coeficientes. Material de apoio disponível em `AVALIACAO_FRAUDE.md`.

## Critérios de avaliação

| Critério | O que será observado |
|----------|------------------------|
| Análises com achado real | Números corretos, comparados com contexto |
| Framework aplicado | Finding → Insight → Ação aparece explicitamente em pelo menos 2 análises |
| Dashboard funcional | Abre, mostra dados reais, tem os 4 blocos mínimos |
| Ideia de BI bem descrita | As 4 perguntas acima têm resposta específica, não genérica |

---

## ✅ Checklist de entrega

- [X] ] Repositório Git criado, com a estrutura de `00_ESTRUTURA_REPOSITORIO.md`
- [X] **Etapa 1:** diagrama + texto de justificativa (1-2 páginas)
- [X] **Etapa 2:** código no repositório + relatório explicando as 6 etapas do pipeline
- [X] **Etapa 3:** código das análises + relatório de achados + dashboard + descrição do BI
- [X] Nenhum bloco de código colado dentro dos relatórios — só no repositório
- [X] Se a rota sem admin foi usada em algum ponto, isso está declarado

---

## ⚠️ O que evitar

- Diagrama idêntico ao dos slides do curso, sem adaptação ao cenário
- Relatório com blocos de código colados em vez de explicação em prosa
- Não usar `channel`/`merchant_category` sem justificar por quê
- Dashboard com números que não batem com o código do repositório
- Respostas genéricas na descrição da ideia do BI (ex.: *"é útil para a empresa tomar decisões"*)

---

## 📤 Como entregar

Envie **um único link** de repositório (GitHub ou GitLab), organizado conforme `00_ESTRUTURA_REPOSITORIO.md`, cobrindo os Labs 1-12 e as 3 Etapas desta avaliação.

Dúvidas sobre o enunciado: procure o professor antes da data de entrega.

---

**Bom trabalho.**
