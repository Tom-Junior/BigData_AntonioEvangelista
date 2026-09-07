# Etapa 3 — Análise, achados e ideia do BI

## Público e decisão

O dashboard foi desenhado para a liderança de risco e para o analista responsável pela priorização semanal de investigações. Ele apoia a decisão de **onde concentrar revisão manual e controles adicionais**, combinando taxa de fraude, volume de transações e valor financeiro em risco. O painel é um produto de monitoramento, não apenas uma coleção de gráficos: cada bloco responde a uma pergunta operacional.

## Quatro blocos do painel

| Bloco | Pergunta respondida | Uso na decisão |
|---|---|---|
| KPI | Qual é o tamanho do problema? | Acompanhar transações, fraudes, taxa e valor em risco |
| Tendência | Quando o problema aumenta? | Planejar escala de revisão e observar anomalias diárias |
| Composição | Qual segmento concentra a taxa? | Priorizar grupos de clientes para controles |
| Detalhe | Como comparar os segmentos? | Escolher foco combinando volume e taxa |

## Achados no framework Finding → Insight → Ação

| Análise | Finding | Insight | Ação |
|---|---|---|---|
| Segmento | High-Risk tem taxa de fraude de 9,65%, contra 0,95% em Premium. | O segmento High-Risk tem risco relativo aproximadamente dez vezes maior que Premium. | Aplicar autenticação reforçada e fila de revisão prioritária para High-Risk. |
| Canal | A análise por canal é exportada em `analise_canal.csv` para comparar taxa e volume. | O canal deve ser avaliado com taxa e denominador, pois um canal com poucos eventos pode parecer extremo por acaso. | Recalibrar regras somente quando a taxa vier acompanhada de volume suficiente e persistência temporal. |
| Categoria | A análise por categoria mostra taxa e valor em risco em `analise_categoria.csv`. | Uma categoria pode ter taxa moderada, mas grande impacto financeiro quando concentra tickets elevados. | Priorizar categorias por valor em risco, não somente por percentual de fraude. |
| Tempo | A série diária está em `analise_temporal.csv` e no gráfico de tendência. | Picos devem ser comparados com o volume diário para distinguir sazonalidade de anomalia. | Criar alerta quando a taxa diária superar a faixa histórica, preservando a revisão humana. |
| Pergunta própria | A combinação de período do dia e faixa de valor está em `analise_pergunta_negocio.csv`. | Esse cruzamento testa se transações de alto valor em um período específico merecem regra adicional. | Usar o resultado como hipótese para uma regra experimental, com acompanhamento de falso positivo. |

## KPIs escolhidos e descartados

Foram escolhidos total de transações, quantidade de fraudes, taxa de fraude e valor em risco. Eles combinam escala, frequência relativa e impacto financeiro. O ticket médio por si só foi descartado do topo porque não indica risco sem o denominador de fraude. O score de crédito médio também não foi colocado como KPI principal porque é uma variável de contexto e não uma medida direta de desempenho do processo antifraude.

## Dono do painel e rotina

O dono operacional é o gerente de risco. O analista de fraude deve revisar o painel semanalmente, investigar segmentos ou combinações com alta taxa e abrir ações para autenticação, bloqueio ou revisão de regra. A diretoria pode consultar o painel para acompanhar tendência e valor protegido, sem precisar interpretar a camada técnica.
