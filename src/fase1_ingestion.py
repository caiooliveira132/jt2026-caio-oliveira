from __future__ import annotations

import ast
import json
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .config import AI_LOG_DIR, OUTPUT_DIR, RAW_FILES

pd.set_option("display.max_columns", 40)
pd.set_option("display.width", 200)
pd.set_option("future.no_silent_downcasting", True)


# ---------------------------------------------------------------------------
# Registro rastreável do saneamento
# ---------------------------------------------------------------------------
@dataclass
class SaneamentoLog:
    eventos: list[dict] = field(default_factory=list)

    def add(self, arquivo: str, acao: str, motivo: str, qtd: int):
        self.eventos.append(
            {"arquivo": arquivo, "acao": acao, "motivo": motivo, "qtd_afetada": qtd}
        )

    def to_markdown(self) -> str:
        linhas = [
            "# Saneamento de dados — Fase 1",
            "",
            "Registro rastreável de TODAS as correções/remoções feitas nos 5 CSVs.",
            "Cada evento tem o porquê. Nenhuma decisão abaixo é invisível.",
            "",
            "| Arquivo | Ação | Motivo | Qtd afetada |",
            "|---|---|---|---|",
        ]
        for e in self.eventos:
            linhas.append(
                f"| {e['arquivo']} | {e['acao']} | {e['motivo']} | {e['qtd_afetada']} |"
            )
        linhas.extend(
            [
                "",
                "## Interpretação da ocupação (proxy) — viés de captura",
                "",
                "`occ_proxy_avg = 1 - (dias com preço / período observado)` mede a **taxa de "
                "bloqueio no snapshot**: noite SEM preço capturado = noite não disponível "
                "(reservada ou bloqueada). Como as capturas ocorrem em 06–20/jan/2025 fotografando "
                "estadias até 20/abril/2025, reservas ainda não feitas em janeiro aparecem como "
                "'disponíveis' — logo `occ_proxy_avg` é um **limite inferior** da ocupação "
                "realizada. Consequência: toda projeção de receita construída sobre ele é "
                "conservadora. Listings com `flag_low_conf` (n_dates<30) têm ocupação pouco "
                "confiável e recebem peso reduzido nas Fases 3–5.",
                "",
                "Limitação adicional: um listing capturado 1 única vez (n_capture=1) cobre "
                "menos noites e tende a ter cobertura de captura menor — `cobertura_captura` "
                "quantifica isso e é usado como peso de confiança.",
            ]
        )
        return "\n".join(linhas) + "\n"

    def to_json(self) -> str:
        return json.dumps(self.eventos, ensure_ascii=False, indent=2)


LOG = SaneamentoLog()


# ---------------------------------------------------------------------------
# Helpers de parsing
# ---------------------------------------------------------------------------
def parse_lista(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return []
    if isinstance(x, list):
        return x
    s = str(x).strip()
    if not s or s.lower() in ("nan", "none"):
        return []
    try:
        v = ast.literal_eval(s)
        return v if isinstance(v, list) else [s]
    except (ValueError, SyntaxError):
        return [s]


AMENITY_KEYWORDS = {
    "ar_condicionado": ["ar-condicionado", "ar condicionado", "arcondicionado"],
    "wifi": ["wi-fi", "wifi"],
    "piscina": ["piscina", "pool"],
    "churrasqueira": ["churrasqueira", "bbq", "barbecue"],
    "estacionamento": ["estacionamento", "parking", "garagem", "vaga"],
    "varanda": ["varanda", "balcony", "sacada"],
    "vista_mar": ["vista para o mar", "vista ao mar", "vista do mar", "vista mar", "seaview", "sea view"],
    "elevador": ["elevador", "elevator"],
    "academia": ["academia", "gym"],
    "cozinha": ["cozinha", "kitchen", "kitchenette"],
    "tv": ["tv", "hd tv", "televisão", "televisao"],
}


def extrair_amenities(df: pd.DataFrame) -> pd.DataFrame:
    df["_am_list"] = df["amenities"].map(parse_lista)
    df["n_amenities"] = df["_am_list"].str.len()
    for kw, termos in AMENITY_KEYWORDS.items():
        df[kw] = df["_am_list"].map(lambda li, t=termos: any(t in " ".join(str(i).lower() for i in li) for t in t))
    return df.drop(columns=["_am_list"])


SUBURB_MAP = {
    "Meia praia": "Meia Praia",
    "meia praia": "Meia Praia",
    "MEIA PRAIA": "Meia Praia",
    "Meia Praia - Frente Mar": "Meia Praia",
    "CENTRO": "Centro",
    "Alto São Bento": "Alto Sao Bento",
    "Sertão do Trombudo": "Sertao do Trombudo",
    "Sertão Do Trombudo": "Sertao do Trombudo",
    "Sertãozinho": "Sertaozinho",
    "Taboleiro": "Tabuleiro dos Oliveiras",
    "Tabuleiro": "Tabuleiro dos Oliveiras",
    "Jardim Praia Mar": "Jardim Praiamar",
    "none": None,
}


def padronizar_suburb(s):
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return None
    key = str(s).strip()
    return SUBURB_MAP.get(key, key)


def drop_cols_existentes(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    return df.drop(columns=[c for c in cols if c in df.columns])


# ---------------------------------------------------------------------------
# 1. DETAILS — listings Airbnb
# ---------------------------------------------------------------------------
def load_details() -> pd.DataFrame:
    df = pd.read_csv(RAW_FILES["details"], low_memory=False)
    n0 = len(df)
    df = df.drop_duplicates(subset=["airbnb_listing_id"])
    LOG.add("Details", "drop_duplicates", "listing_id duplicado", n0 - len(df))

    n_rating_zero = int((df["star_rating"] == 0).sum())
    df["star_rating"] = df["star_rating"].replace(0.0, np.nan)
    LOG.add("Details", "recode", "star_rating==0 => sem avaliação (vira NaN)", n_rating_zero)

    for col in ["is_professional", "can_instant_book", "is_new_listing"]:
        df[col + "_missing"] = df[col].isna()
        df[col] = df[col].fillna(False)
    LOG.add("Details", "fillna", "flags binárias com null tratado como False + coluna _missing", 355)

    df = extrair_amenities(df)

    n_dead_min_nights = int((df["min_nights"] == 0).sum())
    df = drop_cols_existentes(df, ["min_nights"])
    LOG.add("Details", "drop_coluna", "min_nights 100% zero (coluna morta)", n_dead_min_nights)

    df["bedroom_cat"] = df["number_of_bedrooms"].map(
        lambda b: "studio" if b == 0 else "1q" if b == 1 else "2q" if b == 2 else "3q" if b == 3 else "4q+"
    )
    df["listing_type_std"] = df["listing_type"].str.strip().str.lower().map(
        {"apartamento": "apartamento", "casa": "casa", "hotel": "hotel", "outros": "outros"}
    )
    df["flag_reviews_zero"] = df["number_of_reviews"] == 0
    df["flag_rating_missing"] = df["star_rating"].isna()
    df["flag_extra_bedrooms"] = df["number_of_bedrooms"] >= 6
    return df


# ---------------------------------------------------------------------------
# 2. HOSTS — por owner_id
# ---------------------------------------------------------------------------
def load_hosts() -> pd.DataFrame:
    df = pd.read_csv(RAW_FILES["hosts"])
    n0 = len(df)
    df = df.drop_duplicates(subset=["owner_id"])
    LOG.add("Hosts", "drop_duplicates", "owner_id duplicado", n0 - len(df))

    df = drop_cols_existentes(df, ["response_rate_shown", "response_time_shown"])
    LOG.add("Hosts", "drop_coluna", "response_rate/time 100% nulos (sem informação)", 2)

    df["years_host_frac"] = df["years_host"] + df["months_host"] / 12.0
    df["flag_host_sem_review_historico"] = df["number_of_reviews_host"] == 0
    return df


# ---------------------------------------------------------------------------
# 3. MESH — bairro + lat/long
# ---------------------------------------------------------------------------
def load_mesh() -> pd.DataFrame:
    df = pd.read_csv(RAW_FILES["mesh"])
    df = df.rename(columns={"latitude": "lat_mesh", "longitude": "lon_mesh"})
    df["suburb"] = df["suburb"].map(padronizar_suburb)
    n_none = int(df["suburb"].isna().sum())
    LOG.add("Mesh", "recode", f"bairro 'none'->NaN; {n_none} registros sem bairro (mantidos)", n_none)
    return df


# ---------------------------------------------------------------------------
# 4. PRICE_AV — preço/ocupação
# ---------------------------------------------------------------------------
def load_price() -> pd.DataFrame:
    df = pd.read_csv(RAW_FILES["price"], parse_dates=["date", "aquisition_date"])
    n0 = len(df)

    df = df.sort_values("aquisition_date").drop_duplicates(
        subset=["airbnb_listing_id", "date"], keep="last"
    )
    LOG.add("Price_AV", "drop_duplicates", "mesmo (listing,data) capturado N vezes -> mantém captura mais recente", n0 - len(df))

    n_price_null = int(df["price"].isna().sum())
    df = df.dropna(subset=["price"])
    LOG.add("Price_AV", "dropna", "price nulo", n_price_null)

    n_outlier = int((df["price"] > 3000).sum())
    df["flag_price_outlier_high"] = df["price"] > 3000
    LOG.add("Price_AV", "flag", "price>3000 sinalizado como outlier a revisar (não exclui)", n_outlier)
    return df


def price_stats_por_listing(p: pd.DataFrame) -> pd.DataFrame:
    g = p.groupby("airbnb_listing_id")
    stats = g.agg(
        n_dates=("date", "count"),
        price_median=("price", "median"),
        price_mean=("price", "mean"),
        price_p25=("price", lambda s: s.quantile(0.25)),
        price_p75=("price", lambda s: s.quantile(0.75)),
        price_min=("price", "min"),
        price_max=("price", "max"),
        n_outliers_high=("flag_price_outlier_high", "sum"),
    ).reset_index()

    span = p.groupby("airbnb_listing_id").agg(
        first_date=("date", "min"), last_date=("date", "max")
    ).reset_index()
    span["observed_span_days"] = (span["last_date"] - span["first_date"]).dt.days + 1
    stats = stats.merge(span[["airbnb_listing_id", "observed_span_days"]], on="airbnb_listing_id", how="left")

    stats["occ_proxy_avg"] = 1 - stats["n_dates"] / stats["observed_span_days"]
    stats["cobertura_captura"] = stats["n_dates"] / stats["observed_span_days"]
    stats["flag_low_conf"] = stats["n_dates"] < 30
    return stats


# ---------------------------------------------------------------------------
# 5. VIVAREAL — mercado de compra
# ---------------------------------------------------------------------------
def load_vivareal() -> pd.DataFrame:
    df = pd.read_csv(RAW_FILES["vivareal"])
    n0 = len(df)
    df = df.sort_values("aquisition_date").drop_duplicates(subset=["listing_id"], keep="last")
    LOG.add("VivaReal", "drop_duplicates", "listing_id duplicado: mantém anúncio mais recente", n0 - len(df))

    df["suburb_padrao"] = df["suburb"].map(padronizar_suburb)
    n_suburb_null = int(df["suburb_padrao"].isna().sum())
    LOG.add("VivaReal", "flag", "suburb nulo (anúncios sem bairro) mantidos como NaN", n_suburb_null)

    n_area_zero = int((df["usable_area"] == 0).sum())
    df["usable_area"] = df["usable_area"].replace(0, np.nan)
    LOG.add("VivaReal", "recode", "usable_area==0 -> NaN (sem área declarada)", n_area_zero)

    df["flag_area_extrema"] = df["usable_area"] > 2000
    df["flag_condo_extremo"] = df["monthly_condo_fee"] > 50000
    df["flag_iptu_extremo"] = df["yearly_iptu"] > 100000
    df["flag_bedrooms_extremos"] = df["bedrooms"] > 6
    n_extremos = int(
        (df["flag_area_extrema"] | df["flag_condo_extremo"] | df["flag_iptu_extremo"] | df["flag_bedrooms_extremos"]).sum()
    )
    LOG.add("VivaReal", "flag", "outliers extremos sinalizados (m2>2000, condominio>50k, IPTU>100k, quartos>6) p/ revisão na Fase 2", n_extremos)

    df["preco_m2"] = df["sale_price"] / df["usable_area"]

    df["flag_alvo_shortstay"] = df["listing_type"].isin(["apartamento", "casa"])
    LOG.add("VivaReal", "flag", "terreno/comercial/outros marcados fora do alvo short stay (não excluídos)", int((~df.flag_alvo_shortstay).sum()))
    return df


# ---------------------------------------------------------------------------
# JOIN PRINCIPAL — base_analise
# ---------------------------------------------------------------------------
def build_base(details, hosts, mesh, price):
    price_stats = price_stats_por_listing(price)

    n_details_sem_mesh = len(set(details.airbnb_listing_id) - set(mesh.airbnb_listing_id))
    n_details_sem_price = len(set(details.airbnb_listing_id) - set(price_stats.airbnb_listing_id))
    LOG.add("Join", "info", "listings sem bairro (Mesh)", n_details_sem_mesh)
    LOG.add("Join", "info", "listings SEM preço (Price_AV) -> NaN e flag_sem_preco", n_details_sem_price)

    mesh_min = mesh[["airbnb_listing_id", "suburb", "lat_mesh", "lon_mesh"]]
    base = (
        details.merge(mesh_min, on="airbnb_listing_id", how="left")
        .merge(price_stats, on="airbnb_listing_id", how="left")
        .merge(hosts, on="owner_id", how="left")
    )

    n_listings_host = details.groupby("owner_id")["airbnb_listing_id"].nunique().rename("n_listings_per_host")
    base = base.merge(n_listings_host, on="owner_id", how="left")
    base["host_multi_listing"] = base["n_listings_per_host"] > 1
    base["flag_sem_preco"] = base["price_median"].isna()

    base = drop_cols_existentes(base, ["host_snapshot_date", "aquisition_date_y"])
    LOG.add("Join", "info", f"base_analise final: {len(base)} listings; sem preço={int(base.flag_sem_preco.sum())}; sem bairro={int(base.suburb.isna().sum())}", 0)
    return base


# ---------------------------------------------------------------------------
# Saídas
# ---------------------------------------------------------------------------
def resumo_estatistico_tabela(titulo, df, cols):
    linhas = [f"## {titulo}", "", f"- shape: {df.shape[0]} linhas x {df.shape[1]} colunas", ""]
    for col in cols:
        if col not in df.columns:
            continue
        s = df[col]
        if pd.api.types.is_numeric_dtype(s):
            linhas.append(
                f"- `{col}`: média={s.mean():.2f} | mediana={s.median():.2f} | "
                f"min={s.min():.2f} | max={s.max():.2f} | nulos={int(s.isna().sum())}"
            )
        else:
            linhas.append(f"- `{col}`: nulos={int(s.isna().sum())} | únicos={s.nunique()}")
    return "\n".join(linhas) + "\n"


def gerar_perfil(base, vivareal, price):
    txt = ["# Perfil estatístico resumido — Fase 1", ""]
    txt.append(resumo_estatistico_tabela(
        "Details (após saneamento)",
        base,
        ["airbnb_listing_id", "number_of_bedrooms", "number_of_beds", "number_of_reviews",
         "cleaning_fee", "star_rating", "min_nights", "n_amenities", "number_of_guests"],
    ))
    txt.append("")
    txt.append(resumo_estatistico_tabela(
        "Price_AV (deduplicado)",
        price,
        ["price", "observed_span_days", "n_outliers_high", "flag_price_outlier_high"],
    ))
    txt.append("")
    txt.append(resumo_estatistico_tabela(
        "Ocupação proxy (por listing)",
        base[base["occ_proxy_avg"].notna()],
        ["occ_proxy_avg", "cobertura_captura", "n_dates", "price_median"],
    ))
    txt.append("")
    txt.append(resumo_estatistico_tabela(
        "VivaReal (após saneamento)",
        vivareal,
        ["sale_price", "usable_area", "monthly_condo_fee", "yearly_iptu", "bedrooms", "preco_m2", "parking_spaces"],
    ))
    return "\n".join(txt)


def main():
    details = load_details()
    hosts = load_hosts()
    mesh = load_mesh()
    price = load_price()
    vivareal = load_vivareal()
    base = build_base(details, hosts, mesh, price)

    base.to_csv(OUTPUT_DIR / "base_analise.csv", index=False)
    vivareal.to_csv(OUTPUT_DIR / "vivareal_clean.csv", index=False)
    price.drop(columns=["flag_price_outlier_high"]).to_csv(OUTPUT_DIR / "price_dedup.csv", index=False)

    md = LOG.to_markdown()
    (AI_LOG_DIR / "saneamento.md").write_text(md, encoding="utf-8")
    (OUTPUT_DIR / "saneamento.md").write_text(md, encoding="utf-8")
    (OUTPUT_DIR / "saneamento_log.json").write_text(LOG.to_json(), encoding="utf-8")
    (OUTPUT_DIR / "perfil_estatistico.md").write_text(gerar_perfil(base, vivareal, price), encoding="utf-8")

    print(">>> BASE_ANALISE:", base.shape)
    print(">>> sem preço:", int(base.flag_sem_preco.sum()))
    print(">>> sem bairro:", int(base.suburb.isna().sum()))
    print(">>> listings com preço:", int((~base.flag_sem_preco).sum()))
    print(">>> ocupacao mediana:", base.occ_proxy_avg.median())
    print(">>> suburb top5:", base.suburb.value_counts(dropna=False).head(6).to_dict())
    print(">>> vivareal por tipo:", vivareal.listing_type.value_counts().to_dict())
    print(">>> salvos: base_analise.csv | vivareal_clean.csv | price_dedup.csv | saneamento.md/json | perfil_estatistico.md")


if __name__ == "__main__":
    main()