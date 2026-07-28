# Pull Request — correção de permissão dos scripts e release v1.1.4

## Branch

```text
fix/script-permissions-release-v1.1.4
```

## Título

```text
fix: corrigir validação dos scripts e desbloquear release automática
```

## Descrição

```markdown
## Objetivo

Corrigir a falha de validação observada tanto na Pull Request quanto no push de
merge em `main`, que impediu a execução do workflow automático de build e
release.

## Diagnóstico

O job `Workflows e scripts de implantação` falhava com:

```text
deploy/scripts/mirror-base-images.sh: Permission denied
Process completed with exit code 126
```

O teste executava o script diretamente e dependia do bit executável Unix. A
cópia registrada no repositório estava sem essa permissão. Como o CI de `main`
falhou, o workflow `Build, publish and release` não iniciou a publicação —
comportamento correto para impedir uma release sem validação.

## Correções realizadas

- execução explícita do script de espelhamento por `bash`;
- teste remove deliberadamente o bit executável para validar o cenário de
  arquivos `0644`;
- chamadas entre scripts de deploy e rollback passam a usar `bash`;
- deploy via GitHub Actions não depende mais de `chmod +x`;
- README, Makefile e documentação atualizados;
- workflow reutilizável de imagens-base recebe o SHA exato aprovado pelo CI;
- checkout do espelhamento fixado nesse SHA;
- versão atualizada para `1.1.4`.

## Resultado esperado

1. CI aprovado na Pull Request;
2. CI aprovado após o merge em `main`;
3. build das imagens no GHCR;
4. criação da tag `v1.1.4`;
5. criação da GitHub Release com ZIP, TAR.GZ, lista de imagens e checksums.

## Validações

- scripts Shell validados com `bash -n`;
- teste de espelhamento executado com o script sem bit executável;
- workflows YAML validados;
- metadados da versão validados;
- testes Laravel e Python aprovados;
- Docker Compose validado;
- Dockerfiles verificados.
```

## Mensagem de commit

```text
fix: remover dependência de permissão executável nos scripts
```

## Mensagem de merge

```text
fix: desbloquear CI e release com execução explícita via bash
```
