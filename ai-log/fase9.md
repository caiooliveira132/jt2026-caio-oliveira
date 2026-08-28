# AI Log — Fase 9 (Vídeo de 3 minutos — roteiro/teleprompter)

Sessão registrada: 2026-08-28 · Ferramenta: opencode (deepseek-v4-flash)

## Prompt solicitado
Fase 9 e Fase 10 do plano: montar o roteiro rígido do vídeo (4 blocos) e o check final
simulando o juiz.

## O que foi feito
- **`roteiro-video.md` reescrito como teleprompter completo**: narração palavra por palavra
  nos 4 blocos obrigatórios (~460 palavras no total, ~150 palavras/min = 3 min):
  1. Recomendação em 2 frases (0:00–0:40) — resultado primeiro, com números.
  2. Raciocínio (0:40–1:20) — critério (yield líquido) + evidências com números.
  3. Como usei IA (1:20–2:00) — obstáculo real (régua 4x irreal) e como driblei.
  4. O que faria com +1 semana (2:00–3:00) — 3-4 ações específicas.
- **`src/fase10_check.py` criado**: simula o juiz e valida automaticamente as regras de
  reprovação do edital.

## Senso crítico
- O roteiro foi desenhado para **não** vender "a IA é maravilhosa": o bloco 3 pede
  explicitamente um obstáculo real e como o decisor (eu) criticou/corrigiu a IA — é o que o
  edital chama de "senso crítico sobre o que a IA devolveu".
- A **restrição crítica do link** (Drive "qualquer pessoa com o link") ficou em destaque no
  topo: link restrito = vídeo não entregue.

## Entregáveis
`roteiro-video.md` (raiz) + `src/fase10_check.py`.