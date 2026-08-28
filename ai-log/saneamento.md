# Saneamento de dados — Fase 1

Registro rastreável de TODAS as correções/remoções feitas nos 5 CSVs.
Cada evento tem o porquê. Nenhuma decisão abaixo é invisível.

| Arquivo | Ação | Motivo | Qtd afetada |
|---|---|---|---|
| Details | drop_duplicates | listing_id duplicado | 0 |
| Details | recode | star_rating==0 => sem avaliação (vira NaN) | 1540 |
| Details | fillna | flags binárias com null tratado como False + coluna _missing | 355 |
| Details | drop_coluna | min_nights 100% zero (coluna morta) | 4441 |
| Hosts | drop_duplicates | owner_id duplicado | 1383 |
| Hosts | drop_coluna | response_rate/time 100% nulos (sem informação) | 2 |
| Mesh | recode | bairro 'none'->NaN; 5 registros sem bairro (mantidos) | 5 |
| Price_AV | drop_duplicates | mesmo (listing,data) capturado N vezes -> mantém captura mais recente | 59799 |
| Price_AV | dropna | price nulo | 0 |
| Price_AV | flag | price>3000 sinalizado como outlier a revisar (não exclui) | 390 |
| VivaReal | drop_duplicates | listing_id duplicado: mantém anúncio mais recente | 36 |
| VivaReal | flag | suburb nulo (anúncios sem bairro) mantidos como NaN | 98 |
| VivaReal | recode | usable_area==0 -> NaN (sem área declarada) | 11 |
| VivaReal | flag | outliers extremos sinalizados (m2>2000, condominio>50k, IPTU>100k, quartos>6) p/ revisão na Fase 2 | 48 |
| VivaReal | flag | terreno/comercial/outros marcados fora do alvo short stay (não excluídos) | 249 |
| Join | info | listings sem bairro (Mesh) | 0 |
| Join | info | listings SEM preço (Price_AV) -> NaN e flag_sem_preco | 3442 |
| Join | info | base_analise final: 4441 listings; sem preço=3442; sem bairro=5 | 0 |

## Interpretação da ocupação (proxy) — viés de captura

`occ_proxy_avg = 1 - (dias com preço / período observado)` mede a **taxa de bloqueio no snapshot**: noite SEM preço capturado = noite não disponível (reservada ou bloqueada). Como as capturas ocorrem em 06–20/jan/2025 fotografando estadias até 20/abril/2025, reservas ainda não feitas em janeiro aparecem como 'disponíveis' — logo `occ_proxy_avg` é um **limite inferior** da ocupação realizada. Consequência: toda projeção de receita construída sobre ele é conservadora. Listings com `flag_low_conf` (n_dates<30) têm ocupação pouco confiável e recebem peso reduzido nas Fases 3–5.

Limitação adicional: um listing capturado 1 única vez (n_capture=1) cobre menos noites e tende a ter cobertura de captura menor — `cobertura_captura` quantifica isso e é usado como peso de confiança.
