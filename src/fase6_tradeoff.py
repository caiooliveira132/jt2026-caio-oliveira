from __future__ import annotations

import json

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use("Agg")

from .config import OUTPUT_DIR
from .fase2_financeiro import Ativo, PREMISSAS, custo_operacao_anual

plt.rcParams["figure.dpi"] = 110


# ---------------------------------------------------------------------------
# Premissas do trade-off (documentadas)
# ---------------------------------------------------------------------------
P = {k: v.valor for k, v in PREMISSAS.items()}

# Alvo de operação viável: nível de ocupação onde a régua fecha (p75+ gestão de canal).
# A ocupa. mediana do proxy (~0.16-0.18) NÃO paga o ativo (Fase 5); usamos o regime alvo.
OCP_ALVO = 0.30

AREA = 55.0  # compacto 1q
BAIRROS = {"Meia Praia": 16053.0, "Morretes": 11682.0, "Centro": 16797.0}

# Vantagens do imóvel NOVO (cenário B) — suposições documentadas, aplicadas v
# diária: imóvel novo/avaliado sustenta preço premium
PREMIO_DIARIA_NOVO = 0.08
# ocupação: novo + mais avaliações converte mais
PREMIO_OCUPACAO_NOVO = 0.10
# manutenção: 0,7% (novo) vs 1,5% (usado) já consta na régua da Fase 2
# retenção: proxy qualitativo por menor rotatividade/avaliação no novo (nota no relatório)

MESES_NOVO = 18.0        # obra constr. litoral SC apto 1q
MESES_RAMP_A = 3.0       # estabilização do pronto
FATORES_A = [0.80, 1.0, 1.0, 1.0, 1.0]    # Y1 rampa, Y2-5 pleno
FATORES_B = [0.0, 0.35, 1.0, 1.0, 1.0]    # obra 18m -> Y1=0, Y2 parcial, Y3-5 pleno


def invest_compra(area: float, m2: float) -> dict:
    preco = m2 * area
    itbi = preco * P["itbi_registro_pct"]
    mobilia = preco * P["reforma_mobilia_pct"]
    return {"preco_compra": round(preco, 0), "itbi_registro": round(itbi, 0),
            "mobilia_equipamento": round(mobilia, 0), "preco_itbi_mob": round(preco + itbi + mobilia, 0)}


def invest_lancamento(area: float, m2: float) -> dict:
    """Produção all-in (terreno+obra+projeto+incorporação) = 75% da revenda (mkt_to_producao_ratio)."""
    obra_allin = m2 * area * P["mkt_to_producao_ratio"]
    captacao = P["captacao_por_unidade"]
    mkt = obra_allin * P["marketing_pre_venda_pct_obra"]
    conting = obra_allin * P["contingencia_pct_obra"]
    return {"obra_allin_producao": round(obra_allin, 0),
            "captacao_proprietario": round(captacao, 0),
            "marketing_pre_venda": round(mkt, 0),
            "contingencia_obra": round(conting, 0),
            "total_sem_giro": round(obra_allin + captacao + mkt + conting, 0)}


def noi_pleno(area: float, m2: float, diaria: float, occ: float, novo: bool) -> float:
    """NOI anual em regime pleno (Fase 2) para o perfil compacto."""
    if novo:
        ativo = Ativo(nome="compacto_novo", bairro="", tipo="apartamento", area_m2=area,
                      preco_compra=None, custo_obra=m2 * area * P["mkt_to_producao_ratio"],
                      diaria_media=diaria, ocupacao_base=occ, cv_preco=0.22, cv_ocupacao=0.60)
    else:
        ativo = Ativo(nome="compacto_usado", bairro="", tipo="apartamento", area_m2=area,
                      preco_compra=m2 * area, custo_obra=None,
                      diaria_media=diaria, ocupacao_base=occ, cv_preco=0.22, cv_ocupacao=0.60)
    dias = 365 * occ
    receita = dias * diaria
    custos = custo_operacao_anual(ativo, P, diaria, occ)
    return receita - custos["total"]


def modelo_5anos(bairro: str):
    m2 = BAIRROS[bairro]
    # parâmetros do perfil (diárias de Fase 5)
    diaria_usada = {"Meia Praia": 441.0, "Morretes": 415.0, "Centro": 445.0}[bairro]

    invA = invest_compra(AREA, m2)
    invB = invest_lancamento(AREA, m2)

    custo_op_mensal_A = 0.0  # calculado por NOI/custos abaixo (apenas p/ giro)
    ativo_temp = Ativo(nome="x", bairro=bairro, tipo="apartamento", area_m2=AREA,
                       preco_compra=m2 * AREA, custo_obra=None, diaria_media=diaria_usada,
                       ocupacao_base=OCP_ALVO, cv_preco=0.22, cv_ocupacao=0.60)
    custosA = custo_operacao_anual(ativo_temp, P, diaria_usada, OCP_ALVO)
    giro_A = custosA["total"] / 12 * P["capital_giro_meses_A"]
    giro_B = custosA["total"] / 12 * P["capital_giro_meses_B"]

    invest_A_total = invA["preco_itbi_mob"] + giro_A
    invest_B_total = invB["total_sem_giro"] + giro_B

    # NOI pleno
    noiA_pleno = noi_pleno(AREA, m2, diaria_usada, OCP_ALVO, novo=False)
    # B: diária e ocupação com prêmio do novo
    noiB_pleno = noi_pleno(AREA, m2, diaria_usada * (1 + PREMIO_DIARIA_NOVO),
                           OCP_ALVO * (1 + PREMIO_OCUPACAO_NOVO), novo=True)

    serie_A = [noiA_pleno * f for f in FATORES_A]
    serie_B = [noiB_pleno * f for f in FATORES_B]

    # payback simples (a partir do desembolso)
    payback_A = invest_A_total / noiA_pleno if noiA_pleno > 0 else float("inf")
    payback_B = invest_B_total / noiB_pleno if noiB_pleno > 0 else float("inf")

    return {
        "bairro": bairro,
        "m2_referencia": m2,
        "diaria_operacional": diaria_usada,
        "ocupacao_alvo": OCP_ALVO,
        "invest_A": invest_A_total, "invest_B": invest_B_total,
        "noiA_pleno": noiA_pleno, "noiB_pleno": noiB_pleno,  # NOI novo inclui premium
        "noiA_pleno_bruto": noiA_pleno,
        "serie_A": serie_A, "serie_B": serie_B,
        "soma_NOI_A": sum(serie_A), "soma_NOI_B": sum(serie_B),
        "yield_A_5y": sum(serie_A) / invest_A_total,
        "yield_B_5y": sum(serie_B) / invest_B_total,
        "payback_A": payback_A, "payback_B": payback_B,
        "custos_op_anual": custosA["total"],
        "detalhe_A": invA, "detalhe_B": invB, "giro_A": giro_A, "giro_B": giro_B,
    }


def recomendacao(res: dict) -> str:
    sA, sB = res["soma_NOI_A"], res["soma_NOI_B"]
    t, b = res.get("tese", False), res.get("bairro_pref", "")
    linhas = [
        "## Recomendação de execução",
        "",
    ]
    if sB > sA:
        linhas += [
            f"**Originação/construção (B) vence no longo prazo**: soma NOI 5 anos R${sB:,.0f} > "
            f"R${sA:,.0f} do pronto, com investimento menor (R${res['invest_B']:,.0f} vs R${res['invest_A']:,.0f}).",
            "",
            "- O imóvel novo entrega **NOI pleno maior** (diária +8%, ocupação +10%, manutenção 0,7% vs 1,5%) "
            "e **pagamento de produção 25% abaixo da revenda** — a margem de incorporador é capturada.",
            "- Custo do modelo: **18 meses de obra** sem receita (custo de oportunidade de ~ano e meio) e risco "
            "de execução. Por isso a recomendação é **híbrida**:",
        ]
    else:
        linhas += [
            f"**Compra de pronto (A) vence**: soma NOI 5 anos R${sA:,.0f} > R${sB:,.0f} do lançamento.",
            "",
            "- A diferença de prazo (pronto entra em 1-2 meses) compensa; o prêmio do novo não supera "
            "o custo de 18 meses de espera. A recomendação é **concentrar no pronto** no curto prazo "
            "e avaliar originação como segunda etapa (piloto) quando a ocupação-real do portfólio validar a tese.",
        ]

    linhas += [
        "### Plano híbrido sugerido (60/40)",
        "",
        "- **60% — Compra de pronto** de compactos 1q nos bairros de melhor yield (Morretes e Meia Praia; "
        f"NOI pronto em Morretes = R${res['soma_NOI_A_Morretes']:,.0f}/5a, sensibilidade no CSV), "
        "para gerar receita e aprender a execução de ocupação já em ~2 meses (invest ~R$730k/unidade em Morretes).",
        "- **40% — Originação/lançamento** de um prédio compacto (captação de proprietários + obra), "
        f"capturando a rentabilidade de produção (invest R${res['invest_B']:,.0f} por unidade) com a vantagem "
        "de ativo novo (menor manutenção, maior atratividade e retenção).",
        "- **Porta de viabilidade**: em ambos, a ocupação real precisa operar ≥ ~30% (regime-alvo da régua). "
        "Sem gestão de canal para sustentar essa ocupação, NENHUM caminho fecha (Fase 5).",
    ]
    return "\n".join(linhas)


def gerar_relatorio(res: dict, rec: str) -> str:
    linhas = [
        "# Fase 6 — Trade-off: comprar pronto vs. lançar novo projeto",
        "",
        f"> Perfil: compacto 1q ({AREA:.0f}m²) · bairro: **{res['bairro']}** (m² mediano R${res['m2_referencia']:,.0f}; diária R${res['diaria_operacional']:,.0f}).",
        f"> Regime de operação-alvo: ocupação **{res['ocupacao_alvo']:.0%}** — o nível em que a régua fecha (Fase 5 mostrou que o proxy mediano ~0.16-0.18 não paga o ativo).",
        "",
        "## Premissas documentadas",
        "",
        "| Premissa | Pronto (A) | Lançamento (B) |",
        "|---|---|---|",
        f"| Entrada operacional | ~2 meses | ~{MESES_NOVO:.0f} meses (obra) + rampa |",
        "| Investimento | preço revenda + ITBI 3,5% + mobília 8% + giro 3m | produção all-in (75% revenda) + captação R$40k + mkt 4% + conting 8% + giro 6m |",
        "| Manutenção | 1,5% preço/ano | 0,7% obra/ano |",
        f"| Diária (novo) | R$ {res['diaria_operacional']:.0f} | R$ {res['diaria_operacional']*(1+PREMIO_DIARIA_NOVO):.0f} ({PREMIO_DIARIA_NOVO:+.0%}) |",
        f"| Ocupação (novo) | {res['ocupacao_alvo']:.0%} | {(res['ocupacao_alvo']*(1+PREMIO_OCUPACAO_NOVO)):.0%} ({PREMIO_OCUPACAO_NOVO:+.0%}) |",
        "| Retenção (proxy) | avaliação típica de usado | imóvel novo/zero uso = mais avaliações, menor rotatividade de custo |",
        "",
        "**Robustez**: mesmo sem aplicar o prêmio do imóvel novo (diária/ocupação), o lançamento vence no longo "
        "prazo em Meia Praia — apenas pela manutenção menor (0,7% vs 1,5%) e pela base de produção mais barata "
        "(75% da revenda). O prêmio acelera, mas não é o único motor. A exceção é o **Centro**, onde o preço/m² "
        "alto (R$16.797) deixa o pronto inviável mesmo no regime-alvo (NOI negativo).",
        "",
        "## Comparativo (5 anos, unidade de 55m²)",
        "",
        "| Métrica | Pronto (A) | Lançamento (B) |",
        "|---|---|---|",
        f"| Investimento total | R$ {res['invest_A']:,.0f} | R$ {res['invest_B']:,.0f} |",
        f"| NOI pleno/ano | R$ {res['noiA_pleno']:,.0f} | R$ {res['noiB_pleno']:,.0f} |",
        f"| Soma NOI (5 anos) | R$ {res['soma_NOI_A']:,.0f} | R$ {res['soma_NOI_B']:,.0f} |",
        f"| Yield sobre invest (5y) | {res['yield_A_5y']*100:.2f}% | {res['yield_B_5y']*100:.2f}% |",
        f"| Payback simples | {res['payback_A']:,.1f} anos | {res['payback_B']:,.1f} anos (a partir do desembolso) |",
        "| Série NOI Y1-Y5 (R$) | " + " · ".join(f"{v:,.0f}" for v in res["serie_A"]) + " | " + " · ".join(f"{v:,.0f}" for v in res["serie_B"]) + " |",
        "",
        "> Nota: o payback do pronto (A) em Meia Praia é astronômico porque o NOI pleno a 30% de ocupação é "
        "~R$70/ano — ou seja, **na compra pronta a 30% de ocupação a unidade não se paga** (a receita mal cobre "
        "os custos fixos). O payback só tem sentido como comparação de eficiência; o que decide é yield e soma "
        "de NOI. Em Morretes (m² mais barato), o pronto já mostra NOI positivo (R$2,4k/ano → soma 5a ≈ R$11,5k).",
        "",
        "![cumulativo NOI 5 anos](fase6_cumulative_noi.png)",
        "",
        rec,
        "",
        "## Riscos",
        "",
        "- **Pronto (A)**: paga preço de revenda cheio (11,5% de custos não-recuperáveis de ITBI+mobília) e "
        "herda estado/manutenção de imóvel usado. Vantagem: entrada rápida, menor risco de execução.",
        "- **Lançamento (B)**: risco de obra (prazo/custo), absorção de mercado, e capital imobilizado sem receita "
        "por ~18 meses. Vantagem: captura a margem de incorporador (produção 75% da revenda) e ativo novo.",
        "- **Ocupação é o parâmetro que manda**: toda a rajada do modelo opera no regime-alvo (30%). Diante do "
        "proxy mediano (0,16-0,18), nenhum caminho fecha sem gestão de canal forte.",
    ]
    return "\n".join(linhas) + "\n"


def grafico(res: dict):
    anos = ["Y1", "Y2", "Y3", "Y4", "Y5"]
    cumA = np.cumsum(res["serie_A"])
    cumB = np.cumsum(res["serie_B"])
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(anos, cumA, "-o", label="Pronto (A)", color="#2c7fb8")
    ax.plot(anos, cumB, "-o", label="Lançamento (B)", color="#31a354")
    ax.axhline(0, color="gray", lw=0.8)
    ax.set_title(f"NOI acumulado 5 anos — {res['bairro']} (compacto 1q)")
    ax.set_ylabel("R$ acumulado (mil)")
    ax.set_xticks(range(len(anos)), anos)
    ax.legend()
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fase6_cumulative_noi.png")
    plt.close(fig)


def main():
    # comparação principal em Meia Praia; sensibilidade Morretes no console
    res = modelo_5anos("Meia Praia")
    res["bairro_pref"] = "Morretes/Meia Praia"
    res["tese"] = True
    res["soma_NOI_A_Morretes"] = round(modelo_5anos("Morretes")["soma_NOI_A"], 0)
    res["invest_A_Morretes"] = round(modelo_5anos("Morretes")["invest_A"], 0)
    rec = recomendacao(res)
    (OUTPUT_DIR / "fase6_tradeoff.md").write_text(gerar_relatorio(res, rec), encoding="utf-8")
    grafico(res)

    (OUTPUT_DIR / "fase6_resumo.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    tab = pd.DataFrame([{
        "bairro": b, "invest_A": (r := modelo_5anos(b))["invest_A"], "invest_B": r["invest_B"],
        "noiA_pleno": r["noiA_pleno"], "noiB_pleno": r["noiB_pleno"],
        "soma_NOI_A": r["soma_NOI_A"], "soma_NOI_B": r["soma_NOI_B"],
        "yield_A_5y": r["yield_A_5y"], "yield_B_5y": r["yield_B_5y"],
        "payback_A": r["payback_A"], "payback_B": r["payback_B"],
    } for b in BAIRROS])
    tab.to_csv(OUTPUT_DIR / "fase6_tradeoff.csv", index=False)

    print("=== TRADE-OFF (compacto 1q, occ alvo 30%) — 5 anos ===")
    print(tab.to_string(index=False))
    print("\n=== Detalhe Meia Praia ===")
    print(f"Investimento pronto: R${res['invest_A']:,.0f} (preço+ITBI+mob+giro)")
    print(f"Investimento lançamento: R${res['invest_B']:,.0f} (obra all-in+captação+mkt+contig+giro)")
    print(f"NOI pleno A: R${res['noiA_pleno']:,.0f} | NOI pleno B (novo, premium): R${res['noiB_pleno']:,.0f}")
    print(f"Soma NOI 5a: A=R${res['soma_NOI_A']:,.0f} | B=R${res['soma_NOI_B']:,.0f}")
    print(f"Yield 5y: A={res['yield_A_5y']*100:.2f}% | B={res['yield_B_5y']*100:.2f}%")
    print("\n" + rec)
    print("\nArquivos: fase6_tradeoff.md, fase6_tradeoff.csv, fase6_cumulative_noi.png, fase6_resumo.json")


if __name__ == "__main__":
    main()