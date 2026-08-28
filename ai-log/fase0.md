# AI Log — Fase 0 (Definições e critério-mestre)

Sessão registrada: 2026-08-28 · Ferramenta: opencode (deepseek-v4-flash)

## Prompt solicitado
Executar a Fase 0 nos moldes do plano: transformar o problema em 5 perguntas fechadas e
definir sistematicamente "melhor", "perfil" e "localização", com saída em código Python
organizado em arquivos acessíveis às próximas fases.

## Iterações (o que a IA devolveu e como foi escrutinado)

1. **Primeira versão do módulo** — a IA escreveu `fase0_definitions.py` com enums
   (`CriterioMestre`, `EixoDeNegocio`, `CenarioExecucao`), funções de régua de retorno
   (`noi`, `yield_liquido_anual`, `payback_simples`, `cv`, `custo_operacao_anual`),
   as 5 perguntas como dataclass e exportação para JSON/`.md`.

2. **Problema detectado (senso crítico sobre a saída da IA)** — três constantes de
   texto (`DEFINICAO_PERFIL`, `DEFINICAO_LOCALIZACAO`, `ESCOPO_EXECUCAO`) continham
   aspas simples/diplas malformadas no meio da string (`"no "'` + `"melhor local'..."`).
   O código rodava por chance de concatenação de literais, mas o texto acumulava um
   apostrofo espúrio. **Corrigido manualmente** com `edit` antes de executar:
   problema evitado antes de migrar para o relatório final.

3. **Execução e checagem de saída** — rodado `python -m src.fase0_definitions`.
   O console exibiu acentos corrompidos (codepage do Windows), mas os arquivos foram
   escritos em UTF-8. **Verificação do `.md` gerado** confirmou texto íntegro.

## Decisões fechadas (herdadas pelas próximas fases)
- "Melhor" = maior yield líquido anual (NOI/Investimento) com consistência; não é receita bruta.
- "Perfil" = tipologia × quartos × tipo de anúncio × comodidades.
- "Localização" = bairro/mesh, yield em vez de receita bruta.
- Escopo de execução = 2 cenários (A pronto, B lançamento/construção), ambos com custo de operação.
- 5 perguntas RQ1–RQ5 definidas com hipótese + método de validação.

## Senso crítico registrado
- A tese dos compactos no Centro foi registrada como hipótese ("sustenta parcialmente"),
  não como verdade — será confrontada com contrafactuals na Fase 5.
- As premissas financeiras (`PremissasFinanceiras`) são placeholders declarados como
  "a VALIDAR na Fase 2" — não viraram número mágico nesta fase.