# Tabela de premissas financeiras — Fase 2

Fonte de cada valor: (1) mercado Itapema medido na base; (2) padrão de mercado; (3) suposição documentada.

| Parâmetro | Valor | Unidade | Fonte |
|---|---|---|---|
| itbi_registro_pct | 0.0350 | % do preço de compra | Mercado SC: ITBI ~3% + registro ~0,5% (fonte: tabela municipal Itapema / prática notarial) |
| reforma_mobilia_pct | 0.0800 | % do preço de compra | Suposição: mobiliar/equipar apto para short stay (mercado Itapema; validar com orçamento) |
| capital_giro_meses_A | 3.0000 | meses | Suposição de prudência: 3 meses de custo operacional até estabilização |
| captacao_por_unidade | 40,000.0000 | R$/unidade | Suposição de originação: prospecção, contrato e comissão de captação de proprietário (calibrar com comercial Seazone) |
| mkt_to_producao_ratio | 0.7500 | taxa sobre revenda m² | Custo de PRODUÇÃO all-in (terreno + obra + projeto + incorporação) ≈ 75% do preço de revenda observado por m² no bairro. Captura a margem/dev markup que se paga ao comprar pronto; construir = capturar esse delta. Validar com VGV/planilha de incorporação na Fase 6. |
| projeto_permutas_pct_obra | 0.1000 | % da obra | Suposição: projeto arquitetônico/estrutural, licenciamento e permutas = 10% do custo de obra |
| marketing_pre_venda_pct_obra | 0.0400 | % da obra | Suposição: marketing/incorporação de pré-venda = 4% da obra |
| contingencia_pct_obra | 0.0800 | % da obra | Suposição: contingência de obra/repasses = 8% da obra |
| capital_giro_meses_B | 6.0000 | meses | Suposição de prudência: 6 meses de custo operacional até estabilização (prazo de obra maior) |
| taxa_gestao_seazone | 0.2000 | % da receita bruta | Padrão de mercado gerenciadora short stay (20-30%); a confirmar com comercial Seazone |
| taxa_canais | 0.1000 | % da receita bruta | Suposição: comissões de distribuição em múltiplos canais (Airbnb/Vrbo/OTA) diluídas |
| custo_limpeza_por_virada | 130.0000 | R$/virada | Mercado Itapema: diária de profissional de limpeza + insumos base (cleaning_fee mediano anunciado R$250 cobre mais que o custo real) |
| consumiveis_por_diaria | 18.0000 | R$/diária ocupada | Suposição: consumíveis/amenities por diária ocupada (amaciante, papel, café, reposição) |
| estada_media_noites | 4.0000 | noites/turnover | Suposição de estada média curta temporada litoral catarinense (3-5 noites) |
| manutencao_pct_ano_pronto | 0.0150 | % do preço/ano | Suposição conservadora: manutenção anual imóvel usado = 1,5% do preço de compra |
| manutencao_pct_ano_novo | 0.0070 | % do custo obra/ano | Suposição: imóvel novo tem manutenção menor = 0,7% do custo de obra (vantagem do cenário B) |
| energia_internet_mensal | 380.0000 | R$/mês | Suposição: energia (clima praia) + internet em curta temporada, média anual |
| seguros_pct_ano | 0.0030 | % do valor/ano | Mercado seguradoras: seguro residencial locação temporária ≈ 0,3% do valor por ano |
| cv_preco_diaria | 0.2500 | desvio/média | Placeholder: volatilidade da diária; será calibrada por bairro/perfil na Fase 3 com Price_AV |
| cv_ocupacao | 0.3500 | desvio/média | Placeholder: sazonalidade da ocupação; será calibrada na Fase 3 |
| occ_base_exemplo | 0.3000 | taxa anual | Cenário base para exemplo da máquina; ocupação real por bairro/perfil virá da Fase 3 (proxy observado 0.17 = piso pessimista) |
