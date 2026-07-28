# Pull Request — automação de build e release v1.1.2

## Branch

```text
fix/automatic-build-release-v1.1.2
```

## Título

```text
fix: automatizar build GHCR e GitHub Release após CI aprovado
```

## Descrição

```markdown
## Objetivo

Corrigir o fluxo de publicação do PDF2OFX Platform. O CI era concluído com
sucesso, porém nenhum build de container e nenhuma GitHub Release eram gerados,
pois os workflows dependiam exclusivamente de uma tag criada manualmente.

## Causa identificada

- `build-images.yml` era executado apenas por `push` de tags `v*.*.*` ou por
  acionamento manual;
- `release.yml` era executado apenas por `push` de tags `v*.*.*`;
- o merge em `main` executava somente o CI e não criava a tag necessária;
- o espelhamento das imagens-base era um procedimento manual separado.

## Correções realizadas

- criado fluxo automático após o workflow `CI` concluir com sucesso em `main`;
- release vinculada exatamente ao commit aprovado pelo CI;
- espelhamento automático das imagens-base no GHCR;
- build e publicação das imagens:
  - `pdf2ofx-app`;
  - `pdf2ofx-gateway`;
  - `pdf2ofx-converter`;
- publicação das tags `X.Y.Z`, `X.Y`, `sha-*` e `latest`;
- criação automática da tag Git `vX.Y.Z`;
- criação automática da GitHub Release;
- geração de ZIP, TAR.GZ, lista de imagens e checksums SHA-256;
- preservação dos arquivos também como artifact do GitHub Actions;
- prevenção contra republicação ou movimentação acidental de uma versão;
- validação da consistência de versão no CI;
- validação da existência da release e das imagens antes do deploy;
- correção da URL do repositório na documentação de implantação;
- versão atualizada para `1.1.2`.

## Comportamento esperado após o merge

1. o push em `main` executa o workflow `CI`;
2. com o CI aprovado, inicia `Build, publish and release`;
3. as imagens-base são espelhadas no GHCR;
4. as três imagens da aplicação são compiladas e publicadas;
5. a tag `v1.1.2` é criada;
6. a GitHub Release `PDF2OFX Platform v1.1.2` é publicada com os artefatos.

## Validações executadas

- 15 testes Python aprovados;
- módulos Python compilados;
- 24 arquivos PHP validados sintaticamente;
- arquivos YAML carregados sem erros;
- scripts Shell validados;
- metadados da versão `1.1.2` validados;
- pacote ZIP e patch de atualização gerados.
```

## Commit

```text
fix: automatizar build e release após CI aprovado
```

## Mensagem de merge

```text
fix: publicar imagens GHCR e release automaticamente após CI (#PR)
```
