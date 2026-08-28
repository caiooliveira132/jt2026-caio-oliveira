# Como publicar no GitHub (passo a passo)

O repositório está pronto e commitado localmente. Falta criar o repositório remoto
**público** com o nome exigido pelo edital e enviar.

## Passo 1 — Criar o repositório público no GitHub.com

1. Acesse [github.com/new](https://github.com/new)
2. Nome: `jt2026-caio-oliveira` (formato: `jt2026-primeiro-ultimo-nome`)
3. Visibilidade: **Public**
4. Não inicialize com README/.gitignore (já existem)
5. Crie o repositório

## Passo 2 — Conectar o remoto e enviar

Na pasta deste projeto, rode:

```bash
git remote add origin https://github.com/CaioOliveira132/jt2026-caio-oliveira.git
git branch -M main
git push -u origin main
```

> O primeiro push vai abrir o Git Credential Manager pedindo login no GitHub
> (pop-up do navegador). Autorize.

## Passo 3 — Vídeo (ENTREGÁVEL 2)

1. Grave o vídeo de até 3 min (sugestão de roteiro no `ai-log/../roteiro-video.md`).
2. Suba no Google Drive com compartilhamento **"Qualquer pessoa com o link"**.
3. Cole o link na **1ª linha do README.md** e faça `git add README.md && git commit -m "abre link do video" && git push`.

## Checklist final do avaliador

- [ ] Repositório público com nome correto (`jt2026-caio-oliveira`)
- [ ] Link do vídeo na 1ª linha do README, acessível sem login
- [ ] `relatorio.md` com a recomendação e a posição sobre a tese dos compactos
- [ ] `ai-log/sessao-completa/sessao_desafio.md` + `.json` (conversa inteira)
- [ ] Código rodável (`python -m src.faseN`) + `requirements.txt`
- [ ] Outputs organizados em `output/`