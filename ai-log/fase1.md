# AI Log — Fase 1 (Ingestão, saneamento e junção)

Sessão registrada: 2026-08-28 · Ferramenta: opencode (deepseek-v4-flash)

## Prompt solicitado
Fase 1 do plano: montar `base_analise` única e limpa a partir dos 5 CSVs, com registro
rastreável de todo saneamento, derivando ocupação, controle de host-back e VivaReal à parte.

## O que foi descoberto nos dados (antes de codar)
- **Price_AV**: 118.839 linhas, mas 59.799 duplicatas `(listing, data)` → uma estadia é
  capturada várias vezes em aquisições diferentes; foi mantida a captura mais recente
  (59.040 linhas únicas). Janela de estadias 06/jan–20/abr/2025; capturas 06–20/jan/2025.
  Apenas **999 dos 4.441 listings** têm preço.
- **Details**: `star_rating==0` em 1.540 (25%) = sem avaliação; `min_nights` 100% zero
  (coluna morta); coluna `is_professional` já existente (389 True) → controle de host-back direto.
- **Hosts**: 1.383 owner duplicados (30%); `response_rate/time` 100% nulos → colunas descartadas.
- **Mesh**: função `none` como bairro (5) → NaN; subtítulos mistos normalizados.
- **VivaReal**: 36 listing duplicados; 249 não-alvo (terreno/comercial/outros) apenas sinalizados;
  outliers graves (m² até 188.000; condomínio até R$3,15M) sinalizados para revisão na Fase 2.

## Senso crítico sobre a saída da IA
1. **A ocupação mediana 0,17 não foi aceita sem contestar.** Analisando o mecanismo de
   captura, o proxy `1 - dias_com_preço/span` é a *taxa de bloqueio no snapshot*: como as
   estadias foram fotografadas 2–3 meses antes, reservas futuras ainda não feitas aparecem
   como "disponíveis" → o proxy é um **limite inferior** conservador da ocupação realizada.
   Isso foi documentado no `saneamento.md` e obriga que qualquer projeção de receita nas
   próximas fases seja declarada conservadora.
2. **Cobertura desigual de captura**: listings com poucas capturas têm ocupação pouco
   confiável → criada `flag_low_conf` (n_dates < 30) e `cobertura_captura` como peso.
3. **Host-back**: `n_listings_per_host` mediana 1, mas máx 112; 43% dos listings pertencem
   a hosts multi-listing → confirmação do risco de confusão por host profissional (Fase 3/4).

## Entregáveis gerados (todos em `output/`)
- `base_analise.csv` (4.441 × 81) — details+mesh+price+hosts, com amenities, ocupação, flags.
- `vivareal_clean.csv` (8.293 × 25) — mercado de compra, outliers sinalizados, `preco_m2`.
- `price_dedup.csv` (59.040 × 4) — capturas deduplicadas.
- `saneamento.md` + `saneamento_log.json` (+ cópia em `ai-log/saneamento.md`).
- `perfil_estatistico.md` — resumos pós-limpeza de cada tabela.

## Validação do "juiz simulado"
> "Sua média de ocupação considera o viés de captura?"
Resposta preparada: sim — `occ_proxy_avg` é limite inferior (snapshot jan/2025 vs estadias até
abr/2025), receitas projetadas serão conservadoras, e `flag_low_conf`/`cobertura_captura`
controlam a confiança por listing. Documentado em `saneamento.md`.