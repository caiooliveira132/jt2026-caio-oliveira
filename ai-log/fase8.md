# AI Log — Fase 8 (Entregáveis: repositório, ai-log/ e relatório)

Sessão registrada: 2026-08-28 · Ferramenta: opencode (deepseek-v4-flash)

## Prompt solicitado
Empacotar os entregáveis: repositório público com README (link do vídeo na 1ª linha),
`relatorio.md` completo, código reexecutável e pasta `ai-log/` com as sessões de IA
completas em texto — sem apagar o que não deu certo.

## O que foi feito
1. **Export da sessão inteira**: `opencode session list` → achada a sessão atual
   `ses_fb742ab18ffeSzrZtkpjEXcTLL`; `opencode export` → JSON (1,5MB). O arquivo veio com BOM
   e status text — limpei e validei. Depois gerei o **.md de leitura** (278KB, 170 mensagens,
   conversa inteira, sem cortes) com `sessao-completa/sessao_desafio.md` + `.json`.
2. **`.gitignore`** (exclui __pycache__, dados brutos); **`requirements.txt`** para reprodução.
3. **README.md** reescrito com o link do vídeo na **1ª linha** (placeholder) e seção
   "avaliar em 2 cliques" (relatorio.md + ai-log).
4. **`ai-log/LEIA-ME.md`** — guia de leitura do log para o avaliador entender o processo.
5. **`PUBLICAR.md`** — passo a passo para criar o repo público no GitHub e push
   (instruções de login via Git Credential Manager).
6. **`roteiro-video.md`** — roteiro de 3 min para o Entregável 2.
7. **Git**: `git init` + commit inicial (64 arquivos, 102k linhas).

## Senso crítico no processo
- **Export veio com sujeira** (BOM + linha de status "Exporting session:...") — detectado por
  falha de parse do JSON, corrigido por leitura binária/poda. O `.md` também foi reescrito
  quando a 1ª versão deu 5KB para 170 mensagens (estrutura do JSON era `parts`, não `content`).
- **Decisão de versionar os outputs CSV grandes** (base_analise 8MB etc.): são entregáveis de
  análise (interpretação, não só código) — mantive. __pycache__/dados brutos excluídos.
- **gh não instalado** — o push fica como passo manual documentado (PUBLICAR.md), o commit
  já está feito localmente com branch main.

## Estado final
Commit `0495fe7` — repo local pronto. Pendências (ações manuais do participante):
criar o repo no GitHub, push, gravar/subir o vídeo e colocar o link no README (1ª linha).