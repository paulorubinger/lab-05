# LAB-05 — GraphQL vs REST: Um Experimento Controlado

> **Disciplina:** Laboratório de Experimentação de Software — PUC Minas  

## Objetivo

Avaliar quantitativamente as diferenças de desempenho entre APIs GraphQL e REST, respondendo:

- **RQ1**: Respostas GraphQL são **mais rápidas** que REST?
- **RQ2**: Respostas GraphQL têm **tamanho menor** que REST?

O objeto experimental é a **API do GitHub**, que suporta ambas as abordagens sobre os mesmos dados.

---

## Estrutura do Projeto

```
LAB-05/
├── docs/
│   ├── design.md                        # Sprint 1 — Desenho do experimento
│   └── LABORATÓRIO 05 - GraphQL vs REST.pdf
├── src/
│   ├── collect_data.py                  # Sprint 2 — Coleta de dados
│   └── analyze.py                       # Sprint 2 — Análise estatística
├── dashboard/
│   ├── dashboard.py                     # Sprint 3 — Dashboard de visualização
│   └── output/                          # Gráficos gerados (criados automaticamente)
├── data/
│   ├── results.csv                      # Dados coletados (gerado por collect_data.py)
│   └── analysis_summary.txt             # Resumo estatístico (gerado por analyze.py)
├── report/
│   └── report.md                        # Relatório final
└── requirements.txt
```

---

## Pré-requisitos

```bash
# Instalar dependências Python
pip install -r requirements.txt
```

Você precisará de um **token do GitHub** com permissão de leitura pública:
1. Acesse https://github.com/settings/tokens
2. Gere um token com escopo `public_repo` (ou sem escopo para acesso público)
3. Configure o token no arquivo `.env`:

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite .env e adicione seu token
echo "GITHUB_TOKEN=ghp_seu_token_aqui" >> .env
```

---

## Execução

### Sprint 1 — Desenho e Preparação
Consulte [docs/design.md](docs/design.md) para o desenho completo do experimento.

### Sprint 2 — Coleta de Dados

```bash
# 1. Coletar dados
python src/collect_data.py

# 2. Analisar resultados estatisticamente
python src/analyze.py
```

Os dados são salvos em `data/results.csv` e o resumo em `data/analysis_summary.txt`.

### Sprint 3 — Dashboard

```bash
python dashboard/dashboard.py
```

Gera 7 visualizações salvas em `dashboard/output/`:

| Arquivo | Conteúdo |
|---|---|
| `fig1_boxplots.png` | Box plots de tempo e tamanho |
| `fig2_violins.png` | Violin plots — distribuição de probabilidade |
| `fig3_bars_by_repo.png` | Medianas por repositório |
| `fig4_summary_tables.png` | Tabelas de estatísticas descritivas |
| `fig5_temporal.png` | Evolução da mediana por trial |
| `fig6_heatmap.png` | Heatmap de medianas por repositório |
| `fig7_statistical_panel.png` | Painel com resultados do teste Mann-Whitney U |

---

## Metodologia em Resumo

| Parâmetro | Valor |
|---|---|
| Repositórios avaliados | 20 (populares, linguagens diversas) |
| Trials por repo × API | 30 |
| Total de medições | 1.200 |
| Teste estatístico | Mann-Whitney U (bicaudal, α = 0,05) |
| Tamanho do efeito | Correlação Rank-Biserial |

Consulte o [relatório completo](report/report.md) para discussão dos resultados.
