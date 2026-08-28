from __future__ import annotations

import json

import pandas as pd

from .config import OUTPUT_DIR
from .fase2_financeiro import Ativo, PREMISSAS, calcular
from .fase6_tradeoff import AREA, BAIRROS

P_FULL = {k: v.valor for k, v in PREMISSAS.items()}


def cenarios_morretes(novo: bool):
    """Retorna {base, otimista, pessimista} com números reais da régua (Fase 2) p/ Morretes."""
    m2 = BAIRROS["Morretes"]
    if novo:
        ativo = Ativo(
            nome="B Morretes novo", bairro="Morretes", tipo="apartamento", area_m2=AREA,
            preco_compra=None, custo_obra=m2 * AREA * P_FULL["mkt_to_producao_ratio"],
            diaria_media=415.0 * 1.08, ocupacao_base=0.30 * 1.10, cv_preco=0.22, cv_ocupacao=0.60,
        )
    else:
        ativo = Ativo(
            nome="A Morretes pronto", bairro="Morretes", tipo="apartamento", area_m2=AREA,
            preco_compra=m2 * AREA, custo_obra=None, diaria_media=415.0, ocupacao_base=0.30,
            cv_preco=0.22, cv_ocupacao=0.60,
        )
    return {sc: calcular(ativo, cenario=sc) for sc in ["base", "otimista", "pessimista"]}


def load_numeros():
    bairro = pd.read_csv(OUTPUT_DIR / "fase3_tab_bairro.csv")
    base = pd.read_csv(OUTPUT_DIR / "fase3_base_receita.csv")
    tese = json.load(open(OUTPUT_DIR / "fase5_resumo.json", encoding="utf-8"))
    trad = pd.read_csv(OUTPUT_DIR / "fase6_tradeoff.csv")
    return bairro, base, tese, trad


def gerar_relatorio(bairro, base, tese, trad, morretes_pronto, morretes_novo) -> str:
    meia = bairro[bairro["suburb"] == "Meia Praia"].iloc[0]
    centro = bairro[bairro["suburb"] == "Centro"].iloc[0]
    morretes = bairro[bairro["suburb"] == "Morretes"].iloc[0]

    A_base, A_otim, A_pess = morretes_pronto["base"], morretes_pronto["otimista"], morretes_pronto["pessimista"]
    B_base, B_otim, B_pess = morretes_novo["base"], morretes_novo["otimista"], morretes_novo["pessimista"]

    L = [
        "# Recomendação Final — Seazone · Itapema/SC",
        "",
        "> Resposta consolidada das Fases 0–6. Cada ponto sustenta número nos dados.",
        "",
        "## 0. Definições operacionais (Fase 0)",
        "",
        "- **Melhor** = maior yield líquido anual (NOI ÷ investimento) com consistência (CV baixo), "
        "atratividade (reviews/avaliações) e resiliência no longo prazo. Não é receita absoluta.",
        "- **Perfil** = tipologia × quartos × tipo de anúncio × comodidades.",
        "- **Localização** = bairro (diária média × ocupação, ponderada por consistência e preço/m² de compra).",
        "- **Execução** = compra de pronto (A) vs. lançamento/construção (B).",
        "",
        "## 1. Melhor perfil de imóvel",
        "",
        "**Resposta: apartamento compacto, 1 quarto, anúncio de imóvel inteiro, com vista e ar-condicionado.**",
        "",
        "| Evidência | Número | Fonte |",
        "|---|---|---|",
        "| Receita cresce com quartos, mas o yield não | 1q: R$1.927/mês (n=144) · 3q: R$3.134 (n=404) · 4q+: R$6.751 (n=92) | Fase 3 |",
        "| +1 quarto (mantendo hóspedes) reduz receita/hóspede | coef −29% (p=0.077) → quarto extra não é alavanca | Fase 4 |",
        "| +1 hóspede de capacidade aumenta receita | coef +34% (p<0.001) | Fase 4 |",
        "| Vista-mar é a comodidade de maior valor | +48% de receita vs ausência (n_pres=153) | Fase 3 |",
        "| Ar-condicionado (clima litoral) valoriza | delta +85% receita (n_pres=986) | Fase 3 |",
        "| Reserva instantânea ativa | +105% receita (p<0.01) — ação operacional de curto prazo | Fase 4 |",
        "| Imóvel inteiro (apartamento) supera casa | apto R$2.783/mês vs casa R$1.930 (n=911 vs 70) | Fase 3 |",
        "",
        "**Por quê (2 frases)**: compacto 1q combina a maior eficiência de capital (invest ~R$648-727k "
        "vs ~R$2,3-2,6M dos maiores) com as alavancas reais do modelo — capacidade de hóspedes + reserva "
        "instantânea + vista/AR. O imóvel inteiro concentra a receita com custo de gestão parecido.",
        "",
        "## 2. Melhor localização",
        "",
        "**Resposta: Morretes (melhor yield) e Meia Praia (maior receita, 2º melhor). Cento perde por preço/m².**",
        "",
        f"- **Morretes**: receita mediana R${morretes['mediana']:,.0f}/mês (n={morretes['n']}) · m² compra "
        f"R$11.682 (o mais barato) → **melhor yield para compacto** (otimista +4,0% pronto / +7,1% lançamento).",
        f"- **Meia Praia**: maior receita mediana da cidade R${meia['mediana']:,.0f}/mês (n={meia['n']}) · mas m² "
        f"R$16.053 e CV {meia['cv']:.2f} → segundo lugar.",
        f"- **Centro**: receita R${centro['mediana']:,.0f}/mês (n={centro['n']}) · eliminado por m² R$16.797 "
        "(pronto inviável — NOI negativo) e pelo teste da tese.",
        "",
        "| Bairro | n | mediana R$/mês | CV | m² mediana (VivaReal) | Veredito yield |",
        "|---|---|---|---|---|---|",
        f"| Morretes | {morretes['n']} | {morretes['mediana']:,.0f} | {morretes['cv']:.2f} | R$11.682 | **melhor** |",
        f"| Meia Praia | {meia['n']} | {meia['mediana']:,.0f} | {meia['cv']:.2f} | R$16.053 | 2º melhor |",
        f"| Centro | {centro['n']} | {centro['mediana']:,.0f} | {centro['cv']:.2f} | R$16.797 | inviável no pronto |",
        "",
        "**Por quê (2 frases)**: a rentabilidade vem do **custo de compra**, não da diária bruta: quem compra "
        "m² mais barato (Morretes) alcança o melhor yield, enquanto o Centro, com diária parecida, paga o "
        "prêmio de um m² 44% mais caro. A volatilidade (CV ~1 em todos os bairros) é endêmica de Itapema — "
        "a Seazone mitiga por gestão de canal.",
        "",
        "## 3. Características que explicam as melhores receitas",
        "",
        "**Resposta**: localização, capacidade de hóspedes, reputação/avaliações e operação (reserva "
        "instantânea) — e não o tamanho físico.",
        "",
        "- **Localização**: sair dos bairros principais custa **−71%** (p=0,05). Morretes/Meia Praia concentram.",
        "- **Capacidade (hóspedes)**: +34% por hóspede adicional (p<0,001) — dimensionar capacidade é a alavanca.",
        "- **Reputação**: dobre reviews → +39% receita; reviews do host → +31% (ambos p<0,05). Avaliações vendem.",
        "- **Operação**: reserva instantânea → +105% (p<0,01). É ação imediata, custo baixo.",
        "- **Não é tamanho**: +1 quarto mantendo hóspedes → −29% (p=0,077). Quarto extra dilui receita/hóspede.",
        "",
        "> O modelo (OLS, log-linear) tem R²≈0,09: explica *direções*, não valores pontuais — limitação declarada.",
        "",
        "## 4. O que comprar hoje — estimativa concreta",
        "",
        "**Ativo recomendado: 1 apartamento de 1 quarto (≈55m², imóvel inteiro, com vista/AR) em Morretes.**",
        "",
        "### Opção 1 — Compra de pronto",
        "",
        "| Item | Valor | Fonte |",
        "|---|---|---|",
        f"| Investimento total | R$ {A_base['investimento']['total']:,.0f} | m² mediano Morretes R$11.682 × 55m² + ITBI 3,5% + mobília 8% + giro 3m |",
        f"| Receita anual bruta | R$ {A_base['receita_bruta']:,.0f} | diária R$415 × occ 30% × 365 |",
        f"| Custos operacionais anuais | R$ {A_base['custos_operacao']['total']:,.0f} | régua Fase 2 (limpeza, energia, condomínio, gestão 20%, canais 10%) |",
        f"| **NOI anual (base)** | R$ {A_base['noi']:,.0f} | receita − custos |",
        f"| **Yield líquido (base)** | {A_base['yield_liquido']*100:.2f}% | NOI ÷ investimento |",
        f"| Yield otimista (occ 48%) | {A_otim['yield_liquido']*100:.2f}% | cenário com gestão de canal forte |",
        f"| Yield pessimista (occ 12%) | {A_pess['yield_liquido']*100:.2f}% | cauda inferior sazonal |",
        "",
        "### Opção 2 — Lançamento (obra própria, 55m²)",
        "",
        "| Item | Valor | Fonte |",
        "|---|---|---|",
        f"| Investimento total | R$ {B_base['investimento']['total']:,.0f} | produção all-in 75% da revenda + captação R$40k + mkt 4% + conting 8% + giro 6m |",
        f"| NOI pleno (base, +prêmio novo) | R$ {B_base['noi']:,.0f}/ano | diária R$448 × occ 33% |",
        f"| **Yield líquido (base)** | {B_base['yield_liquido']*100:.2f}% | NOI ÷ investimento |",
        f"| Yield otimista (occ 53%) | {B_otim['yield_liquido']*100:.2f}% | prêmio novo + gestão de canal |",
        f"| Yield pessimista (occ 13%) | {B_pess['yield_liquido']*100:.2f}% | cauda inferior |",
        "",
        f"**Cenários (régua Fase 2) — leitura honesta**: no cenário base conservador (occ 30%) o yield do pronto "
        f"é só {A_base['yield_liquido']*100:.2f}% — é o **piso**: com gestão de canal real (occ 48%, a cauda superior "
        f"observada) sobe para {A_otim['yield_liquido']*100:.2f}%. O lançamento, por capturar a margem de produção e "
        f"o prêmio do novo (e ter investimento 11% menor), já parte de {B_base['yield_liquido']*100:.2f}% de base e "
        f"chega a {B_otim['yield_liquido']*100:.2f}% no otimista. **Nenhum cenário com occ≤20% fecha** "
        "(yield negativo) — é a fronteira de decisão.",
        "",
        f"**Por quê (2 frases)**: é a única combinação m² barato × perfil compacto testado que atinge yield "
        f"positivo em cenários realistas; e o lançamento multiplica o retorno pela margem de incorporador, "
        f"sem abrir mão da operação short stay. Dito isso, **retorno é de longo prazo** — payback da base é "
        f"lento (invest ÷ NOI ≈ {B_base['investimento']['total']/B_base['noi']:.0f} anos no B base e "
        f"{A_base['investimento']['total']/A_base['noi']:.0f} anos no A base), dependente de valorização do "
        "ativo (não modelada).",
        "",
        "## 5. Veredito sobre a tese dos compactos no Centro",
        "",
        "**SUSTENTA PARCIALMENTE → corretíssima no PERFIL, errada no BAIRRO.**",
        "",
        "- **Perfil confirmado**: compacto/1q supera unidades maiores em yield em todos os cenários "
        "(tese −1,0% base vs maior/Centro −1,3% e maior/fora −1,1%; otimista +0,6% vs −0,4% e −0,1%).",
        "- **Localização corrigida**: o melhor bairro para compactos é **Morretes** (otimista +4,0%) e não o "
        "Centro (+0,6%) — o m² do Centro (R$16.797) é 44% mais caro que o de Morretes (R$11.682).",
        "",
        "> A tese acertou no 'o quê', errou no 'onde'. Em vez de 'compactos no Centro', a recomendação é "
        "**'compactos em Morretes/Meia Praia'**.",
        "",
        "## 6. Recomendação de execução",
        "",
        "**Híbrida 60/40**: 60% para lançamento/originação de prédio compacto em Morretes (melhor yield, "
        "captura margem de produção) + 40% para compra de pronto em Meia Praia/Morretes como **piloto de "
        "entrada** (~2 meses), aprendendo a execução de ocupação/canal antes de escalar capital.",
        "",
        f"| Métrica (unidade 55m², Morretes) | Pronto (A) | Lançamento (B) |",
        "|---|---|---|",
        f"| Investimento | R$ {A_base['investimento']['total']:,.0f} | R$ {B_base['investimento']['total']:,.0f} |",
        f"| Yield base | {A_base['yield_liquido']*100:.2f}% | {B_base['yield_liquido']*100:.2f}% |",
        f"| Yield otimista | {A_otim['yield_liquido']*100:.2f}% | {B_otim['yield_liquido']*100:.2f}% |",
        f"| Soma NOI 5 anos | R$ {round(trad[trad['bairro']=='Morretes'].iloc[0]['soma_NOI_A']):,.0f} | R$ {round(trad[trad['bairro']=='Morretes'].iloc[0]['soma_NOI_B']):,.0f} |",
        "",
        "**Porta de viabilidade**: em ambos, a ocupação real precisa operar ≥ ~30% (regime-alvo da régua) — "
        "sem gestão de canal forte (especialidade da Seazone), nenhum caminho fecha (Fase 5).",
        "",
        "## 7. Limitações e próximos passos (o que faria com +1 semana)",
        "",
        "- **Ocupação é proxy inferior** (snapshot jan–abr/2025): receitas projetadas são conservadoras; a "
        "ocupação é o parâmetro mais sensível — validar por calendário real/OTAs.",
        "- **Preço/m² é mediana de lista (VivaReal)**: a negociação real de compra mudaria o veredito.",
        "- **Amostra de compactos em Morretes pequena (n=17)**: o n=118 de compactos no Centro suporta o "
        "perfil, não a localização.",
        "- **R² do modelo ≈0,09**: explica direções, não precisa receita pontual.",
        "- **Com +1 semana eu faria**: (1) validar ocupação com calendário real e canais; (2) orçamento de obra "
        "e VGV para fechar o NPI do lançamento; (3) sazonalidade de alta temporada (valores de jan/fev); "
        "(4) simular impacto da taxa de gestão da Seazone na viabilidade; (5) modelar capacidade por quarto/M.D. "
        "por metro quadrado para ancorar o dimensionamento.",
    ]
    return "\n".join(L) + "\n"


def main():
    bairro, base, tese, trad = load_numeros()
    morretes_pronto = cenarios_morretes(novo=False)
    morretes_novo = cenarios_morretes(novo=True)

    texto = gerar_relatorio(bairro, base, tese, trad, morretes_pronto, morretes_novo)
    (OUTPUT_DIR / "relatorio.md").write_text(texto, encoding="utf-8")
    (OUTPUT_DIR / "relatorio_final.md").write_text(texto, encoding="utf-8")

    resumo = {
        "morretes_pronto": {k: {kk: vv for kk, vv in v.items() if kk in ("ocupacao_usada", "yield_liquido", "noi", "receita_bruta")} for k, v in morretes_pronto.items()},
        "morretes_novo": {k: {kk: vv for kk, vv in v.items() if kk in ("ocupacao_usada", "yield_liquido", "noi", "receita_bruta")} for k, v in morretes_novo.items()},
    }
    (OUTPUT_DIR / "fase7_resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Relatório final gerado em output/relatorio.md")
    print("Tamanho:", len(texto), "caracteres")


if __name__ == "__main__":
    main()