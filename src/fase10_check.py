from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from .config import ROOT, OUTPUT_DIR, AI_LOG_DIR

OK_S = "[ OK ]"
WARN_S = "[PEND ]"
FAIL_S = "[FALHA]"


def check(nome: str, ok: bool, critico: bool, detalhe: str = "") -> dict:
    return {"nome": nome, "ok": ok, "critico": critico, "detalhe": detalhe}


def main():
    c = lambda *a: subprocess.run(a, capture_output=True, text=True, cwd=str(ROOT))
    resultados = []

    # 1. Repositório
    git = c("git", "rev-parse", "--is-inside-work-tree")
    resultados.append(check(
        "Repositório git inicializado", git.returncode == 0, True,
        "" if git.returncode == 0 else "execute: git init",
    ))

    c("git", "remote", "get-url", "origin")
    remote_ok = c("git", "remote", "get-url", "origin").returncode == 0
    resultados.append(check(
        "Remoto origin configurado (push manual pendente)", remote_ok, False,
        "gh não instalado — ver PUBLICAR.md" if not remote_ok else "",
    ))

    # 2. README: link do vídeo na 1ª linha
    readme = (ROOT / "README.md")
    primeira = readme.read_text(encoding="utf-8").splitlines()[0] if readme.exists() else ""
    tem_link = "drive.google.com" in primeira and "https" in primeira
    eh_placeholder = "COLAR" in primeira or "placeholder" in primeira.lower()
    resultados.append(check(
        "Vídeo: link publicado na 1ª linha do README (Drive, sem login)",
        tem_link and not eh_placeholder, True,
        "AÇÃO PENDENTE: gravar/subir vídeo e colar o link (roteiro-video.md) — regra de reprovação" if not (tem_link and not eh_placeholder) else "",
    ))

    # 3. relatorio.md com os 4 blocos + tese + definições
    rel = (ROOT / "relatorio.md")
    rel_txt = rel.read_text(encoding="utf-8") if rel.exists() else ""
    blocos = ["Melhor perfil", "Melhor localização", "Características que explicam",
              "O que comprar", "tese", "Morretes"]
    faltam = [b for b in blocos if b.lower() not in rel_txt.lower()]
    resultados.append(check(
        "relatorio.md responde as 4 perguntas + tese dos compactos",
        rel.exists() and not faltam, True,
        "faltam seções: " + ", ".join(faltam) if faltam else "",
    ))
    tem_num = any(s in rel_txt for s in ("%", "R$", "0.33", "7.14"))
    resultados.append(check(
        "Recomendação com NÚMEROS vindos dos dados (não tolice)",
        tem_num, True, "sem números no relatorio.md?" if not tem_num else "",
    ))
    tem_def = all(s in rel_txt for s in ["Yield", "Melhor", "Perfil", "Localização"])
    resultados.append(check(
        "Definiu formalmente melhor/perfil/localização",
        tem_def, True,
    ))

    # 4. ai-log/ completo
    sess_md = AI_LOG_DIR / "sessao-completa" / "sessao_desafio.md"
    sess_json = AI_LOG_DIR / "sessao-completa" / "sessao_desafio.json"
    fases = list(AI_LOG_DIR.glob("fase*.md"))
    ok_sess = sess_md.exists() and sess_json.exists()
    tamanho_ok = sess_md.stat().st_size > 100_000 if sess_md.exists() else False
    resultados.append(check(
        "ai-log/ com conversa completa (md+json, >100KB) — processo visível",
        ok_sess and tamanho_ok, True,
        "export pendente — rode: opencode export <ID>" if not ok_sess else "",
    ))
    resultados.append(check(
        f"ai-log/ com logs por fase ({len(fases)} fases registradas)",
        len(fases) >= 7, True,
    ))

    # 5. Código reexecutável
    srcs = list((ROOT / "src").glob("fase*.py"))
    resultados.append(check(
        f"Código reexecutável: {len(srcs)} módulos em src/ + requirements.txt",
        len(srcs) >= 8 and (ROOT / "requirements.txt").exists(), True,
    ))

    # 6. Outputs
    outs = list((ROOT / "output").glob("*"))
    resultados.append(check(
        f"Outputs organizados em output/ ({len(outs)} arquivos)",
        len(outs) >= 10, False,
    ))

    # --- Relatório ---
    linhas = [
        "# Check final — simulação do juiz (Fase 10)",
        "",
        f"Gerado em: (automático) · ferramenta: opencode",
        "",
        "## Resultado por regra",
        "",
        "| # | Regra (reprovação imediata se falhar) | Situação |",
        "|---|---|---|",
    ]
    for i, r in enumerate(resultados, 1):
        estado = OK_S if r["ok"] else (WARN_S if not r["critico"] else FAIL_S)
        linhas.append(f"| {i} | {r['nome']} | {estado} {r['detalhe']} |")

    pend = [r for r in resultados if not r["ok"]]
    falhas = [r for r in pend if r["critico"]]
    linhas += [
        "",
        "## Resumo",
        "",
        f"- Regras reprobatórias atendidas: **{len(resultados)-len(falhas)}/{len(resultados)}**.",
    ]
    if falhas:
        linhas.append("")
        linhas.append("### Pendências que podem reprovar (ação obrigatória):")
        for r in falhas:
            linhas.append(f"- **{r['nome']}** — {r['detalhe'] or 'verifique'}")
    linhas += [
        "",
        "## Próximos passos automáticos para o participante",
        "1. Gravar/subir o vídeo no Drive ('qualquer pessoa com o link') e colar o link na 1ª linha do README.",
        "2. `git remote add origin https://github.com/CaioOliveira132/jt2026-caio-oliveira.git && git branch -M main && git push -u origin main` (ver PUBLICAR.md).",
        "3. Re-rodar `python -m src.fase10_check` para confirmar tudo verde.",
    ]
    texto = "\n".join(linhas) + "\n"
    (OUTPUT_DIR / "fase10_checklist.md").write_text(texto, encoding="utf-8")

    # console
    print("=" * 74)
    print("CHECK FINAL — SIMULAÇÃO DO JUIZ")
    print("=" * 74)
    for r in resultados:
        est = OK_S if r["ok"] else (WARN_S if not r["critico"] else FAIL_S)
        print(f"  {est:8s} {r['nome']}" + (f"  — {r['detalhe']}" if r["detalhe"] else ""))
    print(f"\nRegras reprobatórias atendidas: {len(resultados)-len(falhas)}/{len(resultados)}")
    print("Relatório: output/fase10_checklist.md")


if __name__ == "__main__":
    main()