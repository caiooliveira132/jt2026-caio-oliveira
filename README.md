**Vídeo (3 min): [link Google Drive — colocar aqui, compartilhamento "qualquer pessoa com o link"]**

# jt2026-caio-oliveira

Recomendação de investimento imobiliário short stay para a Seazone — Itapema/SC.
Desafio Jovens Talentos AI Builder 2026.

> **Resposta em 1 frase**: comprar/construir **apartamentos compactos de 1 quarto em Morretes/Meia Praia** (e não no Centro) como short stay, via **60% originação/lançamento + 40% pronto**, com retorno real dependente de ocupação ≥30% garantida por gestão de canal.

## Como avaliar em 2 cliques

1. **`relatorio.md`** (raiz) — a recomendação final: as 4 perguntas do edital + veredito da tese dos compactos + estimativa de retorno, com números.
2. **`ai-log/`** — o processo completo: 170 mensagens da sessão OpenCode exportadas em texto (`.md` + `.json`), mais o registro por fase (`fase0..8.md`).
3. **`output/apresentacao_apoio_video.pptx`** — a apresentação de apoio ao vídeo (9 slides, com os gráficos reais da análise).

## Estrutura

```
src/                       # código Python reexecutável (Fases 0-10)
  config.py                # caminhos para os dados (../jovens-talentos-2026-hackathon-data/data/)
  fase0_definitions.py     # Fase 0: definições + critério-mestre + 5 perguntas
  fase1_ingestion.py       # Fase 1: ingesta/saneamento/junção dos 5 CSVs -> base_analise
  fase2_financeiro.py      # Fase 2: régua financeira (cenários A/B, premissas justificadas)
  fase3_exploratoria.py    # Fase 3: receita por bairro/perfil/amenities/canal
  fase4_modelo.py          # Fase 4: modelo explicativo (OLS log-linear + ocupação)
  fase5_tese.py            # Fase 5: teste da tese dos compactos no Centro
  fase6_tradeoff.py        # Fase 6: pronto vs. lançamento (5 anos)
  fase7_recomendacao.py    # Fase 7: recomendação final
  fase10_check.py          # Fase 10: check final (simula o juiz / regras de reprovação)
  gerar_apresentacao.py    # gera o apoio visual do vídeo (pptx, 9 slides)
output/                    # todos os outputs organizados por fase
ai-log/                    # conversas de IA exportadas (processo = 30% da nota)
  sessao-completa/         #   export integral da sessão (md + json)
  fase0..8.md              #   registro do processo por fase
  saneamento.md            #   registro de saneamento
relatorio.md               # RECOMENDAÇÃO FINAL
requirements.txt           # dependências
roteiro-video.md           # teleprompter do vídeo (3 min, palavra por palavra)
apresentacao_apoio_video.pptx  # apoio visual (na pasta output/)
PUBLICAR.md                # passo a passo para criar repo público + push
```

## Como rodar

```bash
pip install -r requirements.txt
python -m src.fase0_definitions   # Fase 0
python -m src.fase1_ingestion     # Fase 1
python -m src.fase2_financeiro    # Fase 2
python -m src.fase3_exploratoria  # Fase 3
python -m src.fase4_modelo        # Fase 4
python -m src.fase5_tese          # Fase 5
python -m src.fase6_tradeoff      # Fase 6
python -m src.fase7_recomendacao  # Fase 7 -> output/relatorio.md
python -m src.fase10_check        # Fase 10 -> check final (simula o juiz)
python -m src.gerar_apresentacao  # regenera o pptx de apoio ao vídeo
```

## Entregáveis do desafio

| Entregável | Onde está | Status |
|---|---|---|
| Repositório público | este repo (`jt2026-caio-oliveira`) | ✅ commitado · ⏳ push pendente (`PUBLICAR.md`) |
| `relatorio.md` com a recomendação + posição sobre a tese | raiz | ✅ |
| `ai-log/` com as conversas de IA em texto | `ai-log/` | ✅ completo (sessão inteira, 170 msgs) |
| Vídeo (3 min) | Google Drive (link na 1ª linha do README) | ⏳ pendente — roteiro: `roteiro-video.md` |
| Apoio visual do vídeo | `output/apresentacao_apoio_video.pptx` | ✅ |

Os dados brutos vivem em `../jovens-talentos-2026-hackathon-data/data/` (repo clonado à parte; o caminho é configurável em `src/config.py`).