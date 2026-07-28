# Pull Request — correção das validações e limite do GHCR v1.1.3

## Branch

```text
fix/ghcr-rate-limit-validations-v1.1.3
```

## Título

```text
fix: corrigir validações e evitar limite de requisições no GHCR
```

## Descrição

```markdown
## Objetivo

Corrigir a falha do workflow `Build, publish and release` causada por excesso de
requisições ao GitHub Container Registry durante o espelhamento das
imagens-base.

## Diagnóstico

A preparação da release foi concluída corretamente. A falha ocorreu nos jobs de
espelhamento de `redis`, `composer` e `python`, todos com:

```text
429 Too Many Requests
allowed: 2000/minute
```

O workflow anterior executava seis cópias em paralelo e usava
`docker buildx imagetools create`, copiando manifests de todas as arquiteturas e
attestations. O projeto publica e executa apenas imagens `linux/amd64`, tornando
essa carga desnecessária.

## Correções realizadas

- removido o espelhamento multi-arquitetura;
- espelhamento restrito a `linux/amd64`;
- imagens processadas sequencialmente;
- imagens já existentes são detectadas e ignoradas;
- adicionadas seis tentativas com espera exponencial;
- adicionada pausa entre publicações;
- validação final das seis imagens-base;
- builds da aplicação limitados a `max-parallel: 1`;
- validação das imagens-base antes da compilação;
- validação integral dos metadados na preparação da release;
- actions atualizadas para runtimes Node.js 24;
- validação YAML dos workflows;
- validação sintática dos scripts Shell;
- verificação estática dos três Dockerfiles;
- versão atualizada para `1.1.3`.

## Resultado esperado

1. o CI valida todos os componentes e arquivos de automação;
2. imagens-base existentes não são republicadas;
3. imagens ausentes são espelhadas uma por vez;
4. falhas transitórias do GHCR são repetidas automaticamente;
5. as imagens da aplicação são publicadas sequencialmente;
6. a tag e a GitHub Release são criadas somente após todos os builds passarem.

## Validações

- metadados da versão validados;
- workflows YAML validados;
- scripts Shell validados;
- módulos Python compilados;
- sintaxe PHP validada;
- Docker Compose validado;
- pacote ZIP e checksum validados.
```

## Mensagem de commit

```text
fix: serializar uploads e reforçar validações do GHCR
```

## Mensagem de merge

```text
fix: corrigir release e validações contra rate limit do GHCR
```
