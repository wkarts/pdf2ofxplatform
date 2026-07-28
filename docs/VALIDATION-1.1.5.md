# Validação da versão 1.1.5

## Diagnóstico dos logs

A preparação da release, o espelhamento das imagens-base e o build do conversor
foram concluídos. Os targets `pdf2ofx-app` e `pdf2ofx-gateway` falharam durante
a construção do estágio PHP.

A falha ocorreu no comando `pecl install redis`:

```text
Package "redis" Version "6.3.0" does not have REST xml available
install failed
```

Como o job de GitHub Release depende da publicação das três imagens, a release
foi corretamente bloqueada.

## Correções

- removida a instalação da extensão Redis pelo endpoint REST do PECL;
- PhpRedis compilado de um tarball versionado do repositório oficial;
- download protegido por retry e falha explícita;
- runtime valida se a extensão Redis foi efetivamente carregada;
- gateway desacoplado do estágio `app`;
- CI passa a compilar integralmente os targets `app`, `gateway` e `runtime`;
- CI executa validações reais dos runtimes;
- criado pacote completo e independente de implantação Docker em
  `deploy/docker`.

## Validações locais executadas

- sintaxe PHP;
- compilação dos módulos Python;
- testes Python;
- sintaxe Shell de todos os scripts;
- carregamento YAML dos workflows e arquivos Compose;
- consistência da versão;
- consistência dos modelos `.env`;
- validação da estrutura do pacote Docker;
- ausência de `pecl install redis`;
- ausência de dependência `COPY --from=app` no gateway;
- integridade do ZIP e do patch.

## Validação a ser executada no GitHub Actions

O CI agora executará build real das três imagens antes do merge. A release só
será iniciada quando:

1. Laravel passar;
2. conversor Python passar;
3. Compose e workflows passarem;
4. `pdf2ofx-app` compilar e carregar `redis`;
5. `pdf2ofx-gateway` passar em `nginx -t`;
6. `pdf2ofx-converter` importar o pacote e expor a versão correta.
