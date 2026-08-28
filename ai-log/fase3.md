# AI Log — Fase 3 (Análise exploratória: receita, localização, perfil)

Sessão registrada: 2026-08-28 · Ferramenta: opencode (deepseek-v4-flash)

## Prompt solicitado
Responder em dados brutos: melhor localização, melhor perfil, características que
explicam receitas (ranking por bairro com dispersão, perfil por quartos/tipologia/tipo
de anúncio, dummies de amenities, dependência de canal via hosts multi-listing), com
cada afirmação levando evidência + N.

## Produzido
- `fase3_base_receita.csv` — base per-listing com `receita_anual/mensal_proxy`, `cv_preco`, `diaria_x_occ`
  (consumida nas Fases 4 e 5).
- Ranking de receita por bairro (N>=5): Meia Praia R$3.124/mês (n=632), Tabuleiro R$2.722 (n=20),
  Centro R$2.340 (n=205), Morretes R$2.060 (n=83), etc. Com p25/p75/cv.
- Tabelas por quartos, tipo de anúncio, amenities (delta %) e hosts (multi-listing/profissional).
- Matriz bairro × quartos (receita mediana + N por célula).
- Gráficos: boxplot bairro, ranking+erro, heatmap bairro×quartos, barra quartos, barra amenities.
- Relatório `fase3_relatorio_exploratorio.md` com texto de leitura.

## Senso crítico sobre a saída da IA
1. **Bug de agregação em pandas** (misto `count` com tuplas `(col, aggfunc)`) — corrigido para
   tuplas em todas as `.agg` que agrupavam por perfil/host.
2. **`occ_proxy=0` em anúncios com captura rara** — não é "vazio o ano todo", é o piso do snapshot.
   O corte `n_dates>=30` na matriz reduz o efeito. Documentado no relatório.
3. **Studio tem N=8** — a tese dos compactos na prática, nesta base, tem de ser avaliada como **1q**.
4. **Cuidado com N pequeno** (Várzea n=5, Alto São Bento n=5, Canto da Praia n=9) — alguns têm
   p25=0 e mediana instável; os rankings conclusivos são Meia Praia, Centro, Morretes, Tabuleiro,
   Casa Branca, Ilhota, Sertaozinho.
5. **Amenities correlacionam com tamanho** — piscina/varanda aparecem em unidades maiores
   (delta negativo não significa "ter piscina piora receita" isoladamente). Controle na Fase 4.

## Achados preliminares
- **Receita por quartos é monotônica crescente** (studio R$~0 n=8; 1q R$1.927 n=144; 2q R$2.485;
  3q R$3.134; 4q+ R$6.751). Mas **não é o critério**: maçores gastam muito mais em compra (R$/m² similar),
  o que tende a destruir o yield — o critério-mestre será aplicado na Fase 5 (a tese dos compactos
  justamente alega que 1q no Centro tem yield melhor, não receita absoluta).
- **Centro 1q: n=79, receita R$2.251/mês** — amostra forte para a tese dos compactos. Meia Praia 1q
  n=29 R$1.931, Morretes 1q n=5 R$1.924 serão contrafactual na Fase 5.
- **Vista-mar gera +48% de receita** (n_pres=153) e ocorrência concentra-me; AR-condicionado/TV/cozinha
  têm deltas altos porém com n_aus pequeno (podem ser proxy de "anúncio completo"). A Fase 4 vai controlar.
- **Hosts profissionais não recebem mais por anúncio** (mediana similar: 2.694 vs 2.602), mas
  concentram 171 anúncios em 14 hosts ("11+") — o mercado tem escala, e a Seazone em canais é exatamente
  este operador.

## Entregáveis
`output/fase3_*` (tabelas CSV/JSON, relatório MD, 5 PNGs) e `output/fase3_base_receita.csv`.