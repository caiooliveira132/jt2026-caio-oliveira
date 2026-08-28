# AI Log — Fase 4 (Modelo explicativo das receitas)

Sessão registrada: 2026-08-28 · Ferramenta: opencode (deepseek-v4-flash)

## Prompt solicitado
Modelo interpretável (regressão log-linear de receita e ocupação) medindo a contribuição de
cada característica, com controle de confusão (host profissional/multi-listing), por tipo de
anúncio, e interpretação de negócio ("aumentar X aumenta receita em Y%").

## Decisões metodológicas (e correções)
1. **Modelos**: 2 OLS — `log(receita_mensal_proxy)` (log-linear → coef×100 ≈ % de variação) e
   `occ_pct` (pontos percentuais). Aplicados no total (n=999) e por tipo (apartamento n=911, casa n=70).
2. **Controle de confusão**: `is_professional` e `host_multi_listing` no modelo — hosts
   profissionais concentram listagens melhores; o efeito das amenidades fica não-viciado.
3. **Referência de bairro = Meia Praia** (coluna removida do modelo). Corrigido depois que a
   primeira versão usou `get_dummies(drop_first=False)` com Todos os bairros + intercepto →
   colinearidade perfeita e coeficiente 'bairro_Tabuleiro' absurdo (+724%) por referência ambígua.
4. **Bug metodológico pego**: o `efeito_pct` (expm1) estava sendo exibido para o modelo de
   ocupação (em pp) — valores absurdos (59.489%). Corrigido: ocupação exibe `coef_pp` direto.
   Coeficientes de log-linear (receita) seguem em %.

## Resultados (interpretação de negócio)
**Fatores que movem RECEITA (% vs. referência Meia Praia):**
- `can_instant_book` (reserva instantânea): **+105%** receita (p<0.01) — ação de curto prazo forte.
- Dobrar `nº de reviews`: **+39%** (p=0.036) — avaliações = moeda de canal.
- `+1 hóspede` de capacidade: **+34%** (p<0.001) — dimensionar capacidade.
- Dobrar `reviews do host`: **+31%** (p<0.01) — reputação do host vende.
- `+1 quarto` (mantendo hóspedes): **−29%** (p=0.077, marginal) — mais quarto não é alavanca e
  dilui receita por hóspede. **Isso contradiz 'maior = melhor' e favorece compactos.**
- Fora dos bairros principais: **−71%** (p=0.05) — localização importa muito.

**Fatores que movem OCUPAÇÃO (pp):** `log_reviews` +3,9pp (p<0,001), `number_of_guests` +1,1pp,
`varanda` −2,8pp (curioso; possivelmente correlacionada com unidade maior/menos rotativa).

**R² baixo (0,09)**: maioria da variação é idiossincrática (não explicável por características
observáveis) — o modelo dá DIRECIONAIS, não predição pontual. Documentado como limitação.

## Consequência para a tese dos compactos
O modelo mostra que **receita não cresce com quartos** (controle por hóspedes) e que
**capacidade de hóspedes + reviews + reserva instantânea** são as alavancas. A favor da tese
de compactos de 1 quarto com forte capacidade por m². A Fase 5 vai aplicar a régua financeira
sobre os perfis para decisão (não apenas receita).

## Entregáveis
`output/fase4_modelo_receitas.md` (relatório completo + interpretação), `fase4_coeficientes.csv`,
`fase4_resumo.json`, `fase4_coef_plot.png`.