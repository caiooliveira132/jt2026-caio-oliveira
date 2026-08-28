# Fase 0 - Definicoes e criterio-mestre

## Paragrafo formal (critério-mestre)

Maximizar o Yield Líquido Anual (NOI / Investimento Total), com consistência temporal de ocupação e atratividade de clientes como filtros obrigatórios. 'Melhor' NÃO é maior receita absoluta: é lucratividade sistemática e racional no longo prazo, avaliada nos eixos preço de aquisição, preço de aluguel, volatilidade e custo de operação.

**Perfil:** Configuração descritiva do ativo: tipologia (apartamento/casa/studio), número de quartos, tipo de anúncio (inteiro vs. privado/compartilhado) e comodidades ameinities. O melhor perfil é a combinação que maximiza o critério-mestre no melhor local, com foco em lucro de longo prazo, retenção e volume de clientes.

**Localizacao:** Nível de bairro (e grade/mesh quando os dados permitirem), medido pela receita média por noite x ocupação, ponderada por consistência (baixo desvio-padrão) e pelo preço de aquisição da região (VivaReal). Melhor localização = maior yield líquido, não maior receita bruta.

**Escopo de execucao:** A recomendação cobre dois cenários de execução: (A) compra de imóvel pronto e (B) lançamento/construção de novo prédio (captação de proprietários + custos de obra), ambos com custo de operação estimado — pois a Seazone origina prédios e capta proprietários, e a decisão de investimento inclui COMO executar.

## Validação em 2 frases

> 'Melhor' e o que produz o maior yield líquido anual persistente (NOI/Investimento total)
> com baixa volatilidade de ocupacao e aluguel; NAO e a maior receita bruta.

## 5 perguntas fechadas x resposta preliminar

| ID | Pergunta | Fontes | Hipotese preliminar | Como valido |
|---|---|---|---|---|
| RQ1 | Qual perfil de imovel maximiza o criterio-mestre em Itapema (tipologia x quartos x tipo de anuncio x comodidades)? | details, price, vivareal | Grupos compactos (studio/1-2 quartos), anuncio inteiro; vista/cenario como diferenciais de preco. NAO assumir: medir. | Matriz perfil x yield; controlar por host profissional |
| RQ2 | Qual localizacao (bairro) maximiza o criterio-mestre - e nao apenas a receita? | mesh, price, vivareal | Bairros de frente-mar com bom preco/m2 no VivaReal; suspeita de receita alta diferente de retorno alto - abrir a caixa-preta. | Boxplot receita x CV por bairro; yield = NOI/preco de compra por bairro |
| RQ3 | Quais caracteristicas mais explicam a variacao das receitas (host, amenities, quartos, avaliacoes)? | details, hosts | Superhost, n de reviews e presenca de vista/amenidades movem receita mais que quartos; controlar confusao com host profissional. | Regressao simples + interpretacao em termos de negocio |
| RQ4 | O que comprar hoje, quanto custa e qual o retorno estimado (cenario A pronto x cenario B lancamento)? | vivareal, price, realistic_assumptions | 1 ativo concreto no melhor bairro (ex.: apto 1 quarto com vista); comparar A vs B em horizonte de 5 anos. | Toda linha da tabela com premissa justificada em mercado |
| RQ5 | A tese dos compactos no Centro se sustenta nos dados? | details, mesh, price, vivareal | Suspeita de 'sustenta parcialmente': Centro pode ganhar em preco/ocupacao, mas perder em retorno comparado a um bairro alternativo de maior yield. | Grupo compacto-Centro vs. 3 contrafactuals da Fase 5 |
