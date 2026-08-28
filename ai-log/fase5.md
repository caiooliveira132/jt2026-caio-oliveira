# AI Log — Fase 5 (Teste da tese dos compactos no Centro)

Sessão registrada: 2026-08-28 · Ferramenta: opencode (deepseek-v4-flash)

## Prompt solicitado
Testar a tese "apartamentos compactos (studio/1q) no Centro são a aposta mais eficiente" com a
régua financeira da Fase 2 (não só receita absoluta): 4 grupos (tese + contrafatos a/b/c),
custo de operação por tipologia, e veredito com números.

## Como foi feito
- Grupos: `tese_compacto_centro` (studio/1q apto no Centro) vs (a) compacto fora, (b) maior no
  Centro, (c) maior fora. + apoio compacto/Meia Praia e compacto/Morretes.
- Custos por tipologia integrados à régua: compacto = limpeza −20%, consumível −15%, energia −15%,
  condomínio menor; maior = condomínio/IPTU maiores.
- Preço de compra = m² mediano VivaReal do bairro × área do perfil.
- Ocupação = occ_proxy mediano do grupo (piso conservador) como base; otimista usa CV.
- Veredito computado por regra em 2 etapas (perfil → localização).

## Senso crítico sobre a saída (duas iterações grandes)
1. **Veredito automático inicial disse "SUSTENTA" só porque compacto/Centro era o 'menos pior'
   no cenário base (−1.04% vs −1.42/−1.26/−1.11)**. Refusei como resposta: todos os yields base são
   negativos; "sustenta" seria enganoso sem olhar a cauda. Incluí o cenário **otimista** (occ≈p75) e
   os **bairros de apoio**. Resultado honesto: **o perfil compacto é confirmado, mas a localização
   Centro falha** — Morretes (m² R$11.682, occ 0,24) chega a +3.42% otimista, bem acima do Centro
   (+0.64%). Veredito final: **SUSTENTA PARCIALMENTE**.
2. **Rigor**: a régua foi a mesma da Fase 2 com premissas por tipologia; documentei que preço de
   compra é mediação por m² (a negociação real alteraria o veredito).

## Números-chave (rendhead)
| Grupo | n | occ base | yield base | yield otimista |
|---|---|---|---|---|
| compacto/Centro (tese) | 118 | 0.18 | −1.04% | +0.64% |
| compacto/fora (a) | 144 | 0.15 | −1.42% | −0.06% |
| maior/Centro (b) | 430 | 0.14 | −1.26% | −0.42% |
| maior/fora (c) | 2960 | 0.18 | −1.11% | −0.10% |
| compacto/Meia Praia | 110 | 0.16 | −1.20% | +0.38% |
| compacto/Morretes | 17 | 0.24 | −0.01% | +3.42% |

## Consequência para a recomendação
- **Perfil**: compactos/1 quarto (eficiência de capital) — confirmado.
- **Localização**: o melhor bairro para o perfil é **Morretes/Meia Praia** (m² barato) e NÃO o Centro.
- **Nenhum grupo é viável na occ base (0.14–0.18)**: a ocupa. mediana do proxy não paga o ativo em
  Itapema com preços medianos. A viabilidade real depende de ocupação na cauda superior (gestão de
  canal) e/ou preço de compra abaixo da mediana. Isso direciona a recomendação final (Fase 7):
  entrar com a régua, focar gestão de ocupação, evitar preço mediano do Centro.

## Entregáveis
`output/fase5_tabela_confronto.csv`, `fase5_relatorio.md`, `fase5_veredito.png`, `fase5_resumo.json`.