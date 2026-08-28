# Recomendação Final — Seazone · Itapema/SC

> Resposta consolidada das Fases 0–6. Cada ponto sustenta número nos dados.

## 0. Definições operacionais (Fase 0)

- **Melhor** = maior yield líquido anual (NOI ÷ investimento) com consistência (CV baixo), atratividade (reviews/avaliações) e resiliência no longo prazo. Não é receita absoluta.
- **Perfil** = tipologia × quartos × tipo de anúncio × comodidades.
- **Localização** = bairro (diária média × ocupação, ponderada por consistência e preço/m² de compra).
- **Execução** = compra de pronto (A) vs. lançamento/construção (B).

## 1. Melhor perfil de imóvel

**Resposta: apartamento compacto, 1 quarto, anúncio de imóvel inteiro, com vista e ar-condicionado.**

| Evidência | Número | Fonte |
|---|---|---|
| Receita cresce com quartos, mas o yield não | 1q: R$1.927/mês (n=144) · 3q: R$3.134 (n=404) · 4q+: R$6.751 (n=92) | Fase 3 |
| +1 quarto (mantendo hóspedes) reduz receita/hóspede | coef −29% (p=0.077) → quarto extra não é alavanca | Fase 4 |
| +1 hóspede de capacidade aumenta receita | coef +34% (p<0.001) | Fase 4 |
| Vista-mar é a comodidade de maior valor | +48% de receita vs ausência (n_pres=153) | Fase 3 |
| Ar-condicionado (clima litoral) valoriza | delta +85% receita (n_pres=986) | Fase 3 |
| Reserva instantânea ativa | +105% receita (p<0.01) — ação operacional de curto prazo | Fase 4 |
| Imóvel inteiro (apartamento) supera casa | apto R$2.783/mês vs casa R$1.930 (n=911 vs 70) | Fase 3 |

**Por quê (2 frases)**: compacto 1q combina a maior eficiência de capital (invest ~R$648-727k vs ~R$2,3-2,6M dos maiores) com as alavancas reais do modelo — capacidade de hóspedes + reserva instantânea + vista/AR. O imóvel inteiro concentra a receita com custo de gestão parecido.

## 2. Melhor localização

**Resposta: Morretes (melhor yield) e Meia Praia (maior receita, 2º melhor). Cento perde por preço/m².**

- **Morretes**: receita mediana R$2,060/mês (n=83) · m² compra R$11.682 (o mais barato) → **melhor yield para compacto** (otimista +4,0% pronto / +7,1% lançamento).
- **Meia Praia**: maior receita mediana da cidade R$3,124/mês (n=632) · mas m² R$16.053 e CV 1.11 → segundo lugar.
- **Centro**: receita R$2,341/mês (n=205) · eliminado por m² R$16.797 (pronto inviável — NOI negativo) e pelo teste da tese.

| Bairro | n | mediana R$/mês | CV | m² mediana (VivaReal) | Veredito yield |
|---|---|---|---|---|---|
| Morretes | 83 | 2,060 | 1.06 | R$11.682 | **melhor** |
| Meia Praia | 632 | 3,124 | 1.11 | R$16.053 | 2º melhor |
| Centro | 205 | 2,341 | 1.05 | R$16.797 | inviável no pronto |

**Por quê (2 frases)**: a rentabilidade vem do **custo de compra**, não da diária bruta: quem compra m² mais barato (Morretes) alcança o melhor yield, enquanto o Centro, com diária parecida, paga o prêmio de um m² 44% mais caro. A volatilidade (CV ~1 em todos os bairros) é endêmica de Itapema — a Seazone mitiga por gestão de canal.

## 3. Características que explicam as melhores receitas

**Resposta**: localização, capacidade de hóspedes, reputação/avaliações e operação (reserva instantânea) — e não o tamanho físico.

- **Localização**: sair dos bairros principais custa **−71%** (p=0,05). Morretes/Meia Praia concentram.
- **Capacidade (hóspedes)**: +34% por hóspede adicional (p<0,001) — dimensionar capacidade é a alavanca.
- **Reputação**: dobre reviews → +39% receita; reviews do host → +31% (ambos p<0,05). Avaliações vendem.
- **Operação**: reserva instantânea → +105% (p<0,01). É ação imediata, custo baixo.
- **Não é tamanho**: +1 quarto mantendo hóspedes → −29% (p=0,077). Quarto extra dilui receita/hóspede.

> O modelo (OLS, log-linear) tem R²≈0,09: explica *direções*, não valores pontuais — limitação declarada.

## 4. O que comprar hoje — estimativa concreta

**Ativo recomendado: 1 apartamento de 1 quarto (≈55m², imóvel inteiro, com vista/AR) em Morretes.**

### Opção 1 — Compra de pronto

| Item | Valor | Fonte |
|---|---|---|
| Investimento total | R$ 727,158 | m² mediano Morretes R$11.682 × 55m² + ITBI 3,5% + mobília 8% + giro 3m |
| Receita anual bruta | R$ 45,442 | diária R$415 × occ 30% × 365 |
| Custos operacionais anuais | R$ 43,038 | régua Fase 2 (limpeza, energia, condomínio, gestão 20%, canais 10%) |
| **NOI anual (base)** | R$ 2,404 | receita − custos |
| **Yield líquido (base)** | 0.33% | NOI ÷ investimento |
| Yield otimista (occ 48%) | 4.02% | cenário com gestão de canal forte |
| Yield pessimista (occ 12%) | -2.23% | cauda inferior sazonal |

### Opção 2 — Lançamento (obra própria, 55m²)

| Item | Valor | Fonte |
|---|---|---|
| Investimento total | R$ 647,600 | produção all-in 75% da revenda + captação R$40k + mkt 4% + conting 8% + giro 6m |
| NOI pleno (base, +prêmio novo) | R$ 14,579/ano | diária R$448 × occ 33% |
| **Yield líquido (base)** | 2.25% | NOI ÷ investimento |
| Yield otimista (occ 53%) | 7.14% | prêmio novo + gestão de canal |
| Yield pessimista (occ 13%) | -1.21% | cauda inferior |

**Cenários (régua Fase 2) — leitura honesta**: no cenário base conservador (occ 30%) o yield do pronto é só 0.33% — é o **piso**: com gestão de canal real (occ 48%, a cauda superior observada) sobe para 4.02%. O lançamento, por capturar a margem de produção e o prêmio do novo (e ter investimento 11% menor), já parte de 2.25% de base e chega a 7.14% no otimista. **Nenhum cenário com occ≤20% fecha** (yield negativo) — é a fronteira de decisão.

**Por quê (2 frases)**: é a única combinação m² barato × perfil compacto testado que atinge yield positivo em cenários realistas; e o lançamento multiplica o retorno pela margem de incorporador, sem abrir mão da operação short stay. Dito isso, **retorno é de longo prazo** — payback da base é lento (invest ÷ NOI ≈ 44 anos no B base e 302 anos no A base), dependente de valorização do ativo (não modelada).

## 5. Veredito sobre a tese dos compactos no Centro

**SUSTENTA PARCIALMENTE → corretíssima no PERFIL, errada no BAIRRO.**

- **Perfil confirmado**: compacto/1q supera unidades maiores em yield em todos os cenários (tese −1,0% base vs maior/Centro −1,3% e maior/fora −1,1%; otimista +0,6% vs −0,4% e −0,1%).
- **Localização corrigida**: o melhor bairro para compactos é **Morretes** (otimista +4,0%) e não o Centro (+0,6%) — o m² do Centro (R$16.797) é 44% mais caro que o de Morretes (R$11.682).

> A tese acertou no 'o quê', errou no 'onde'. Em vez de 'compactos no Centro', a recomendação é **'compactos em Morretes/Meia Praia'**.

## 6. Recomendação de execução

**Híbrida 60/40**: 60% para lançamento/originação de prédio compacto em Morretes (melhor yield, captura margem de produção) + 40% para compra de pronto em Meia Praia/Morretes como **piloto de entrada** (~2 meses), aprendendo a execução de ocupação/canal antes de escalar capital.

| Métrica (unidade 55m², Morretes) | Pronto (A) | Lançamento (B) |
|---|---|---|
| Investimento | R$ 727,158 | R$ 647,600 |
| Yield base | 0.33% | 2.25% |
| Yield otimista | 4.02% | 7.14% |
| Soma NOI 5 anos | R$ 11,542 | R$ 48,839 |

**Porta de viabilidade**: em ambos, a ocupação real precisa operar ≥ ~30% (regime-alvo da régua) — sem gestão de canal forte (especialidade da Seazone), nenhum caminho fecha (Fase 5).

## 7. Limitações e próximos passos (o que faria com +1 semana)

- **Ocupação é proxy inferior** (snapshot jan–abr/2025): receitas projetadas são conservadoras; a ocupação é o parâmetro mais sensível — validar por calendário real/OTAs.
- **Preço/m² é mediana de lista (VivaReal)**: a negociação real de compra mudaria o veredito.
- **Amostra de compactos em Morretes pequena (n=17)**: o n=118 de compactos no Centro suporta o perfil, não a localização.
- **R² do modelo ≈0,09**: explica direções, não precisa receita pontual.
- **Com +1 semana eu faria**: (1) validar ocupação com calendário real e canais; (2) orçamento de obra e VGV para fechar o NPI do lançamento; (3) sazonalidade de alta temporada (valores de jan/fev); (4) simular impacto da taxa de gestão da Seazone na viabilidade; (5) modelar capacidade por quarto/M.D. por metro quadrado para ancorar o dimensionamento.
