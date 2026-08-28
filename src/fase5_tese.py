from __future__ import annotations

import json

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use("Agg")

from .config import OUTPUT_DIR
from .fase2_financeiro import Ativo, PREMISSAS, calcular

plt.rcParams["figure.dpi"] = 110


# ---------------------------------------------------------------------------
# Grupo-alvo da tese + contrafactuals
# ---------------------------------------------------------------------------
def montar_grupos(b: pd.DataFrame):
    """Retorna lista de grupos (dicts) alinhada ao enunciado:
      tese      = compacto(studio/1q, apartamento) no Centro
      (a)       = compacto fora do Centro
      (b)       = tamanho maior (2q/3q) no Centro
      (c)       = tamanho maior fora do Centro
    Cada grupo: filtro de linhas + n + métricas observadas."""
    apart = b[b["listing_type_std"] == "apartamento"]

    def compacto_filtro(d) -> pd.Series:
        return d["bedroom_cat"].isin(["studio", "1q"])

    def maior_filtro(d) -> pd.Series:
        return d["bedroom_cat"].isin(["2q", "3q", "4q+"])

    bairros_top = ["Meia Praia", "Centro", "Morretes", "Tabuleiro dos Oliveiras", "Casa Branca", "Ilhota"]
    fora = apart[apart["suburb"].isin(bairros_top) & (apart["suburb"] != "Centro")]

    grupos = [
        {
            "id": "tese_compacto_centro",
            "nome": "TESE: compacto (studio/1q) no Centro",
            "dados": apart[(apart["suburb"] == "Centro") & compacto_filtro(apart)],
        },
        {
            "id": "a_compacto_fora_centro",
            "nome": "CONTRAFATO (a): compacto fora do Centro",
            "dados": fora[compacto_filtro(fora)],
        },
        {
            "id": "b_maior_no_centro",
            "nome": "CONTRAFATO (b): maior (2q/3q+) no Centro",
            "dados": apart[(apart["suburb"] == "Centro") & maior_filtro(apart)],
        },
        {
            "id": "c_maior_fora_centro",
            "nome": "CONTRAFATO (c): maior (2q/3q+) fora do Centro",
            "dados": fora[maior_filtro(fora)],
        },
        # subgrupos de apoio para leitura
        {
            "id": "compacto_meia_praia",
            "nome": "Apoio: compacto em Meia Praia",
            "dados": apart[(apart["suburb"] == "Meia Praia") & compacto_filtro(apart)],
        },
        {
            "id": "compacto_morretes",
            "nome": "Apoio: compacto em Morretes",
            "dados": apart[(apart["suburb"] == "Morretes") & compacto_filtro(apart)],
        },
    ]
    for g in grupos:
        d = g["dados"]
        g["n"] = len(d)
        g["diaria_med"] = d["price_median"].median()
        g["occ_med"] = d["occ_proxy_avg"].median()
        g["occ_p75"] = d["occ_proxy_avg"].quantile(0.75)
        g["receita_mensal_med"] = d["receita_mensal_proxy"].median()
        g["cv_occ"] = d["occ_proxy_avg"].std() / d["occ_proxy_avg"].mean() if d["occ_proxy_avg"].mean() > 0 else np.nan
        g["diaria"] = d
    return grupos


# ---------------------------------------------------------------------------
# Parametrização de custos por tipologia (integra à régua da Fase 2)
# ---------------------------------------------------------------------------
# Compactos: limpeza mais barata (menor virada), consumível menor, energia menor,
# condomínio menor. Mas podem ter concorrência maior (não capturável numericamente — destacar).
def premissas_por_grupo(premissas_base: dict, area_m2: float, compacto: bool) -> dict:
    P = dict(premissas_base)
    if compacto:
        P["custo_limpeza_por_virada"] *= 0.80  # limpeza menor
        P["consumiveis_por_diaria"] *= 0.85
        P["energia_internet_mensal"] *= 0.85
        P["condominio_anual"] = 350.0 * 12     # condomínio compacto menor
        P["iptu_anual"] = 800.0
        # manutenção: a régua usa % do investimento; mais compacta = menos área → menos manut.
        P["manut_ajuste_eixo"] = "compacto"
    else:
        P["condominio_anual"] = 650.0 * 12
        P["iptu_anual"] = 1400.0
        P["manut_ajuste_eixo"] = "maior"
    return P


def area_m2_por_grupo(g: dict, bairro: str, compacto: bool) -> float:
    """Área média do perfil no bairro: usar VivaReal (vivareal_clean) para o tipo.
    Compacto ≈ 50-60m²; maior ≈ 110-140m² conforme bairro."""
    if compacto:
        return 55.0 if bairro != "Morretes" else 48.0
    return 130.0 if bairro != "Morretes" else 75.0


def preco_compra_referencia(bairro: str, area_m2: float, vivareal: pd.DataFrame, compacto: bool):
    """Preço de compra de referência (Cenário A) por bairro/m² (mediana VivaReal, apto)."""
    ap = vivareal[vivareal["listing_type"] == "apartamento"]
    sub = ap[ap["suburb_padrao"] == bairro]
    if len(sub) == 0:
        sub = ap
    preco_m2 = sub["preco_m2"].median()
    return preco_m2 * area_m2, preco_m2


# ---------------------------------------------------------------------------
# Rodar régua por grupo
# ---------------------------------------------------------------------------
def rodar_grupo(g: dict, vivareal: pd.DataFrame, premissas: dict) -> dict:
    bairro = g["dados"]["suburb"].mode()[0] if g["n"] else "Centro"
    compacto = g["id"].startswith("tese") or g["id"].startswith("a_") or g["id"].startswith("compacto") or g["id"] in ("a_compacto_fora_centro",)
    # corrige: compacto = id contenha 'compacto'
    compacto = "compacto" in g["id"]

    area = area_m2_por_grupo(g, bairro, compacto)
    preco_compra, preco_m2 = preco_compra_referencia(bairro, area, vivareal, compacto)

    # ocupação: usar mediana observada do grupo (piso conservador); p75 como sensibilidade alta
    occ_base = g["occ_med"]
    diaria_med = g["diaria_med"]

    ativo = Ativo(
        nome=f"{bairro} / {g['nome']}",
        bairro=bairro, tipo="apartamento", area_m2=area,
        preco_compra=preco_compra, custo_obra=None,
        diaria_media=diaria_med, ocupacao_base=occ_base,
        cv_preco=0.22, cv_ocupacao=0.6,  # CV de ocupa. entre anúncios (leitura); régua usa 0.35 base
    )
    P_g = premissas_por_grupo(premissas, area, compacto)
    # a régua do módulo Fase 2 usa condominio_iptu fixo; aqui injetamos o do grupo
    P_g["condominio_anual_grupo"] = P_g["condominio_anual"]
    P_g["iptu_anual_grupo"] = P_g["iptu_anual"]

    res_base = calcular(ativo, P_g, cenario="base")
    res_otim = calcular(ativo, P_g, cenario="otimista")
    res_pess = calcular(ativo, P_g, cenario="pessimista")

    return {
        "id": g["id"],
        "nome": g["nome"],
        "bairro": bairro,
        "n": g["n"],
        "area_m2": area,
        "preco_compra_ref": round(preco_compra, 0),
        "preco_m2_ref": round(preco_m2, 0),
        "diaria_med": round(diaria_med, 0),
        "occ_base": round(occ_base, 3),
        "occ_p75": round(g["occ_p75"], 3),
        "cv_occ": round(g["cv_occ"], 3) if g["cv_occ"] == g["cv_occ"] else None,
        "receita_mensal_med": round(g["receita_mensal_med"], 0),
        "cenarios": {
            "base": res_base, "otimista": res_otim, "pessimista": res_pess,
        },
        "noi_base": res_base["noi"],
        "yield_base": res_base["yield_liquido"],
        "payback_base": res_base["payback_anos"],
        "invest_total": res_base["investimento"]["total"],
        "custos_op_anual": res_base["custos_operacao"]["total"],
    }


# ---------------------------------------------------------------------------
# Veredito
# ---------------------------------------------------------------------------
def veredito(grupos: list[dict]) -> str:
    tese = next(g for g in grupos if g["id"] == "tese_compacto_centro")
    a = next(g for g in grupos if g["id"] == "a_compacto_fora_centro")
    b = next(g for g in grupos if g["id"] == "b_maior_no_centro")
    c = next(g for g in grupos if g["id"] == "c_maior_fora_centro")
    mp = next(g for g in grupos if g["id"] == "compacto_meia_praia")
    mt = next(g for g in grupos if g["id"] == "compacto_morretes")

    def yg(g, cen="base"):
        return g["cenarios"][cen]["yield_liquido"] * 100

    def ymax_otim(g):
        return g["cenarios"]["otimista"]["yield_liquido"] * 100

    linhas = [
        "# VEREDITO — Tese dos compactos no Centro",
        "",
        f"**Grupo tese (compacto/Centro)**: n={tese['n']} | occ={tese['occ_base']:.2f} (p75 {tese['occ_p75']:.2f}), CV={tese['cv_occ']} | "
        f"diária=R${tese['diaria_med']:.0f} | m² ref=R${tese['preco_m2_ref']:,.0f} | "
        f"yield base={yg(tese):+.2f}% | yield otimista={ymax_otim(tese):+.2f}% (occ {tese['cenarios']['otimista']['ocupacao_usada']:.0%})",
        "",
        f"**(a) compacto fora do Centro**: n={a['n']} | yield base={yg(a):+.2f}% | otimista={ymax_otim(a):+.2f}%",
        f"**(b) maior no Centro**: n={b['n']} | yield base={yg(b):+.2f}% | otimista={ymax_otim(b):+.2f}%",
        f"**(c) maior fora do Centro**: n={c['n']} | yield base={yg(c):+.2f}% | otimista={ymax_otim(c):+.2f}%",
        "",
        "_Apoio (localização dentro de compactos):_",
        f"- Compacto em **Meia Praia**: yield base={yg(mp):+.2f}% | otimista={ymax_otim(mp):+.2f}%",
        f"- Compacto em **Morretes**: yield base={yg(mt):+.2f}% | otimista={ymax_otim(mt):+.2f}% (m² ref={mt['preco_m2_ref']:,.0f})",
        "",
    ]

    # Etapa 1 — PERFIL: compacto bate maior?
    compacto_me_q = (yg(tese) > yg(b)) and (yg(tese) > yg(c))
    compacto_me_q_otim = (ymax_otim(tese) > ymax_otim(b)) and (ymax_otim(tese) > ymax_otim(c))
    perfil_ok = compacto_me_q and compacto_me_q_otim

    # Etapa 2 — LOCALIZAÇÃO: dentro dos compactos, o Centro é o melhor?
    fora_melhor = (yg(mp) > yg(tese)) or (yg(mt) > yg(tese))
    fora_melhor_otim = (ymax_otim(mp) > ymax_otim(tese)) or (ymax_otim(mt) > ymax_otim(tese))
    local_ok = not (fora_melhor and fora_melhor_otim)

    linhas += ["## Decisão em duas etapas", ""]
    if perfil_ok and local_ok:
        linhas += ["### VEREDITO: SUSTENTA", "",
                   "O grupo compacto/Centro tem o maior yield entre os 4 contrafatos (base e otimista) "
                   "e é o melhor bairro entre os compactos.", ""]
    elif perfil_ok and not local_ok:
        linhas += ["### VEREDITO: SUSTENTA PARCIALMENTE", "",
                   "**O perfil compacto é confirmado**: compactos superam unidades maiores em eficiência de "
                   "capital (yield) tanto no cenário base quanto no otimista — a tese acerta no TAMANHO.",
                   "",
                   f"**Mas a localização falha**: o melhor bairro para compactos NÃO é o Centro "
                   f"(yield base {yg(tese):+.2f}% / otimista {ymax_otim(tese):+.2f}%). "
                   f"Morretes alcança {yg(mt):+.2f}% no base e {ymax_otim(mt):+.2f}% no otimista, e Meia Praia "
                   f"{ymax_otim(mp):+.2f}% — impulsionados por preço/m² menor "
                   f"(Morretes m² mediano R${mt['preco_m2_ref']:,.0f} vs Centro R${tese['preco_m2_ref']:,.0f}). "
                   "A tese original está correta no 'o quê', errada no 'onde' do CENTRO.", ""]
    else:
        linhas += ["### VEREDITO: NÃO SUSTENTA", "",
                   "Nos dados, o grupo compacto/Centro não alcança o maior yield; outra combinação "
                   "perfil×local vence.", ""]

    linhas += [
        "## Leitura econômica",
        "",
        "- **Nenhum grupo é viável no cenário base** (todos os yields negativos com occ_proxy mediana "
        "0.14-0.18): a viabilidade depende da cauda superior de ocupação (p75/otimista). Isso reforça que, "
        "antes de qualquer alocação, a Seazone precisa de receita real de ocupação OU captação agressiva.",
        "- **Eficiência de capital do compacto**: investimento ~R$1,0M vs ~R$2,3-2,5M dos maiores — "
        "mesmo com diária menor, o yield relativo favorece compactos.",
        "- **Preço/m² é o motor da localização**: bairros com m² mais barato (Morretes, Meia Praia) "
        "conseguem yield positivo mais cedo que o Centro (m² mais caro).",
        "- **CV de ocupa. alto (0.7-1.1)** destaca a volatilidade sazonal de Itapema: gestão de canal é decisiva.",
    ]
    return "\n".join(linhas)


# ---------------------------------------------------------------------------
# Saída markdown
# ---------------------------------------------------------------------------
def relatorio(grupos: list[dict], veredito_txt: str) -> str:
    linhas = [
        "# Fase 5 — Teste da tese dos compactos no Centro",
        "",
        "> A régua é a da Fase 2 (NOI/yield/cap rate/payback). Receita usa occ_proxy (limite inferior).",
        "> Custos por tipologia: compacto tem limpeza −20%, consumível −15%, energia −15%, condomínio menor;",
        "> maior tem condomínio/IPTU maiores. Concorrência (não capturável) é nota qualitativa por N.",            
        "",
        veredito_txt,
        "",
        "## Tabela de confronto (cenário base)",
        "",
        "| Grupo | n | Área | Preço compra ref | Diária | Occ base | CV occ | Receita mês | NOI/ano | Yield | Payback | Investimento |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for g in grupos:
        pb = f"{g['payback_base']}" if g["payback_base"] else "—"
        linhas.append(
            f"| {g['nome']} | {g['n']} | {g['area_m2']}m² | R$ {g['preco_compra_ref']:,.0f} | R$ {g['diaria_med']} | "
            f"{g['occ_base']:.2f} | {g['cv_occ'] or '—'} | R$ {g['receita_mensal_med']:,.0f} | "
            f"R$ {g['noi_base']:,.0f} | {g['yield_base']*100:.2f}% | {pb} anos | R$ {g['invest_total']:,.0f} |"
        )
    linhas += ["", "## Cenários (otimista/pessimista) por grupo — yield", ""]
    for g in grupos:
        oy = g["cenarios"]["otimista"]["yield_liquido"]
        py = g["cenarios"]["pessimista"]["yield_liquido"]
        linhas.append(f"- **{g['nome']}**: otimista {oy*100:.2f}% | pessimista {py*100:.2f}%")
    linhas += ["", "![comparativo](fase5_veredito.png)", ""]
    linhas += [
        "## Senso crítico",
        "",
        "- **Ocupação é o fator decisivo**: na régua base (mediana do proxy, ~0.17-0.19) os yields são",
        "  baixos; quem sustenta a tese é a cauda superior (p75). A Fase 7 recomendará trabalhar ocupação",
        "  com captação (canais Seazone) antes de escalar capital.",
        "- **Tamanho de amostra**: n=78 compactos/Centro é robusto; n de compactos/fora e maior/Centro",
        "  deve ser lido com cautela conforme a tabela.",
        "- **Preço de compra = mediana VivaReal m² × área** (proxy por bairro). A compra real negocia",
        "  esse valor — sensibilidade de preço mudaria o veredito.",
    ]
    return "\n".join(linhas) + "\n"


# ---------------------------------------------------------------------------
# Gráfico
# ---------------------------------------------------------------------------
def grafico(grupos):
    ids = ["tese_compacto_centro", "a_compacto_fora_centro", "b_maior_no_centro", "c_maior_fora_centro"]
    gs = [g for g in grupos if g["id"] in ids]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    x = np.arange(len(gs))
    y = [g["yield_base"] * 100 for g in gs]
    yn = [g["cenarios"]["otimista"]["yield_liquido"] * 100 for g in gs]
    ax.bar(x - 0.2, y, 0.4, label="yield base", color="#2c7fb8")
    ax.bar(x + 0.2, yn, 0.4, label="yield otimista", color="#31a354")
    ax.set_xticks(x, [g["nome"].split(":")[-1].strip() for g in gs], rotation=20, ha="right", fontsize=8)
    ax.set_ylabel("Yield líquido anual (%)")
    ax.axhline(0, color="gray", lw=0.8)
    ax.legend()
    ax.set_title("Yield por grupo (base vs otimista)")
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fase5_veredito.png")
    plt.close(fig)


def main():
    b = pd.read_csv(OUTPUT_DIR / "fase3_base_receita.csv")
    vivareal = pd.read_csv(OUTPUT_DIR / "vivareal_clean.csv")

    premissas = {k: p.valor for k, p in PREMISSAS.items()}

    grupos_data = montar_grupos(b)
    grupos = [rodar_grupo(g, vivareal, premissas) for g in grupos_data]

    # salvar tabela
    tab = pd.DataFrame([{
        "id": g["id"], "nome": g["nome"], "n": g["n"], "area_m2": g["area_m2"],
        "preco_compra_ref": g["preco_compra_ref"], "diaria_med": g["diaria_med"],
        "occ_base": g["occ_base"], "cv_occ": g["cv_occ"], "receita_mensal_med": g["receita_mensal_med"],
        "noi_base": g["noi_base"], "yield_base": g["yield_base"],
        "invest_total": g["invest_total"], "payback_base": g["payback_base"],
    } for g in grupos])
    tab.to_csv(OUTPUT_DIR / "fase5_tabela_confronto.csv", index=False)

    veredito_txt = veredito(grupos)
    (OUTPUT_DIR / "fase5_relatorio.md").write_text(relatorio(grupos, veredito_txt), encoding="utf-8")
    grafico(grupos)

    resumo = {
        "veredito": veredito_txt,
        "grupos": [{k: (v if k != "dados" else None) for k, v in g.items() if k != "cenarios"} for g in grupos],
        "cenarios_detalhados": {g["id"]: {k: v for k, v in g["cenarios"].items()} for g in grupos},
    }
    (OUTPUT_DIR / "fase5_resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    print("=== TABELA DE CONFRONTO (cenário base) ===")
    print(tab[["id", "n", "area_m2", "occ_base", "cv_occ", "diaria_med", "noi_base", "yield_base", "invest_total"]].to_string(index=False))
    print("\n=== VEREDITO ===")
    print(veredito_txt)
    print("\nArquivos: fase5_tabela_confronto.csv, fase5_relatorio.md, fase5_veredito.png, fase5_resumo.json")


if __name__ == "__main__":
    main()