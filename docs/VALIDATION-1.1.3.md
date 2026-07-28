# Validação da versão 1.1.3

## Falha analisada

A preparação da release foi iniciada corretamente após o CI aprovado, mas o job
reutilizável de imagens-base falhou ao copiar manifestos multi-arquitetura em
paralelo para o GHCR.

Os logs registraram `429 Too Many Requests`, com limite informado pelo próprio
registro de `2000/minute`. As falhas ocorreram durante uploads simultâneos de
múltiplos manifests e blobs de `redis`, `composer` e `python`.

## Causa técnica

O workflow anterior combinava duas características inadequadas ao ambiente:

1. matriz com seis imagens executadas em paralelo;
2. `docker buildx imagetools create`, que copiava todas as arquiteturas e
   attestations de cada imagem oficial.

A aplicação e a VPS compilam e executam somente `linux/amd64`. Portanto, copiar
todos os manifests não agregava compatibilidade ao projeto e multiplicava o
número de requisições ao GHCR.

## Correção aplicada

- espelhamento limitado a `linux/amd64`;
- processamento sequencial das seis imagens-base;
- detecção e reaproveitamento de imagens já existentes;
- até seis tentativas por `pull`, `push` e validação;
- espera exponencial entre tentativas;
- intervalo entre imagens para evitar rajadas no registro;
- validação final das seis imagens no GHCR;
- build das imagens da aplicação limitado a uma publicação por vez;
- validação explícita das imagens-base antes de iniciar os Docker builds.

## Validações preventivas adicionadas ao CI

- parsing YAML de todos os workflows;
- `bash -n` em todos os scripts de implantação;
- rejeição de actions antigas baseadas em versões anteriores;
- rejeição do comando `docker buildx imagetools create`;
- `docker buildx build --check` nos targets `app`, `gateway` e `runtime`;
- validação completa dos metadados antes da preparação da release.

## Resultado esperado

Após o merge em `main`:

1. o CI valida código, workflows, scripts, Compose e Dockerfiles;
2. a release detecta as imagens-base já publicadas;
3. somente imagens ausentes são espelhadas, uma por vez;
4. as três imagens da aplicação são compiladas e publicadas sequencialmente;
5. a tag `v1.1.3` e a GitHub Release são criadas somente após todos os builds
   concluírem com sucesso.
