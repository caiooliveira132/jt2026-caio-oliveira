from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

import json
from .config import OUTPUT_DIR


class CriterioMestre(Enum):
    YIELD_LIQUIDO_ANUAL = "yield_liquido_anual"
    PAYBACK_SIMPLES = "payback_simples"
    CONSISTENCIA_OCUPACAO = "consistencia_ocupacao"


class EixoDeNegocio(Enum):
    PRECO_AQUISICAO = "preco_aquisicao"
    PRECO_ALUGUEL = "preco_aluguel"
    VOLATILIDADE = "volatilidade"
    CUSTO_OPERACAO = "custo_operacao"


class CenarioExecucao(Enum):
    COMPRA_PRONTO = "A"
    LANCAMENTO_CONSTRUCAO = "B"


class TipoAnuncio(Enum):
    INTEGRAL = "inteiro"
    QUARTO_PRIVADO = "quarto_privado"
    QUARTO_COMPARTILHADO = "quarto_compartilhado"


# ---------------------------------------------------------------------------
# Definições formais (herdadas por todas as fases seguintes)
# ---------------------------------------------------------------------------
DEFINICAO_MELHOR = (
    "Maximizar o Yield Líquido Anual (NOI / Investimento Total), com consistência "
    "temporal de ocupação e atratividade de clientes como filtros obrigatórios. "
    "'Melhor' NÃO é maior receita absoluta: é lucratividade sistemática e racional "
    "no longo prazo, avaliada nos eixos preço de aquisição, preço de aluguel, "
    "volatilidade e custo de operação."
)

DEFINICAO_PERFIL = (
    "Configuração descritiva do ativo: tipologia (apartamento/casa/studio), número de "
    "quartos, tipo de anúncio (inteiro vs. privado/compartilhado) e comodidades "
    "ameinities. O melhor perfil é a combinação que maximiza o critério-mestre no "
    "melhor local, com foco em lucro de longo prazo, retenção e volume de clientes."
)

DEFINICAO_LOCALIZACAO = (
    "Nível de bairro (e grade/mesh quando os dados permitirem), medido pela receita média "
    "por noite x ocupação, ponderada por consistência (baixo desvio-padrão) e pelo preço "
    "de aquisição da região (VivaReal). Melhor localização = maior yield líquido, "
    "não maior receita bruta."
)

ESCOPO_EXECUCAO = (
    "A recomendação cobre dois cenários de execução: (A) compra de imóvel pronto e "
    "(B) lançamento/construção de novo prédio (captação de proprietários + custos de "
    "obra), ambos com custo de operação estimado — pois a Seazone origina prédios e "
    "capta proprietários, e a decisão de investimento inclui COMO executar."
)


@dataclass(frozen=True)
class ConceitosFase0:
    melhor: str = DEFINICAO_MELHOR
    perfil: str = DEFINICAO_PERFIL
    localizacao: str = DEFINICAO_LOCALIZACAO
    escopo_execucao: str = ESCOPO_EXECUCAO
    criterio_mestre: str = CriterioMestre.YIELD_LIQUIDO_ANUAL.value
    metricas_suporte: tuple = (
        CriterioMestre.PAYBACK_SIMPLES.value,
        CriterioMestre.CONSISTENCIA_OCUPACAO.value,
    )
    eixos: tuple = tuple(e.value for e in EixoDeNegocio)
    cenarios: tuple = tuple(f"{c.value}:{c.name}" for c in CenarioExecucao)


# ---------------------------------------------------------------------------
# Régua de retorno (skeleton parametrizável; números reais entram na Fase 2)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PremissasFinanceiras:
    taxas_imobiliarias: float = 0.04
    taxa_gestao_seazone: float = 0.20
    taxa_distribuicao_canais: float = 0.15
    custo_limpeza_por_diaria: float = 80.0
    custo_fixo_mensal: float = 1000.0
    manutencao_anual_pct_invest: float = 0.01
    custo_obra_por_m2: float = 3500.0
    custo_captacao_por_unidade: float = 35000.0
    capital_giro_mensal: float = 0.0
    margem_key_metrics: str = (
        "Premissas a VALIDAR com mercado de Itapema na Fase 2; aqui definem a forma da régua."
    )


def receita_bruta_anual(preco_medio_noite: float, ocupacao_media: float) -> float:
    return preco_medio_noite * ocupacao_media * 365


def noi(
    receita_bruta_anual: float,
    custo_operacao_anual: float,
    taxa_gestao: float,
    taxa_canais: float,
    custo_limpeza_por_diaria: float,
    dias_ocupados: float,
) -> float:
    despesas_fixas = custo_operacao_anual
    despesas_variaveis = receita_bruta_anual * (taxa_gestao + taxa_canais)
    limpeza = custo_limpeza_por_diaria * dias_ocupados
    return receita_bruta_anual - despesas_fixas - despesas_variaveis - limpeza


def yield_liquido_anual(noi_: float, investimento_total: float) -> float:
    return noi_ / investimento_total


def payback_simples(investimento_total: float, noi_anual: float) -> float:
    if noi_anual <= 0:
        return float("inf")
    return investimento_total / noi_anual


def cv(serie: list[float]) -> float:
    import statistics

    if len(serie) < 2:
        return float("nan")
    media = statistics.fmean(serie)
    if media == 0:
        return float("inf")
    return statistics.pstdev(serie) / media


def custo_operacao_anual(
    premissas: PremissasFinanceiras, investimento_total: float, dias_ocupados: float
) -> float:
    return (
        premissas.custo_fixo_mensal * 12
        + premissas.manutencao_anual_pct_invest * investimento_total
        + premissas.custo_limpeza_por_diaria * dias_ocupados
    )


# ---------------------------------------------------------------------------
# As 5 perguntas fechadas da Fase 0
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PerguntaDePesquisa:
    id: str
    pergunta: str
    fontes: list[str]
    formato_resposta: str
    hipotese_preliminar: str
    metodo_validacao: str


AS_5_PERGUNTAS: list[PerguntaDePesquisa] = [
    PerguntaDePesquisa(
        id="RQ1",
        pergunta=(
            "Qual perfil de imovel maximiza o criterio-mestre em Itapema "
            "(tipologia x quartos x tipo de anuncio x comodidades)?"
        ),
        fontes=["details", "price", "vivareal"],
        formato_resposta="1 perfil vencedor + 2 alternativos, com yield/payback/CV",
        hipotese_preliminar=(
            "Grupos compactos (studio/1-2 quartos), anuncio inteiro; vista/cenario como "
            "diferenciais de preco. NAO assumir: medir."
        ),
        metodo_validacao="Matriz perfil x yield; controlar por host profissional",
    ),
    PerguntaDePesquisa(
        id="RQ2",
        pergunta=(
            "Qual localizacao (bairro) maximiza o criterio-mestre - e nao apenas a receita?"
        ),
        fontes=["mesh", "price", "vivareal"],
        formato_resposta="Ranking de bairros por yield liquido ajustado por volatilidade + N por bairro",
        hipotese_preliminar=(
            "Bairros de frente-mar com bom preco/m2 no VivaReal; suspeita de receita alta "
            "diferente de retorno alto - abrir a caixa-preta."
        ),
        metodo_validacao="Boxplot receita x CV por bairro; yield = NOI/preco de compra por bairro",
    ),
    PerguntaDePesquisa(
        id="RQ3",
        pergunta="Quais caracteristicas mais explicam a variacao das receitas (host, amenities, quartos, avaliacoes)?",
        fontes=["details", "hosts"],
        formato_resposta="Ranking de coeficientes (contribuicao % na receita)",
        hipotese_preliminar=(
            "Superhost, n de reviews e presenca de vista/amenidades movem receita mais que "
            "quartos; controlar confusao com host profissional."
        ),
        metodo_validacao="Regressao simples + interpretacao em termos de negocio",
    ),
    PerguntaDePesquisa(
        id="RQ4",
        pergunta=(
            "O que comprar hoje, quanto custa e qual o retorno estimado "
            "(cenario A pronto x cenario B lancamento)?"
        ),
        fontes=["vivareal", "price", "realistic_assumptions"],
        formato_resposta="Especificacao do ativo + tabela NOI/yield/payback em 3 cenarios",
        hipotese_preliminar=(
            "1 ativo concreto no melhor bairro (ex.: apto 1 quarto com vista); comparar "
            "A vs B em horizonte de 5 anos."
        ),
        metodo_validacao="Toda linha da tabela com premissa justificada em mercado",
    ),
    PerguntaDePesquisa(
        id="RQ5",
        pergunta="A tese dos compactos no Centro se sustenta nos dados?",
        fontes=["details", "mesh", "price", "vivareal"],
        formato_resposta="Veredito: sustenta / nao sustenta / sustenta parcialmente + numeros",
        hipotese_preliminar=(
            "Suspeita de 'sustenta parcialmente': Centro pode ganhar em preco/ocupacao, "
            "mas perder em retorno comparado a um bairro alternativo de maior yield."
        ),
        metodo_validacao="Grupo compacto-Centro vs. 3 contrafactuals da Fase 5",
    ),
]


# ---------------------------------------------------------------------------
# Saídas acessíveis para as próximas fases
# ---------------------------------------------------------------------------
def gerar_definicoes_json() -> Path:
    payload = {
        "fase": "fase0",
        "conceitos": {
            "melhor": DEFINICAO_MELHOR,
            "perfil": DEFINICAO_PERFIL,
            "localizacao": DEFINICAO_LOCALIZACAO,
            "escopo_execucao": ESCOPO_EXECUCAO,
        },
        "criterio_mestre": CriterioMestre.YIELD_LIQUIDO_ANUAL.value,
        "metricas_suporte": [CriterioMestre.PAYBACK_SIMPLES.value, CriterioMestre.CONSISTENCIA_OCUPACAO.value],
        "eixos_de_negocio": [e.value for e in EixoDeNegocio],
        "cenarios_execucao": [{"id": c.value, "nome": c.name} for c in CenarioExecucao],
        "perguntas": [asdict(p) for p in AS_5_PERGUNTAS],
        "formula_régua": {
            "receita_bruta_anual": "preco_medio_noite * ocupacao_media * 365",
            "noi": "receita_bruta - custo_fixo_anual - %gestao - %canais - limpeza",
            "yield_liquido_anual": "noi / investimento_total",
            "payback_simples": "investimento_total / noi_anual",
            "consistencia": "cv(ocupacao) = pstdev/mean({diarias_ocupadas})",
        },
    }
    destino = OUTPUT_DIR / "definicoes_fase0.json"
    destino.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return destino


def gerar_relatorio_md() -> Path:
    linhas = [
        "# Fase 0 - Definicoes e criterio-mestre",
        "",
        "## Paragrafo formal (critério-mestre)",
        "",
        DEFINICAO_MELHOR,
        "",
        "**Perfil:** " + DEFINICAO_PERFIL,
        "",
        "**Localizacao:** " + DEFINICAO_LOCALIZACAO,
        "",
        "**Escopo de execucao:** " + ESCOPO_EXECUCAO,
        "",
        "## Validação em 2 frases",
        "",
        "> 'Melhor' e o que produz o maior yield líquido anual persistente (NOI/Investimento total)",
        "> com baixa volatilidade de ocupacao e aluguel; NAO e a maior receita bruta.",
        "",
        "## 5 perguntas fechadas x resposta preliminar",
        "",
        "| ID | Pergunta | Fontes | Hipotese preliminar | Como valido |",
        "|---|---|---|---|---|",
    ]
    for p in AS_5_PERGUNTAS:
        linhas.append(
            f"| {p.id} | {p.pergunta} | {', '.join(p.fontes)} | {p.hipotese_preliminar} | {p.metodo_validacao} |"
        )
    destino = OUTPUT_DIR / "relatorio_fase0.md"
    destino.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return destino


if __name__ == "__main__":
    j = gerar_definicoes_json()
    m = gerar_relatorio_md()
    print(f"[Fase 0] Definições salvas em: {j}")
    print(f"[Fase 0] Relatório salvo em:    {m}")
    print("\nValidação em 2 frases:")
    print("  'Melhor' é o que produz o MAIOR YIELD LÍQUIDO ANUAL PERSISTENTE (NOI/Investimento),")
    print("  com baixa volatilidade de ocupação e aluguel. NÃO é a maior receita bruta.")