# Como publicar no GitHub (passo a passo — ATUALIZADO)

O repositório está pronto e commitado localmente na branch **`main`**, com o remote já
configurado. **Falta criar o repositório no site do GitHub** e rodar o push.

## Passo 1 — CRIAR o repositório público no GitHub.com (obrigatório)

> ⚠️ **Este é o passo que falta.** O push falha com "Repository not found" porque o
> repositório `jt2026-caio-oliveira` ainda não existe no site.

1. Acesse [github.com/new](https://github.com/new) (logado como **CaioOliveira132**)
2. Nome do repositório: `jt2026-caio-oliveira`
3. Visibilidade: **Public**
4. Deixe desmarcado "Add a README" / ".gitignore" (já existem no seu repositório local)
5. Clique em **Create repository**

## Passo 2 — Rodar o push (já está tudo configurado)

Na pasta deste projeto:

```bash
git push -u origin main
```

> O primeiro push pode abrir o Git Credential Manager pedindo login no GitHub. Autorize.
> Branches: o projeto está em `main` (padronizado).

## Passo 3 — Conferir (antes de enviar o formulário)

1. Abra o link em **janela anônima** (deslogado): https://github.com/CaioOliveira132/jt2026-caio-oliveira
2. Confirme que abre sem login ✅ (se pedir login, o repo não está Public)
3. Confirme também o vídeo em janela anônima: [Google Drive](https://drive.google.com/file/d/1SYOkXpITNIz9YnpqL8o3qAaENeqXUPb1/view?usp=sharing) (Testado: HTTP 200 ✅)
4. Depois do push, rode `python -m src.fase10_check` para reconfirmar o "Remoto origin" como OK

## Checklist final do avaliador

- [ ] Repositório público com nome `jt2026-caio-oliveira` (criar em Passo 1)
- [ ] Link do vídeo na 1ª linha do README (corrigido — já está clicável)
- [ ] `relatorio.md` com a recomendação e posição sobre a tese dos compactos ✅
- [ ] `ai-log/sessao-completa/` com a conversa inteira (md + json, 232 msgs) ✅
- [ ] Código rodável (`python -m src.faseN`) + `requirements.txt` ✅
- [ ] Outputs organizados em `output/` ✅
- [ ] Enviar os dois links no formulário de entrega (uma única vez)