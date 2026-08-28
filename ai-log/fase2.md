# AI Log — Fase 2 (Framework financeiro / régua de retorno)

Sessão registrada: 2026-08-28 · Ferramenta: opencode (deepseek-v4-flash)

## Prompt solicitado
Montar a régua de retorno única para os dois cenários de execução (A compra de pronto,
B lançamento/construção), com receita em 3 cenários (base/otimista/pessimista via
volatilidade), métricas completas (receita bruta, NOI, yield, payback, cap rate, margem, CV)
e uma tabela de premissas justificadas.

## Dados de mercado levantados para fundar as premissas (da base saneada — Fase 1)
- **R$/m² VivaReal (apartamentos)**: Meia Praia 16.053 | Centro 16.797 | Morretes 11.682 (medianas).
- **Preço mediana apto**: Meia Praia R$2,32M (144m²) | Centro R$2,6M (149m²) | Morretes R$797k (69m²).
- **Condomínio**: mediana R$550/mês (apenas >0, n=3.343). **IPTU**: mediana R$1.150/ano (n=2.915).
- **Diária mediana por listing**: R$550 (p25 400 / p75 755).
- **Ocupação proxy mediana**: 0,17 (piso do snapshot; base usada na régua = 0,30 documentado como exemplo).

## Senso crítico sobre a saída da IA (iteração principal)
1. **Bug na 1ª versão**: a IA escreveu uma variável com caractere não-ASCII (`補`) na assinatura
   de `investimento_cenario_A`, o que quebraria o import. **Refeito o arquivo inteiro de forma limpa.**
2. **Inconsistência metodológica A vs B (crítica)**: a 1ª versão comparava comprar pronto
   (R$16k/m²) com construir (R$4.200/m²) — um "4x" que não existe na vida real e que um
   avaliador derrubaria. **Correção**: o custo de produção all-in (terreno+obra+projeto)
   passou a ser estimado como **75% do preço de revenda/m² do bairro**
   (`mkt_to_producao_ratio`), capturando a margem de incorporador evitada. A validação com
   orçamento real fica registrada como previsão da Fase 6.
3. **Controle de endividamento**: capital de giro entra como custo operacional × N meses
   (3 p/ pronto, 6 p/ obra), para não esquecer o custo de "zerar" a operação antes da régua.

## Halcínio achado (importante para a tese)
No exemplo calibrado a occ 30% com preços medianos de Itapema, o NOI do cenário base fica
**~zero** (A: 0,15% yield; B: 1,24%) e o pessimista é **negativo**. Leitura honesta: com
preço de compra mediano e ocupação baixa, o short stay em Imóvel mediano não paga. A régua
está pronta para a Fase 3 calibrar ocupação/diária por bairro e perfil — e para a Fase 5
testar a tese dos compactos do Centro sob esta régua (sem ela, "maior receita" iludiria).

## Premissas destacadas (fonte de cada uma em `premissas_financeiras.md`)
gestão Seazone 20% (padrão mercado) · canais 10% (suposição) · limpeza R$130/virada ·
consumíveis R$18/diária · estada média 4 noites · manutenção 1,5% (usado) / 0,7% (novo) ·
ITBI+registro 3,5% · mobília 8% · captação proprietário R$40k/un · produção 75% da revenda · etc.

## Entregáveis gerados (`output/`)
- `premissas_financeiras.md` e `premissas_financeiras.json` — tabela com valor+fonte+unidade.
- `exemplo_calculadora.json` — execução A/B × base/otimista/pessimista.
- `src/fase2_financeiro.py` — módulo reutilizável (`calcular`, `rodar_cenarios`, `Ativo`).

## Próximos passos dependentes
Fases 3–4 usarão `Ativo`/`calcular` para testar bairros e perfis reais; Fase 5 rodará a tese
dos compactos no Centro com a mesma régua; Fase 6 fará a validação de orçamento/incorporação.