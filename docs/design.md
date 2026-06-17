# Desenho do Experimento — GraphQL vs REST

## Contexto

Este experimento controlado visa avaliar quantitativamente as diferenças de desempenho entre APIs GraphQL e REST, respondendo às seguintes perguntas de pesquisa:

- **RQ1**: Respostas às consultas GraphQL são mais rápidas que respostas às consultas REST?
- **RQ2**: Respostas às consultas GraphQL têm tamanho menor que respostas às consultas REST?

A API utilizada como objeto experimental é a **API do GitHub**, por ser uma das únicas APIs públicas amplamente utilizadas que oferece suporte simultâneo a REST e GraphQL sobre os mesmos dados.

---

## A. Hipóteses

### RQ1 — Tempo de Resposta

| | Hipótese |
|---|---|
| **H₀ (Nula)** | Não há diferença significativa no tempo de resposta entre consultas GraphQL e REST. |
| **H₁ (Alternativa)** | Consultas GraphQL apresentam tempo de resposta menor que consultas REST. |

### RQ2 — Tamanho da Resposta

| | Hipótese |
|---|---|
| **H₀ (Nula)** | Não há diferença significativa no tamanho da resposta entre consultas GraphQL e REST. |
| **H₁ (Alternativa)** | Respostas GraphQL têm tamanho menor que respostas REST. |

---

## B. Variáveis Dependentes

| Variável | Unidade | Descrição |
|---|---|---|
| **Tempo de resposta** | milissegundos (ms) | Tempo decorrido desde o envio da requisição até o recebimento completo da resposta HTTP. |
| **Tamanho da resposta** | bytes | Número de bytes do corpo (`body`) da resposta HTTP. |

---

## C. Variáveis Independentes

| Variável | Valores |
|---|---|
| **Tipo de API** | `REST`, `GraphQL` |
| **Repositório consultado** | 20 repositórios populares do GitHub (lista fixa) |
| **Trial** | 1 a 30 (repetições por par repositório × API) |

---

## D. Tratamentos

Dois tratamentos são aplicados ao mesmo conjunto de repositórios:

### Tratamento 1 — REST
Requisição `GET` ao endpoint:
```
https://api.github.com/repos/{owner}/{repo}
```
Retorna ~80 campos descrevendo o repositório, incluindo dados não solicitados (over-fetching).

### Tratamento 2 — GraphQL
Requisição `POST` ao endpoint:
```
https://api.github.com/graphql
```
Com a query:
```graphql
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    name
    description
    stargazerCount
    forkCount
    issues(states: OPEN) { totalCount }
    updatedAt
    primaryLanguage { name }
  }
}
```
Retorna **apenas os 7 campos solicitados**, eliminando o over-fetching.

---

## E. Objetos Experimentais

20 repositórios populares do GitHub, selecionados por relevância e diversidade de linguagem:

| # | Owner | Repositório |
|---|---|---|
| 1 | facebook | react |
| 2 | vuejs | vue |
| 3 | microsoft | vscode |
| 4 | torvalds | linux |
| 5 | tensorflow | tensorflow |
| 6 | twbs | bootstrap |
| 7 | ohmyzsh | ohmyzsh |
| 8 | angular | angular |
| 9 | golang | go |
| 10 | kubernetes | kubernetes |
| 11 | nodejs | node |
| 12 | django | django |
| 13 | rails | rails |
| 14 | laravel | laravel |
| 15 | flutter | flutter |
| 16 | denoland | deno |
| 17 | rust-lang | rust |
| 18 | apple | swift |
| 19 | libp2p | go-libp2p |
| 20 | python | cpython |

---

## F. Tipo de Projeto Experimental

**Experimento controlado com medições repetidas** (*repeated measures*), do tipo **within-subjects**: cada repositório é submetido a ambos os tratamentos (REST e GraphQL), garantindo que variações individuais entre repositórios não influenciem a comparação.

O protocolo de coleta utiliza **randomização** da ordem entre REST e GraphQL por trial para mitigar efeitos de caching e ordem.

---

## G. Quantidade de Medições

| Parâmetro | Valor |
|---|---|
| Repositórios | 20 |
| Trials por repositório × API | 30 |
| Total de medições por API | 600 |
| Total geral | 1.200 |

---

## H. Ameaças à Validade

### Validade Interna
- **Caching de rede**: A API do GitHub pode retornar respostas em cache para requisições repetidas, reduzindo artificialmente o tempo de resposta. Mitigação: pequeno delay entre requisições e randomização da ordem.
- **Variação da latência de rede**: Flutuações de rede local ou da internet podem afetar o tempo de resposta. Mitigação: experimento executado em ambiente controlado (mesma máquina, mesma rede) e uso de mediana estatística.
- **Rate limiting**: A API do GitHub impõe limites de requisição. Mitigação: uso de token autenticado (5.000 req/h) e delays entre calls.

### Validade Externa
- **Generalização**: Os resultados são específicos à API do GitHub. Outras APIs podem apresentar comportamentos distintos dependendo da implementação do servidor GraphQL.
- **Tamanho das queries**: A vantagem do GraphQL em tamanho de resposta depende do grau de over-fetching da API REST equivalente. Para outros endpoints REST mais enxutos, a diferença pode ser menor.

### Validade de Construto
- **Métrica de tamanho**: O tamanho é medido no corpo (`Content-Length` ou `len(response.content)`) após decompressão HTTP. Dados transmitidos com compressão gzip seriam menores — ambas as APIs são chamadas sem `Accept-Encoding: gzip` para garantir comparação justa.
- **Overhead de JSON**: Ambas as APIs retornam JSON, garantindo comparação homogênea de formato.
