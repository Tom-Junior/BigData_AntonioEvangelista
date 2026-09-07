## Resultado geral

O pipeline foi executado com DuckDB local e arquivos Parquet. A base de entrada contém 30.000 transações. Todas chegaram à Bronze. A Silver ficou com 29.975 linhas, pois 25 transações tinham `customer_id` sem correspondência na dimensão de clientes e foram excluídas pelo JOIN interno. A Gold foi calculada sobre as 29.975 linhas enriquecidas.

| Camada | Linhas | Observação |
|---|---:|---|
| Raw | 30.000 | Registro recebido com schema explícito |
| Bronze | 30.000 | Nenhuma linha violou as regras de qualidade |
| Silver | 29.975 | 25 transações sem cliente correspondente |
| Gold por segmento | 3 | Premium, Standard e High-Risk |
| Gold diária | 365 | Uma linha por data observada |

## 1. Ingestão

A ingestão leu o CSV de transações e o CSV de clientes diretamente do diretório do projeto. O schema foi declarado explicitamente para garantir que identificadores fossem inteiros, valores fossem numéricos, timestamps fossem datas e `is_fraud` fosse booleano. Essa escolha evita que a análise dependa da inferência automática de tipos. A cópia Parquet foi criada na área Raw para suportar leituras analíticas mais eficientes.

## 2. Criação da tabela Raw

A Raw preservou as colunas do arquivo de origem e adicionou uma visão particionada por ano e mês. O arquivo original não foi alterado. Essa separação permite rastreabilidade: a Raw representa o que chegou, enquanto as camadas seguintes representam decisões de tratamento.

## 3. Particionamento

O particionamento físico foi aplicado por ano e mês. Ele atende consultas de risco por período e evita a fragmentação excessiva que ocorreria com partições horárias ou por identificador. As colunas dia e hora foram mantidas na Silver para permitir tendências diárias e análises de período do dia.

## 4. Bronze

A Bronze removeu duplicidades completas, descartou identificadores nulos, valores monetários não positivos, scores fora dos limites plausíveis e status não reconhecidos. Nenhum registro foi eliminado nessa base específica, o que indica que a fonte fornecida já respeitava essas regras. Mesmo assim, os filtros permanecem no código para proteger a execução contra futuras cargas sujas.

## 5. Silver

A Silver fez o enriquecimento com a dimensão de clientes. As colunas `channel` e `merchant_category` foram mantidas deliberadamente, porque respondem a ações concretas: reforçar autenticação em um canal e revisar uma categoria de estabelecimento. Também foram derivados ano, mês, dia, dia da semana, hora, período do dia e faixa de valor. As 25 linhas sem cliente correspondente não foram mascaradas; foram registradas como perda de integridade referencial do JOIN.

## 6. Gold

Foram criadas quatro agregações. A primeira compara fraude, volume, ticket e valor em risco por segmento. A segunda cruza canal e categoria para localizar combinações de risco. A terceira resume risco por categoria de estabelecimento. A quarta registra tendência diária. Essas tabelas foram escolhidas porque alimentam diretamente os KPIs, a composição, a tendência e o detalhe exigidos no dashboard.

O resultado por segmento mostra High-Risk com taxa de fraude de 9,65%, Standard com 2,92% e Premium com 0,95%. O total foi de 748 fraudes em 29.975 transações, equivalente a 2,50%, com R$ 119.252,98 em valor associado a fraude.