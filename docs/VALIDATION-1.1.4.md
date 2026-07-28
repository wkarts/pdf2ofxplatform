# Validação da versão 1.1.4

## Falha analisada

Os dois conjuntos de logs — validação da Pull Request e execução após o merge em
`main` — falharam no job **Workflows e scripts de implantação** com código de
saída `126`:

```text
deploy/scripts/tests/test-mirror-base-images.sh: line 56:
deploy/scripts/mirror-base-images.sh: Permission denied
Process completed with exit code 126
```

Os jobs Laravel, conversor, Compose, metadados e validação estática dos
Dockerfiles foram concluídos. Como o workflow `CI` em `main` terminou com falha,
o workflow de release, corretamente condicionado a `conclusion == success`, não
prosseguiu para build, publicação no GHCR ou criação da GitHub Release.

## Causa técnica

O teste chamava o script de espelhamento diretamente:

```bash
"$ROOT_DIR/deploy/scripts/mirror-base-images.sh"
```

A cópia versionada no GitHub não preservou o bit executável. Embora o arquivo
possuísse `#!/usr/bin/env bash`, o kernel recusou a execução antes de iniciar o
Bash.

A automação não deve depender do modo Unix do arquivo, porque projetos enviados
por ZIP, interface web, Windows ou algumas integrações podem registrar scripts
como `0644`.

## Correções aplicadas

- o teste invoca o espelhamento explicitamente com `bash`;
- o teste remove propositalmente o bit executável antes da execução, garantindo
  que a regressão seja detectada;
- chamadas entre scripts (`deploy`, `rollback` e `healthcheck`) usam `bash`;
- o deploy por SSH não depende mais de `chmod +x`;
- exemplos do README, Makefile e documentação usam `bash script.sh`;
- o workflow reutilizável de espelhamento recebe o SHA validado e faz checkout
  exatamente desse commit;
- a release fornece `source_sha` ao workflow de imagens-base, evitando usar uma
  revisão diferente caso `main` avance durante a execução;
- metadados atualizados para a versão `1.1.4`.

## Validações preventivas

- `bash -n` em todos os scripts;
- execução do teste de retry com o script alvo sem permissão de execução;
- parsing YAML dos workflows;
- validação dos metadados da versão;
- testes Laravel e Python;
- compilação dos módulos Python;
- validação do Docker Compose;
- verificação estática dos targets Docker `app`, `gateway` e `runtime`.

## Resultado esperado após o merge

1. o CI da Pull Request é aprovado mesmo que scripts estejam registrados como
   `0644`;
2. o CI do push em `main` também é aprovado;
3. `Build, publish and release` recebe o commit exato aprovado;
4. imagens-base e imagens da aplicação são publicadas;
5. a tag `v1.1.4` e a GitHub Release são criadas somente após os builds passarem.
