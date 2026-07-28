# Pull Request 1.1.6

## Branch

```text
fix/gateway-runtime-validation-v1.1.6
```

## Título

```text
fix: corrigir validação isolada do gateway e liberar a release
```

## Descrição

```markdown
## Objetivo

Corrigir a falha do job `Build real gateway`, que impedia o CI de `main` de
concluir e, consequentemente, bloqueava o workflow automático de build, GHCR e
GitHub Release.

## Diagnóstico

A imagem NGINX foi compilada corretamente. A falha acontecia somente ao executar
`nginx -t` em um container isolado:

```text
host not found in upstream "app:9000"
```

O hostname `app` é criado pelo DNS interno do Docker Compose em produção. A
validação anterior não conectava o container a essa resolução de nomes.

## Correções realizadas

- criado `deploy/scripts/validate-gateway-image.sh`;
- validação do NGINX executada com o hostname `app` disponível;
- inicialização real do container do gateway durante o CI;
- validação do endpoint `/health` além do teste sintático;
- logs do container exibidos automaticamente em caso de falha;
- limpeza garantida do container temporário;
- `validate-version.sh` reforçado para exigir o novo mecanismo;
- versão atualizada para `1.1.6`;
- documentação, changelog e pacote Docker atualizados.

## Resultado esperado

1. os três builds reais do CI são aprovados;
2. o merge em `main` conclui o workflow `CI`;
3. `Build, publish and release` é iniciado automaticamente;
4. as imagens `app`, `gateway` e `converter` são publicadas no GHCR;
5. a tag `v1.1.6` e a GitHub Release são criadas;
6. os pacotes de código e de implantação Docker são anexados à release.

## Validações

- scripts Shell validados;
- workflows YAML validados;
- metadados da versão validados;
- testes Python aprovados;
- sintaxe PHP aprovada;
- pacote Docker independente validado;
- ZIP, TAR.GZ e checksums gerados.
```

## Mensagem de commit

```text
fix: validar gateway com resolução do upstream Docker
```

## Mensagem de merge

```text
fix: liberar CI e release com validação correta do gateway
```
