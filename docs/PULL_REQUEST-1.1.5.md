# Pull Request — build Redis e implantação Docker v1.1.5

## Branch

```text
fix/phpredis-build-and-docker-deployment-v1.1.5
```

## Título

```text
fix: corrigir build das imagens e adicionar implantação Docker completa
```

## Objetivo

Corrigir a falha de build causada pela indisponibilidade do XML REST do PECL e
entregar um modelo completo de implantação Docker/GHCR para CloudPanel.

## Alterações

- substituição de `pecl install redis` pela compilação de PhpRedis 6.3.0 a
  partir do código-fonte versionado;
- retry no download da extensão;
- validação da extensão no build e no CI;
- gateway NGINX independente do estágio PHP;
- build real das três imagens dentro do CI;
- validação de runtime para PHP, Redis, Artisan, NGINX e Python;
- pacote `deploy/docker` com Compose, `.env`, instalação, atualização,
  rollback, backup, restauração, status, logs e health check;
- modelos CloudPanel e systemd;
- documentação completa de implantação;
- versão atualizada para 1.1.5.

## Resultado esperado

Após o merge em `main`, o CI compila integralmente os três targets. Com todos
aprovados, o fluxo publica as imagens no GHCR, cria a tag `v1.1.5` e publica a
GitHub Release com os pacotes e checksums.

## Mensagem de commit

```text
fix: estabilizar build Redis e incluir implantação Docker completa
```

## Mensagem de merge

```text
fix: publicar imagens e release com pacote Docker de produção
```
