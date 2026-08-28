from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Optional

from .config import OUTPUT_DIR


# ---------------------------------------------------------------------------
# Premissas justificadas
# Cada premissa tem: valor + fonte (mercado Itapema / taxa padrão mercado / suposição)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Premissa:
    valor: float
    fonte: str
    unidade: str


PREMISSAS: dict[str, Premissa] = {
    # --- Investimento, Cenário A (compra de pronto) ---
    "itbi_registro_pct": Premissa(0.035, "Mercado SC: ITBI ~3% + registro ~0,5% (fonte: tabela municipal Itapema / prática notarial)", "% do preço de compra"),
    "reforma_mobilia_pct": Premissa(0.08, "Suposição: mobiliar/equipar apto para short stay (mercado Itapema; validar com orçamento)", "% do preço de compra"),
    "capital_giro_meses_A": Premissa(3.0, "Suposição de prudência: 3 meses de custo operacional até estabilização", "meses"),

    # --- Investimento, Cenário B (lançamento/construção) ---
    "captacao_por_unidade": Premissa(40000.0, "Suposição de originação: prospecção, contrato e comissão de captação de proprietário (calibrar com comercial Seazone)", "R$/unidade"),
    "mkt_to_producao_ratio": Premissa(0.75, "Custo de PRODUÇÃO all-in (terreno + obra + projeto + incorporação) ≈ 75% do preço de revenda observado por m² no bairro. Captura a margem/dev markup que se paga ao comprar pronto; construir = capturar esse delta. Validar com VGV/planilha de incorporação na Fase 6.", "taxa sobre revenda m²"),
    "projeto_permutas_pct_obra": Premissa(0.10, "Suposição: projeto arquitetônico/estrutural, licenciamento e permutas = 10% do custo de obra", "% da obra"),
    "marketing_pre_venda_pct_obra": Premissa(0.04, "Suposição: marketing/incorporação de pré-venda = 4% da obra", "% da obra"),
    "contingencia_pct_obra": Premissa(0.08, "Suposição: contingência de obra/repasses = 8% da obra", "% da obra"),
    "capital_giro_meses_B": Premissa(6.0, "Suposição de prudência: 6 meses de custo operacional até estabilização (prazo de obra maior)", "meses"),

    # --- Operação (compartilhados A e B) ---
    "taxa_gestao_seazone": Premissa(0.20, "Padrão de mercado gerenciadora short stay (20-30%); a confirmar com comercial Seazone", "% da receita bruta"),
    "taxa_canais": Premissa(0.10, "Suposição: comissões de distribuição em múltiplos canais (Airbnb/Vrbo/OTA) diluídas", "% da receita bruta"),
    "custo_limpeza_por_virada": Premissa(130.0, "Mercado Itapema: diária de profissional de limpeza + insumos base (cleaning_fee mediano anunciado R$250 cobre mais que o custo real)", "R$/virada"),
    "consumiveis_por_diaria": Premissa(18.0, "Suposição: consumíveis/amenities por diária ocupada (amaciante, papel, café, reposição)", "R$/diária ocupada"),
    "estada_media_noites": Premissa(4.0, "Suposição de estada média curta temporada litoral catarinense (3-5 noites)", "noites/turnover"),
    "manutencao_pct_ano_pronto": Premissa(0.015, "Suposição conservadora: manutenção anual imóvel usado = 1,5% do preço de compra", "% do preço/ano"),
    "manutencao_pct_ano_novo": Premissa(0.007, "Suposição: imóvel novo tem manutenção menor = 0,7% do custo de obra (vantagem do cenário B)", "% do custo obra/ano"),
    "energia_internet_mensal": Premissa(380.0, "Suposição: energia (clima praia) + internet em curta temporada, média anual", "R$/mês"),
    "seguros_pct_ano": Premissa(0.003, "Mercado seguradoras: seguro residencial locação temporária ≈ 0,3% do valor por ano", "% do valor/ano"),
    # condomínio e IPTU vêm de dados por bairro na execução (vivareal_clean), não como premissa fixa.

    # --- Calibração de cenários (volatilidade) ---
    "cv_preco_diaria": Premissa(0.25, "Placeholder: volatilidade da diária; será calibrada por bairro/perfil na Fase 3 com Price_AV", "desvio/média"),
    "cv_ocupacao": Premissa(0.35, "Placeholder: sazonalidade da ocupação; será calibrada na Fase 3", "desvio/média"),

    # --- Exemplos de execução (calibração na Fase 3+) ---
    "occ_base_exemplo": Premissa(0.30, "Cenário base para exemplo da máquina; ocupação real por bairro/perfil virá da Fase 3 (proxy observado 0.17 = piso pessimista)", "taxa anual"),
}


# ---------------------------------------------------------------------------
# Estruturas de execução
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Ativo:
    """Descrição do ativo e parâmetros de receita (calibrados na Fase 3)."""
    nome: str
    bairro: str
    tipo: str
    area_m2: float
    preco_compra: Optional[float]   # Cenário A (None se não aplicável)
    custo_obra: Optional[float]     # Cenário B (None se não aplicável)
    diaria_media: float
    ocupacao_base: float
    cv_preco: float = 0.25
    cv_ocupacao: float = 0.35
    n_unidades: int = 1


def _multiplicador_cenario(cenario: str, cv: float) -> float:
    if cenario == "otimista":
        return 1.0 + cv
    if cenario == "pessimista":
        return max(1.0 - cv, 0.0)
    return 1.0


def preco_producao_por_m2(preco_m2_mercado: float, P: dict[str, float]) -> float:
    """Custo all-in de desenvolvimento por m² a partir do preço de revenda observado do bairro."""
    return preco_m2_mercado * P["mkt_to_producao_ratio"]


def custo_operacao_anual(
    ativo: Ativo,
    P: dict[str, float],
    diaria_media: float,
    ocupacao_media: float,
) -> dict[str, float]:
    """Custos de operação anuais (fixos + variáveis). Condomínio/IPTU das medianas da base."""
    dias_ocupados = 365 * ocupacao_media
    receita_bruta = dias_ocupados * diaria_media

    n_viradas = dias_ocupados / P["estada_media_noites"]
    limpeza = n_viradas * P["custo_limpeza_por_virada"]
    consumiveis = dias_ocupados * P["consumiveis_por_diaria"]
    energia = P["energia_internet_mensal"] * 12

    if ativo.custo_obra is not None:
        base_manut = ativo.custo_obra * ativo.n_unidades
        manut = base_manut * P["manutencao_pct_ano_novo"]
    else:
        base_manut = ativo.preco_compra * ativo.n_unidades
        manut = base_manut * P["manutencao_pct_ano_pronto"]
    seguros = base_manut * P["seguros_pct_ano"]

    cond_iptu = {"condominio_anual": 550.0 * 12, "iptu_anual": 1150.0}  # medianas da base (vivareal_clean)

    gestao = receita_bruta * P["taxa_gestao_seazone"]
    canais = receita_bruta * P["taxa_canais"]

    total = (
        limpeza + consumiveis + energia + manut + seguros
        + cond_iptu["condominio_anual"] + cond_iptu["iptu_anual"]
        + gestao + canais
    )

    return {
        "limpeza": round(limpeza, 0),
        "consumiveis": round(consumiveis, 0),
        "energia_internet": round(energia, 0),
        "manutencao": round(manut, 0),
        "seguros": round(seguros, 0),
        "condominio": round(cond_iptu["condominio_anual"], 0),
        "iptu": round(cond_iptu["iptu_anual"], 0),
        "gestao_seazone": round(gestao, 0),
        "canais_distribuicao": round(canais, 0),
        "total": round(total, 0),
    }


def investimento_cenario_A(ativo: Ativo, P: dict[str, float], capital_giro: float) -> dict[str, float]:
    preco = ativo.preco_compra * ativo.n_unidades
    itbi = preco * P["itbi_registro_pct"]
    reforma = preco * P["reforma_mobilia_pct"]
    total = preco + itbi + reforma + capital_giro
    return {
        "preco_compra": round(preco, 0),
        "itbi_registro": round(itbi, 0),
        "reforma_mobilia": round(reforma, 0),
        "capital_giro": round(capital_giro, 0),
        "total": round(total, 0),
    }


def investimento_cenario_B(ativo: Ativo, P: dict[str, float], capital_giro: float) -> dict[str, float]:
    obra = ativo.custo_obra * ativo.n_unidades
    captacao = P["captacao_por_unidade"] * ativo.n_unidades
    proj = obra * P["projeto_permutas_pct_obra"]
    mkt = obra * P["marketing_pre_venda_pct_obra"]
    conting = obra * P["contingencia_pct_obra"]
    total = obra + captacao + proj + mkt + conting + capital_giro
    return {
        "captacao_proprietarios": round(captacao, 0),
        "custo_obra": round(obra, 0),
        "projeto_permutas": round(proj, 0),
        "marketing_pre_venda": round(mkt, 0),
        "contingencia": round(conting, 0),
        "capital_giro": round(capital_giro, 0),
        "total": round(total, 0),
    }


def calcular(ativo: Ativo, premissas: Optional[dict] = None, cenario: str = "base") -> dict:
    """Função única da régua. `cenario` em {base, otimista, pessimista}."""
    P = premissas or {k: p.valor for k, p in PREMISSAS.items()}

    mult_preco = _multiplicador_cenario(cenario, ativo.cv_preco)
    mult_occ = _multiplicador_cenario(cenario, ativo.cv_ocupacao)

    diaria = ativo.diaria_media * mult_preco
    ocupacao = max(0.05, ativo.ocupacao_base * mult_occ)

    dias_ocupados = 365 * ocupacao
    receita_bruta = dias_ocupados * diaria
    custos = custo_operacao_anual(ativo, P, diaria, ocupacao)
    noi = receita_bruta - custos["total"]

    custo_op_mensal = custos["total"] / 12
    if ativo.custo_obra is not None:
        invest = investimento_cenario_B(ativo, P, capital_giro=custo_op_mensal * P["capital_giro_meses_B"])
        base_apreci = ativo.custo_obra * ativo.n_unidades
    else:
        invest = investimento_cenario_A(ativo, P, capital_giro=custo_op_mensal * P["capital_giro_meses_A"])
        base_apreci = ativo.preco_compra * ativo.n_unidades

    inv_total = invest["total"]
    yield_l = noi / inv_total if inv_total else float("nan")
    cap_rate = noi / base_apreci if base_apreci else float("nan")
    payback = inv_total / noi if noi > 0 else float("inf")
    margem = noi / receita_bruta if receita_bruta else float("nan")

    return {
        "cenario": cenario,
        "ativo": ativo.nome,
        "diaria_usada": round(diaria, 2),
        "ocupacao_usada": round(ocupacao, 4),
        "dias_ocupados": round(dias_ocupados, 0),
        "receita_bruta": round(receita_bruta, 0),
        "custos_operacao": custos,
        "noi": round(noi, 0),
        "investimento": invest,
        "yield_liquido": round(yield_l, 4),
        "cap_rate": round(cap_rate, 4),
        "payback_anos": round(payback, 2) if payback != float("inf") else None,
        "margem_operacional": round(margem, 4),
        "cv_ocupacao_usada": ativo.cv_ocupacao,
    }


def rodar_cenarios(ativo: Ativo) -> dict:
    return {
        "base": calcular(ativo, cenario="base"),
        "otimista": calcular(ativo, cenario="otimista"),
        "pessimista": calcular(ativo, cenario="pessimista"),
    }


# ---------------------------------------------------------------------------
# Saídas
# ---------------------------------------------------------------------------
def tabela_premissas_md() -> str:
    linhas = ["# Tabela de premissas financeiras — Fase 2", "",
              "Fonte de cada valor: (1) mercado Itapema medido na base; (2) padrão de mercado; (3) suposição documentada.",
              "", "| Parâmetro | Valor | Unidade | Fonte |", "|---|---|---|---|"]
    for k, p in PREMISSAS.items():
        linhas.append(f"| {k} | {p.valor:,.4f} | {p.unidade} | {p.fonte} |")
    return "\n".join(linhas) + "\n"


def exemplo_execucao() -> dict:
    """Exemplo da máquina: apto compacto em Meia Praia — valores calibrados na Fase 3."""
    P = {k: p.valor for k, p in PREMISSAS.items()}
    # mercado observado (fase 1): Meia Praia apto R$/m² mediana ≈ 16.053
    preco_m2_mercado = 16053.0
    ativo_a = Ativo(
        nome="Apto 1q Meia Praia (pronto)",
        bairro="Meia Praia", tipo="apartamento", area_m2=55,
        preco_compra=55 * preco_m2_mercado, custo_obra=None,
        diaria_media=460.0, ocupacao_base=0.30,
    )
    ativo_b = Ativo(
        nome="Apto 1q Meia Praia (lançamento)",
        bairro="Meia Praia", tipo="apartamento", area_m2=55,
        preco_compra=None, custo_obra=55 * preco_producao_por_m2(preco_m2_mercado, P),
        diaria_media=460.0, ocupacao_base=0.30,
    )
    return {
        "exemplo": {
            "A_compra_pronto": rodar_cenarios(ativo_a),
            "B_lancamento_obra": rodar_cenarios(ativo_b),
        },
        "premissas_usadas": {k: p.valor for k, p in PREMISSAS.items()},
        "nota_metodologica": (
            "O custo de produção (cenário B) é estimado como 75% do preço de revenda por m² "
            "do bairro (mkt_to_producao_ratio), capturando a margem de desenvolvedor evitada. "
            "A validação com orçamento/planilha de incorporação real é prevista na Fase 6."
        ),
    }


def exemplo_md(ex: dict) -> str:
    linhas = ["# Exemplo de execução da régua financeira — Fase 2", "",
              "Apto compacto em Meia Praia (55m², diária média R$460, ocupação base 30%).",
              "Valores de receita/ocupação serão calibrados por bairro e perfil na Fase 3.",
              "", "## Cenário A — Compra de pronto", "", "| Cenário | Receita | NOI | Investimento | Yield | Payback | Margem | Ocupação |", "|---|---|---|---|---|---|---|---|"]
    for sc, r in ex["exemplo"]["A_compra_pronto"].items():
        pb = f"{r['payback_anos']:.2f}" if r["payback_anos"] is not None else "—"
        linhas.append(
            f"| {sc} | R$ {r['receita_bruta']:,.0f} | R$ {r['noi']:,.0f} | R$ {r['investimento']['total']:,.0f} | "
            f"{r['yield_liquido']*100:.2f}% | {pb} anos | {r['margem_operacional']*100:.2f}% | {r['ocupacao_usada']:.0%} |"
        )
    linhas += ["", "## Cenário B — Lançamento/construção", "", "| Cenário | Receita | NOI | Investimento | Yield | Payback | Margem | Ocupação |", "|---|---|---|---|---|---|---|---|"]
    for sc, r in ex["exemplo"]["B_lancamento_obra"].items():
        pb = f"{r['payback_anos']:.2f}" if r["payback_anos"] is not None else "—"
        linhas.append(
            f"| {sc} | R$ {r['receita_bruta']:,.0f} | R$ {r['noi']:,.0f} | R$ {r['investimento']['total']:,.0f} | "
            f"{r['yield_liquido']*100:.2f}% | {pb} anos | {r['margem_operacional']*100:.2f}% | {r['ocupacao_usada']:.0%} |"
        )
    linhas += ["", "## Leitura", "",
               "Com preços medianos de Itapema e ocupação de 30%, o NOI é ~zero (A) ou mínimo (B) e o "
               "cenário pessimista é negativo. Isso indica que a viabilidade depende de ocupação/diária "
               "maiores do que a mediana — o que direciona a busca de perfil e localização nas Fases 3-5, "
               "e testa diretamente a tese dos compactos do Centro."]
    return "\n".join(linhas) + "\n"


def main():
    md = tabela_premissas_md()
    (OUTPUT_DIR / "premissas_financeiras.md").write_text(md, encoding="utf-8")
    (OUTPUT_DIR / "premissas_financeiras.json").write_text(
        json.dumps({k: asdict(p) for k, p in PREMISSAS.items()}, ensure_ascii=False, indent=2), encoding="utf-8")

    ex = exemplo_execucao()
    (OUTPUT_DIR / "exemplo_calculadora.json").write_text(
        json.dumps(ex, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "exemplo_calculadora.md").write_text(exemplo_md(ex), encoding="utf-8")

    print("=== RÉGUA FINANCEIRA (exemplo: apto 1q Meia Praia, occ base 30%) ===\n")
    for k, cen in ex["exemplo"].items():
        print(f"--- {k} ---")
        for sc, r in cen.items():
            pb = f"{r['payback_anos']:.2f}" if r["payback_anos"] is not None else "inf"
            print(f"  [{sc:>9}] receita={r['receita_bruta']:>10,.0f} | NOI={r['noi']:>9,.0f} | "
                  f"invest={r['investimento']['total']:>11,.0f} | yield={r['yield_liquido']*100:>5.2f}% | "
                  f"payback={pb:>5} | margem={r['margem_operacional']*100:>5.2f}% | occ={r['ocupacao_usada']:.2f}")
    print("\nArquivos: premissas_financeiras.md/json, exemplo_calculadora.json")


if __name__ == "__main__":
    main()