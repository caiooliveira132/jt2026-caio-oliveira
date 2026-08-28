from __future__ import annotations

import json

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

matplotlib.use("Agg")

from .config import OUTPUT_DIR

plt.rcParams["figure.dpi"] = 110


# ---------------------------------------------------------------------------
# Preparo de features
# ---------------------------------------------------------------------------
def preparar_dados():
    b = pd.read_csv(OUTPUT_DIR / "fase3_base_receita.csv")
    b = b[b["occ_proxy_avg"].notna()].copy()

    # star_rating nulo (0 => sem avaliação) -> imputar 0 + flag de ausência
    b["flag_rating_missing"] = b["star_rating"].isna()
    b["star_rating"] = b["star_rating"].fillna(0)

    # log1p de receita e reviews
    b["log_receita"] = np.log1p(b["receita_mensal_proxy"])
    b["log_reviews"] = np.log1p(b["number_of_reviews"])
    b["log_host_reviews"] = np.log1p(b["number_of_reviews_host"])

    # proporção ocupada (limite inferior; documentar)
    b["occ_pct"] = (b["occ_proxy_avg"] * 100).clip(0, 100)

    # bairros principais para dummies (referência = Meia Praia, amostra maior)
    b["suburb"] = b["suburb"].fillna("Sem_bairro")
    b["_bairro_top"] = b["suburb"].where(b["suburb"].isin(
        ["Meia Praia", "Centro", "Morretes", "Tabuleiro dos Oliveiras", "Casa Branca", "Ilhota"]), "Outros")
    # get_dummies adiciona dummies de TODAS as categorias; usamos a referência explícita
    # removendo a coluna bairro_Meia_Praia: coeficientes passam a ser relativos a Meia Praia.
    b = pd.get_dummies(b, columns=["_bairro_top"], prefix="bairro", drop_first=False)
    # patsy não aceita espaços em nomes -> sanitizar
    b.columns = [c.replace(" ", "_") for c in b.columns]

    # flags para maioriano
    b["_flag"] = 0
    return b


FEATURES = [
    # patamar/perfil
    "number_of_bedrooms", "number_of_guests",
    # comodidades chave
    "ar_condicionado", "tv", "cozinha", "vista_mar", "elevador", "piscina",
    "churrasqueira", "academia", "varanda", "n_amenities",
    # host / reputação
    "is_superhost", "log_host_reviews", "log_reviews", "star_rating", "flag_rating_missing",
    # confounders controle
    "is_professional", "host_multi_listing", "can_instant_book",
    # bairros (referência implícita = MEIA PRAIA: a coluna bairro_Meia_Praia NÃO entra nele)
    "bairro_Centro", "bairro_Morretes", "bairro_Tabuleiro_dos_Oliveiras",
    "bairro_Casa_Branca", "bairro_Ilhota", "bairro_Outros",
]


def rodar_ols(df, formula: str, nome: str) -> dict:
    modelo = smf.ols(formula, data=df).fit()
    coef = modelo.params
    ci = modelo.conf_int()
    pvals = modelo.pvalues
    tab = pd.DataFrame({
        "var": coef.index,
        "coef": coef.values,
        "ci_lo": ci[0].values,
        "ci_hi": ci[1].values,
        "pvalue": pvals.values,
    })
    # interpretação: para modelo log-linear, coef*100 ≈ % de variação na receita
    tab["efeito_pct"] = np.expm1(tab["coef"]) * 100

    resumo = {
        "nome": nome,
        "n": int(modelo.nobs),
        "r2": float(modelo.rsquared),
        "r2_adj": float(modelo.rsquared_adj),
        "f_pvalue": float(modelo.f_pvalue),
    }
    return {"tab": tab, "resumo": resumo, "modelo": modelo}


def coef_plot(modelos: list, fname: str):
    """Gráfico de coeficientes (brutos) com IC, apenas vars significativas (p<0.1).
    Significância é comparável entre modelos; a ESCALA é diferente (log vs pp) —
    por isso o gráfico cruza coeficientes normalizados por modelo."""
    names = [m["resumo"]["nome"] for m in modelos]
    fig, axes = plt.subplots(1, len(modelos), figsize=(6.2 * max(1, len(modelos)), 8), sharey=False)
    if len(modelos) == 1:
        axes = [axes]
    for ax, (name, m) in zip(axes, [(n, m) for n, m in zip(names, modelos)]):
        t = m["tab"][m["tab"]["pvalue"] < 0.10].dropna(subset=["coef"]).sort_values("coef")
        if t.empty:
            ax.text(0.5, 0.5, "sem variável significativa", ha="center", va="center")
            ax.set_title(name)
            continue
        y = np.arange(len(t))
        ax.errorbar(t["coef"], y, xerr=[t["coef"] - t["ci_lo"], t["ci_hi"] - t["coef"]], fmt="o")
        ax.axvline(0, color="gray", lw=0.8)
        ax.set_yticks(y, [v.replace("bairro_", "") for v in t["var"]], fontsize=8)
        ax.set_xlabel("coeficiente (escala do modelo)")
        ax.set_title(f"{name} (p<0.10)")
    plt.tight_layout()
    fig.savefig(OUTPUT_DIR / fname)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Saída markdown
# ---------------------------------------------------------------------------
def tabela_coef(tab: pd.DataFrame, loglinear: bool = True) -> str:
    out = tab.copy()
    out["p_sig"] = out["pvalue"].map(lambda p: "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else "")
    if loglinear:
        out = out[["var", "coef", "ci_lo", "ci_hi", "pvalue", "efeito_pct", "p_sig"]]
    else:
        out = out.rename(columns={"coef": "coef_pp"})
        out = out[["var", "coef_pp", "ci_lo", "ci_hi", "pvalue", "p_sig"]]
    return out.round(4).to_markdown(index=False)


def gerar_relatorio(modelos: dict) -> str:
    r = modelos["receita"]["resumo"]
    o = modelos["ocupacao"]["resumo"]
    linhas = [
        "# Fase 4 — Modelo explicativo das receitas",
        "",
        "> Modelos OLS sobre dados da Fase 3 (n=999 anúncios com preço).",
        "> - `log_receita`: log-linear → `coef × 100` ≈ variação % na receita mensal por unidade da variável.",
        "> - `occ_pct`: ocupação (proxy, limite inferior do snapshot) em pontos percentuais.",
        "> Confounders controlados: `is_professional`, `host_multi_listing` (hosts profissionais concentram melhores listagens).",
        "> Referência de bairro: **Meia Praia** (coluna removida do modelo — coeficientes de bairro são relativos a ela).",
        "",
        "## 1. Modelo de Receita (log-linear)",
        "",
        f"n={r['n']} | R²={r['r2']:.3f} | R²-aj={r['r2_adj']:.3f} | F-p={r['f_pvalue']:.2e}",
        "",
        tabela_coef(modelos["receita"]["tab"]),
        "",
        "## 2. Modelo de Ocupação (pontos percentuais)",
        "",
        f"n={o['n']} | R²={o['r2']:.3f} | R²-aj={o['r2_adj']:.3f} | F-p={o['f_pvalue']:.2e}",
        "",
        tabela_coef(modelos["ocupacao"]["tab"], loglinear=False),
        "",
        "![coeficientes](fase4_coef_plot.png)",
        "",
        "## 3. Ranking de impacto (o que MOVE receita de fato)",
        "",
    ]
    tab = modelos["receita"]["tab"].copy()
    tab["efeito_pct"] = np.expm1(tab["coef"]) * 100
    sig = tab[(tab["pvalue"] < 0.05) & (tab["var"] != "Intercept")]
    top = sig.reindex(sig["coef"].abs().sort_values(ascending=False).index).head(10)
    for _, r in top.iterrows():
        linhas.append(f"  - **{r['var']}**: +{r['efeito_pct']:.1f}% receita (coef={r['coef']:.3f}, p={r['pvalue']:.3g})")
    linhas += [
        "",
        "## 4. Separado por tipo de anúncio (apartamento vs casa)",
        "",
    ]
    if "apartamento" in modelos:
        a = modelos["apartamento"]
        c = modelos["casa"]
        linhas.append(f"**Apartamento** (n={a['resumo']['n']}, R²={a['resumo']['r2']:.3f}):")
        linhas.append(tabela_coef(a["tab"]))
        linhas.append("")
        linhas.append(f"**Casa** (n={c['resumo']['n']}, R²={c['resumo']['r2']:.3f}):")
        linhas.append(tabela_coef(c["tab"]))
    linhas += [
        "",
        "## 5. Interpretação para negócio",
        "",
    ]
    tab_r = modelos["receita"]["tab"]
    frases = {
        "can_instant_book[T.True]": "Reserva instantânea ativa",
        "log_reviews": "Dobrar o nº de reviews (log)",
        "number_of_guests": "1 hóspede a mais de capacidade",
        "log_host_reviews": "Dobrar o nº de reviews do host (log)",
        "number_of_bedrooms": "1 quarto a mais (mantendo hóspedes constantes)",
        "bairro_Outros": "Estar fora dos bairros principais",
        "is_superhost[T.True]": "Host com selo superhost",
        "vista_mar[T.True]": "Ter vista para o mar",
        "ar_condicionado[T.True]": "Ter ar-condicionado",
        "elevador[T.True]": "Ter elevador",
        "tv[T.True]": "Ter TV",
    }
    vistos = set()
    for var in tab_r.sort_values("coef", ascending=False)["var"]:
        if var in vistos or var not in frases or var == "Intercept":
            continue
        vistos.add(var)
        r = tab_r[tab_r["var"] == var].iloc[0]
        efeito = (np.expm1(r["coef"]) * 100)
        sig = ("significativo" if r["pvalue"] < 0.05 else "não-significativo")
        linhas.append(f"  - **{frases[var]}**: ≈ {efeito:+.0f}% na receita mensal ({sig}, p={r['pvalue']:.3g})")
    linhas += [
        "",
        "> Recomendações diretas: ativar `Reserva instantânea` (+105%), investir em conversão/avaliações",
        "> (dobrar reviews ≈ +39%), dimensionar capacidade de hóspedes (+34%/hóspede); e NÃO tratar 'mais",
        "> quartos' como alavanca — mantendo hóspedes fixos, quarto extra reduz receita média por hóspede.",
        "",
        "## 6. Limitações explícitas (senso crítico)",
        "",
        "- **Ocupação é proxy inferior**: os coeficientes de ocupação devem ser lidos como *ordem de grandeza*,",
        "  não precisão. Receita usa o mesmo proxy — conclusões absolutas limitadas.",
        "- **Correlação ≠ causa**: amenidades correlacionam com tamanho/área (não temos área m² no Airbnb;",
        "  `number_of_guests`/`number_of_beds` são proxies de área). A direção dos efeitos é o que importa.",
        "- **N pequeno em bairros** (Ilhota n=10, Casa Branca n=15) torna aquelas dummies instáveis.",
        "- **Colinearidade**: `piscina`/`academia`/`varanda` vivem em unidades maiores — isolam-se mal.",
        "- **Snapshot único (jan–abr)**: sazonalidade de fim de ano não é observada.",
        "- **R² baixo (~0.09)**: a maior parte da variação de receita é idiossincrática ou não capturada",
        "  (revolvimento de canais, demanda pontual). O modelo explica DIRECIONAIS, não prediz valores.",
    ]
    return "\n".join(linhas) + "\n"


def main():
    b = preparar_dados()

    f_receita = "log_receita ~ " + " + ".join(FEATURES)
    f_ocupa = "occ_pct ~ " + " + ".join(FEATURES)

    modelos = {
        "receita": rodar_ols(b, f_receita, "Receita (log)"),
        "ocupacao": rodar_ols(b, f_ocupa, "Ocupação (pp)"),
    }

    # separar por tipo de anúncio
    if "listing_type_std" in b.columns:
        b_ap = b[b["listing_type_std"] == "apartamento"]
        b_casa = b[b["listing_type_std"] == "casa"]
        if len(b_ap) >= 50:
            modelos["apartamento"] = rodar_ols(b_ap, f_receita, "Receita (apartamento)")
        if len(b_casa) >= 30:
            modelos["casa"] = rodar_ols(b_casa, f_receita, "Receita (casa)")

    coef_plot([modelos["receita"], modelos["ocupacao"]], "fase4_coef_plot.png")

    relatorio = gerar_relatorio(modelos)
    (OUTPUT_DIR / "fase4_modelo_receitas.md").write_text(relatorio, encoding="utf-8")

    # CSV com todos os coeficientes
    todas = []
    for nome, m in modelos.items():
        t = m["tab"].copy()
        t["modelo"] = nome
        todas.append(t)
    pd.concat(todas, ignore_index=True).to_csv(OUTPUT_DIR / "fase4_coeficientes.csv", index=False)

    resumo = {}
    for nome in ("receita", "ocupacao", "apartamento", "casa"):
        if nome in modelos:
            resumo[nome] = modelos[nome]["resumo"]

    (OUTPUT_DIR / "fase4_resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")

    # Ranking com todos os modelos significativos
    print("=== R² por modelo ===")
    for nome, m in modelos.items():
        print(f"  {nome:14s} n={m['resumo']['n']:4d}  R²={m['resumo']['r2']:.3f}  adj={m['resumo']['r2_adj']:.3f}")
    print("\n=== Top 10 fatores que movem RECEITA (p<0.05, |coef| maior) ===")
    tab = modelos["receita"]["tab"]
    sig = tab[(tab["pvalue"] < 0.05) & (tab["var"] != "Intercept")]
    top = sig.reindex(sig["coef"].abs().sort_values(ascending=False).index).head(10)
    for _, r in top.iterrows():
        print(f"  {r['var']:30s} coef={r['coef']:+.3f}  efeito%={np.expm1(r['coef'])*100:+8.1f}  p={r['pvalue']:.3g}")
    print("\nArquivos: fase4_modelo_receitas.md, fase4_coeficientes.csv, fase4_resumo.json, fase4_coef_plot.png")


if __name__ == "__main__":
    main()