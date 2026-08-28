# Pasta ai-log/ — como você está vendo meu processo de trabalho

Esta pasta é o registro de como a IA foi usada no desafio (30% da avaliação).

## O que você encontrará

| Arquivo | O que é |
|---|---|
| `sessao-completa/sessao_desafio.md` | **Conversa inteira** com a IA (232 mensagens, toda a jornada do desafio), exportada via `opencode export`, em formato de leitura humana. |
| `sessao-completa/sessao_desafio.json` | O mesmo export em JSON (formato original da ferramenta). |
| `fase0.md` … `fase10.md` | Para cada fase, o que foi pedido, o que a IA devolveu, o que eu critiquei/corrigi e os números-chave. |
| `saneamento.md` | Registro rastreável de TODAS as correções de dados (Fase 1). |
| `LEIA-ME.md` | Este guia. |

> **Como atualizar/reesportar** a sessão (comando): `opencode session list` → pega o ID → `opencode export <ID>`.

## O que você deveria observar (o processo, não o resultado)

1. **Iteração**: erros aconteceram e foram corrigidos. Ex.: a 1ª versão da régua comparava
   construir a R$4.200/m² com comprar a R$16k/m² ("4x" irreal) — refeita com produção ≈ 75% da revenda.
2. **Persistência**: o veredito da tese passou por 2 iterações até ser honesto (a 1ª disse
   "sustenta" só porque o grupo era o "menos pior"; a versão final pesa o cenário otimista
   de ocupação e encontra **Morretes** como o melhor bairro).
3. **Senso crítico**: recusei outputs da IA que "cheiravam a número mágico" — revisando
   premissas, distinguindo correlação de causa e declarando limitações (R²=0,09, proxy de ocupação).
4. **Código sobre "achismo"**: tudo é executável (`src/fase0..7.py`) — você pode rodar a cadeia
   inteira em `python -m src.faseN`.

## Para reproduzir
Cada arquivo `src/faseN_*.py` tem um `__main__` que regenera os outputs de `output/`.