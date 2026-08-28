from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use("Agg")

from .config import OUTPUT_DIR

plt.rcParams["figure.dpi"] = 110
plt.rcParams["axes.titlesize"] = 10
plt.rcParams["axes.labelsize"] = 9
plt.rcParams["xtick.labelsize"] = 8
plt.rcParams["ytick.labelsize"] = 8


def _fmt(v, prec=0):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    return f"{v:,.{prec}f}"


# ---------------------------------------------------------------------------
# 0. Base de receita per-listing (consumida nas Fases 4/5)
# ---------------------------------------------------------------------------
def montar_base_receita() -> pd.DataFrame:
    base = pd.read_csv(OUTPUT_DIR / "base_analise.csv")
    price = pd.read_csv(OUTPUT_DIR / "price_dedup.csv")

    # CV do preço dentro do anúncio (volatilidade sazonal do aluguel)
    cv_preco = (
        price.groupby("airbnb_listing_id")["price"]
        .agg(cv= lambda s: float(np.std(s, ddof=1)) / float(np.mean(s)) if np.mean(s) > 0 else np.nan)
        .reset_index()
    )
    cv_preco.columns = ["airbnb_listing_id", "cv_preco"]

    b = base.copy()
    b = b.merge(cv_preco, on="airbnb_listing_id", how="left")

    # Receita anual/mensal proxy (conservadora, occ=limite inferior)
    b["receita_anual_proxy"] = b["price_median"] * b["occ_proxy_avg"] * 365
    b["receita_mensal_proxy"] = b["receita_anual_proxy"] / 12
    b["diaria_x_occ"] = b["price_median"] * b["occ_proxy_avg"]

    b.to_csv(OUTPUT_DIR / "fase3_base_receita.csv", index=False)
    return b


# ---------------------------------------------------------------------------
# 1. Receita por bairro (ranking + dispersão)
# ---------------------------------------------------------------------------
def tabela_bairro(b: pd.DataFrame):
    tab = (
        b[b["occ_proxy_avg"].notna()]
        .groupby("suburb")["receita_mensal_proxy"]
        .agg(n="count", mediana="median", media="mean", p25=lambda s: s.quantile(0.25), p75=lambda s: s.quantile(0.75), std="std")
        .reset_index()
    )
    tab["cv"] = tab["std"] / tab["media"]
    tab = tab[tab["n"] >= 5].sort_values("mediana", ascending=False)
    return tab.reset_index(drop=True)


TEXTO_BAIRRO = (
    "Leitura: mediana da receita mensal proxy (R$) por bairro, apenas bairros com N>=5 anúncios com preço. "
    "A mediana é a régua de comparação (não a média, puxada por outliers). 'cv' alto = receita instável entre "
    "os anúncios -> mesmo com mediana boa, o retorno é arriscado. Olhar também amplitude p25-p75."
)


# ---------------------------------------------------------------------------
# 2. Perfil (tipologia, quartos, tipo anúncio, comodidades)
# ---------------------------------------------------------------------------
def tabela_quartos(b: pd.DataFrame):
    return (
        b[b["occ_proxy_avg"].notna()]
        .groupby("bedroom_cat")
        .agg(n=("receita_mensal_proxy", "count"),
             receita_med=("receita_mensal_proxy", "median"),
             diaria_med=("price_median", "median"), occ_med=("occ_proxy_avg", "median"),
             estrelas_med=("star_rating", "median"))
        .reindex(["studio", "1q", "2q", "3q", "4q+"])
        .reset_index()
    )


def tabela_tipo_anuncio(b: pd.DataFrame):
    return (
        b[b["occ_proxy_avg"].notna()]
        .groupby("listing_type_std")
        .agg(n=("receita_mensal_proxy", "count"),
             receita_med=("receita_mensal_proxy", "median"),
             diaria_med=("price_median", "median"), occ_med=("occ_proxy_avg", "median"))
        .reset_index()
    )


TEXTO_PERFIL = (
    "Leitura: para cada corte de perfil, comparar receita mensal mediana — mas sempre cruzar com "
    "ocupeção e diária: receita alta pode vir de diária cara (pouca rotação) ou de alta rotação. "
    "O critério-mestre (yield/NOI) será aplicado na Fase 5 sobre estes perfis."
)


# ---------------------------------------------------------------------------
# 3. Cross bairro × quartos (matriz receita + volatilidade)
# ---------------------------------------------------------------------------
def matriz_bairro_quartos(b: pd.DataFrame):
    sub = b[(b["occ_proxy_avg"].notna()) & (b["suburb"].notna()) & (b["n_dates"] >= 30)]
    piv_receita = sub.pivot_table(index="suburb", columns="bedroom_cat", values="receita_mensal_proxy", aggfunc="median")
    piv_n = sub.pivot_table(index="suburb", columns="bedroom_cat", values="receita_mensal_proxy", aggfunc="count")
    return piv_receita, piv_n


TEXTO_CROSS = (
    "Leitura: células coloridas = receita mensal mediana (R$) por bairro × quartos (apenas células com "
    "N>=5 via 'n' na tabela acompanhante — células com N pequeno não são conclusivas). Comparar a coluna "
    "'1q' (compactos) entre bairros: é o teste inicial da tese dos compactos no Centro."
)


# ---------------------------------------------------------------------------
# 3b. Comodidades: presença vs ausência (delta receita/ocupação)
# ---------------------------------------------------------------------------
AMEN_COLS = ["ar_condicionado", "wifi", "piscina", "churrasqueira", "estacionamento",
             "varanda", "vista_mar", "elevador", "academia", "cozinha", "tv"]


def tabela_amenities(b: pd.DataFrame):
    sub = b[b["occ_proxy_avg"].notna()]
    linhas = []
    for col in AMEN_COLS:
        if col not in sub.columns:
            continue
        pres = sub[sub[col] == True]
        aus = sub[sub[col] == False]
        if len(pres) < 5 or len(aus) < 5:
            continue
        linhas.append({
            "amenidade": col,
            "n_pres": len(pres), "n_aus": len(aus),
            "receita_pres": pres.receita_mensal_proxy.median(),
            "receita_aus": aus.receita_mensal_proxy.median(),
            "delta_receita_pct": (pres.receita_mensal_proxy.median() / aus.receita_mensal_proxy.median() - 1) * 100 if aus.receita_mensal_proxy.median() else np.nan,
            "occ_pres": pres.occ_proxy_avg.median(),
            "occ_aus": aus.occ_proxy_avg.median(),
            "diaria_pres": pres.price_median.median(),
            "diaria_aus": aus.price_median.median(),
        })
    return pd.DataFrame(linhas).sort_values("delta_receita_pct", ascending=False)


TEXTO_AMENITIES = (
    "Leitura: delta_receita_pct = quanto a presença da comodidade adiciona à receita mensal mediana "
    "(positivo = amenidade valorizada). Correção importante: amenities correlacionam-se com tamanho "
    "(piscina/varanda aparecem em apartamentos maiores) — o controle por quartos/vista será feito na Fase 4."
)


# ---------------------------------------------------------------------------
# 4. Profissionais/multi-listing (dependência de canal)
# ---------------------------------------------------------------------------
def tabela_hosts(b: pd.DataFrame):
    sub = b[b["occ_proxy_avg"].notna()]
    buckets = pd.cut(
        sub["n_listings_per_host"],
        bins=[0, 1, 2, 5, 10, np.inf],
        labels=["1 (amador)", "2", "3-5", "6-10", "11+"],
    )
    tab = sub.groupby(buckets, observed=False).agg(
        n_listings=("receita_mensal_proxy", "count"), n_hosts=("owner_id", "nunique"),
        receita_med=("receita_mensal_proxy", "median"), occ_med=("occ_proxy_avg", "median"),
        diaria_med=("price_median", "median"))
    return tab.reset_index().rename(columns={"index": "anuncios_por_host"})


def tabela_profissional(b: pd.DataFrame):
    sub = b[b["occ_proxy_avg"].notna()]
    return sub.groupby("is_professional").agg(
        n=("receita_mensal_proxy", "count"), receita_med=("receita_mensal_proxy", "median"),
        occ_med=("occ_proxy_avg", "median"), diaria_med=("price_median", "median"),
        estrelas_med=("star_rating", "median")).reset_index()


TEXTO_HOSTS = (
    "Leitura: se anúncios de hosts com múltiplos anúncios (≥6) concentram receita alta, o mercado é "
    "dominado por operadores profissionais — a Seazone gerenciando o canal consegue replicar isso (distribuição "
    "em canais é a especialidade dela). Separar 'amador' de 'profissional' muda a interpretação da receita por "
    "bairro na Fase 4 (controle de confusão)."
)


# ---------------------------------------------------------------------------
# 4b. Griffins: concentração de município
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Saída markdown com tudo + texto de leitura
# ---------------------------------------------------------------------------
def tabela_md(df: pd.DataFrame, nr: int = 2) -> str:
    return df.round(nr).to_markdown(index=False)


def gerar_relatorio(tab_bairro, tab_quartos, tab_tipo, tab_amen, tab_hosts, tab_prof) -> str:
    linhas = [
        "# Fase 3 — Análise exploratória (receita, localização, perfil)",
        "",
        "> Receita mensal proxy = `preco_mediano (Price_AV) × occ_proxy × 365 / 12`. ",
        "> occ_proxy é limite inferior (snapshot jan/2025) — valores conservadores. ",
        "> Apenas anúncios com preço e bairro; rankings com N>=5.",
        "",
        "## 1. Receita mensal por bairro (ranking) — N e dispersão",
        "",
        tabela_md(tab_bairro),
        "",
        TEXTO_BAIRRO,
        "",
        "![boxplot receita por bairro](fase3_boxplot_bairro.png)",
        "",
        "## 2. Perfil — nº de quartos",
        "",
        tabela_md(tab_quartos),
        "",
        "![barra quartos](fase3_barra_quartos.png)",
        "",
        "## 2b. Perfil — tipo de anúncio",
        "",
        tabela_md(tab_tipo),
        "",
        TEXTO_PERFIL,
        "",
        "## 3. Cruzamento bairro × quartos — matriz de receita mensal mediana (R$)",
        "",
        "![matriz bairro x quartos](fase3_heatmap_bairro_quartos.png)",
        "",
        TEXTO_CROSS,
        "",
        "## 3b. Comodidades — delta de receita (presença vs ausência)",
        "",
        "![delta comodidades](fase3_barra_amenities.png)",
        "",
        tabela_md(tab_amen, 1),
        "",
        TEXTO_AMENITIES,
        "",
        "## Nota sobre amostra e edge-cases",
        "",
        "- Bairros com N pequeno (Várzea n=5, Alto São Bento n=5, Canto da Praia n=9, Sertaozinho n=6) têm p25=0 "
        "e mediana instável — não são conclusivos; destacar apenas Meia Praia, Centro, Morretes, Tabuleiro, casa Branca, Ilhota.",
        "- `occ_proxy=0` ocorre em anúncios cujo snapshot não registrou nenhuma noite bloqueada (captura rara) — "
        "é o piso do proxy, não 'vazio o ano todo'. O corte por `n_dates>=30` usado no heatmap reduz esse efeito.",
        "- Studio tem n=8 apenas (base pequena): a tese dos compactos na prática aqui é sobre **1q**, e não studio.",
        "",
        "## 4. Dependência de canal — profissionais / multi-listing",
        "",
        tabela_md(tab_hosts),
        "",
        tabela_md(tab_prof),
        "",
        TEXTO_HOSTS,
    ]
    return "\n".join(linhas) + "\n"


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------
def graficos(b, tab_bairro, piv_receita):
    # 1. boxplot receita por bairro
    sub = b[b["occ_proxy_avg"].notna()]
    bairros = tab_bairro["suburb"].tolist()
    dados = [sub[sub["suburb"] == bb]["receita_mensal_proxy"].dropna().values for bb in bairros]
    fig, ax = plt.subplots(figsize=(9, 4.2))
    bp = ax.boxplot(dados, tick_labels=bairros, showfliers=False, patch_artist=True)
    for patch in bp["boxes"]:
        patch.set_facecolor("#9ecae1")
    ax.set_ylim(0, None)
    ax.set_title("Receita mensal proxy por bairro (mediana = linha, caixa p25-p75)")
    ax.set_ylabel("R$/mês")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fase3_boxplot_bairro.png")
    plt.close(fig)

    # 2. barra ranking com erro p25-p75
    fig, ax = plt.subplots(figsize=(9, 3.8))
    yerr = np.array([tab_bairro["mediana"] - tab_bairro["p25"], tab_bairro["p75"] - tab_bairro["mediana"]])
    x = np.arange(len(tab_bairro))
    ax.bar(x, tab_bairro["mediana"], yerr=np.abs(yerr), capsize=3, color="#3182bd")
    ax.set_xticks(x, tab_bairro["suburb"], rotation=30, ha="right")
    ax.set_title("Receita mensal mediana por bairro (barras de erro p25–p75)")
    ax.set_ylabel("R$/mês")
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fase3_ranking_bairro.png")
    plt.close(fig)

    # 3. heatmap bairro × quartos
    fig, ax = plt.subplots(figsize=(7, max(3, 0.45 * len(piv_receita))))
    im = ax.imshow(piv_receita.values, cmap="YlGnBu", aspect="auto")
    ax.set_xticks(range(len(piv_receita.columns)), piv_receita.columns)
    ax.set_yticks(range(len(piv_receita.index)), piv_receita.index)
    for i in range(len(piv_receita.index)):
        for j in range(len(piv_receita.columns)):
            v = piv_receita.values[i, j]
            ax.text(j, i, _fmt(v), ha="center", va="center", color="black", fontsize=7)
    fig.colorbar(im, ax=ax, label="R$/mês (mediana)")
    ax.set_title("Receita mensal mediana: bairro × quartos")
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fase3_heatmap_bairro_quartos.png")
    plt.close(fig)

    # 4. barra receita por quartos (perfil)
    q = tabela_quartos(b)
    q = q[q["n"] >= 5]
    fig, ax = plt.subplots(figsize=(7, 3.6))
    x = np.arange(len(q))
    ax.bar(x, q["receita_med"], color="#74c476")
    for xi, v in zip(x, q["receita_med"]):
        ax.text(xi, v, f"R$ {v:,.0f}\nn={int(q.loc[q.index[list(x).index(xi)], 'n'])}",
                ha="center", va="bottom", fontsize=8)
    ax.set_xticks(x, q["bedroom_cat"])
    ax.set_title("Receita mensal mediana por nº de quartos")
    ax.set_ylabel("R$/mês")
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fase3_barra_quartos.png")
    plt.close(fig)

    # 5. barra delta de amenidades
    fig, ax = plt.subplots(figsize=(8, 3.8))
    am = tabela_amenities(b).head(8)
    cores = ["#31a354" if d >= 0 else "#de2d26" for d in am["delta_receita_pct"]]
    ax.barh(am["amenidade"][::-1], am["delta_receita_pct"][::-1], color=cores[::-1])
    ax.set_title("Δ receita mensal mediana por ter a comodidade (%)")
    ax.set_xlabel("Δ % vs anúncios sem a comodidade")
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / "fase3_barra_amenities.png")
    plt.close(fig)


def main():
    b = montar_base_receita()
    tab_bairro = tabela_bairro(b)
    tab_quartos = tabela_quartos(b)
    tab_tipo = tabela_tipo_anuncio(b)
    piv_receita, piv_n = matriz_bairro_quartos(b)
    tab_amen = tabela_amenities(b)
    tab_hosts = tabela_hosts(b)
    tab_prof = tabela_profissional(b)

    graficos(b, tab_bairro, piv_receita)

    relatorio = gerar_relatorio(tab_bairro, tab_quartos, tab_tipo, tab_amen, tab_hosts, tab_prof)
    (OUTPUT_DIR / "fase3_relatorio_exploratorio.md").write_text(relatorio, encoding="utf-8")

    tab_bairro.to_csv(OUTPUT_DIR / "fase3_tab_bairro.csv", index=False)
    tab_amen.to_csv(OUTPUT_DIR / "fase3_tab_amenities.csv", index=False)
    piv_receita.to_csv(OUTPUT_DIR / "fase3_matriz_bairro_quartos.csv")

    resumo_json = {
        "tab_bairro": tab_bairro.to_dict(orient="records"),
        "tab_amenities": tab_amen.to_dict(orient="records"),
        "piv_n": piv_n.to_dict(),
    }
    (OUTPUT_DIR / "fase3_resumo.json").write_text(json.dumps(resumo_json, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    print("== RANKING RECEITA/BARRO (mediana R$/mês, N>=5) ==")
    print(tab_bairro.to_string(index=False))
    print("\n== QUARTOS ==")
    print(tab_quartos.to_string(index=False))
    print("\n== TIPO ==")
    print(tab_tipo.to_string(index=False))
    print("\n== AMENITIES (delta receita %) ==")
    print(tab_amen[["amenidade", "n_pres", "delta_receita_pct", "occ_pres", "occ_aus"]].to_string(index=False))
    print("\n== HOSTS (anúncios por host) ==")
    print(tab_hosts.to_string(index=False))
    print("== PROFISSIONAL ==")
    print(tab_prof.to_string(index=False))
    print("\nArquivos gerados em output/fase3_*")


if __name__ == "__main__":
    main()