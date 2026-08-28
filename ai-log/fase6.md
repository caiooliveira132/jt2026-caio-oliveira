# AI Log — Fase 6 (Trade-off: comprar pronto vs. lançar novo projeto)

Sessão registrada: 2026-08-28 · Ferramenta: opencode (deepseek-v4-flash)

## Prompt solicitado
Recomendar a melhor FORMA de execução (não apenas "o quê"): comprar pronto (A) vs.
lançar/construir (B), com tudo do processo de originação (captação + obra + ciclo),
vantagens do imóvel novo (manutenção, preço, atratividade/retenção) e comparação em
5 anos (soma NOI, yield, payback, risco).

## Metodologia do modelo
- Perfil: compacto 1q (55m²); bairros: Meia Praia (principal), Morretes, Centro (sensibilidade).
- Regime de operação-alvo = **30%** (nível em que a régua fecha; Fase 5 mostrou que o
  proxy mediano 0.16–0.18 não paga o ativo). Documentado como premissa.
- **Pronto (A)**: invest = revenda/m² + ITBI 3,5% + mobília 8% + giro 3m; entra em ~2 meses;
  manutenção 1,5%/ano. Série Y1 0.8×, Y2–5 pleno.
- **Lançamento (B)**: produção all-in = 75% da revenda/m² (mkt_to_producao_ratio) + captação
  R$40k/un + mkt 4% + conting 8% + giro 6m; obra 18 meses sem receita → Y1=0, Y2=0.35×, Y3–5 pleno;
  manutenção 0,7%/ano. Prêmio do novo: diária +8%, ocupação +10%.
- Vantagem "retenção" do novo registrada como proxy qualitativo (mais avaliações, menos
  rotatividade de custo), não inflada nos números.

## Resultados (unidade 55m², Meia Praia — occ alvo 30%)
| Métrica | Pronto (A) | Lançamento (B) |
|---|---|---|
| Investimento | R$ 996.505 | R$ 805.758 |
| NOI pleno/ano | R$ 70 | R$ 15.143 |
| Soma NOI 5 anos | R$ 338 | R$ 50.729 |
| Yield 5y | 0,03% | 6,30% |

- **Sensibilidade**: Morretes pronto → NOI R$2,4k/ano (soma 5a ≈ R$11,5k, invest ~R$730k) —
  m² mais barato muda a viabilidade do pronto. Centro → pronto inviável (NOI negativo).
- **Robustez**: mesmo SEM o prêmio do novo, B vence em Meia Praia (só manutenção 0,7% + produção
  mais barata garantem). O prêmio acelera, não é o único motor.

## Senso crítico
1. **O payback estava absurdo (A: ~14 mil anos)** — não é bug: é o NOI ≈ R$70 do pronto na occ
   30%, sinal real de que **a unidade pronta a 30% não se paga em Meia Praia**. Adicionei nota
   explicando e reforçando que yield/soma de NOI (não payback) decidem.
2. **Recomendação híbrida 60/40** (pronto imediato em Morretes/Meia Praia + originação de prédio
   novo) — reconhece o trade tempo×risco sem abrir mão da margem de produção.

## Entregáveis
`output/fase6_tradeoff.md`, `fase6_tradeoff.csv`, `fase6_cumulative_noi.png`,
`fase6_resumo.json`.