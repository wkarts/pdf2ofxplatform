# Validação da versão 1.1.7

## Escopo

A versão adiciona a implantação do PDF2OFX gerenciada pelo Dockge, preservando
a implantação Docker Compose já existente.

## Validações realizadas

- `bash -n` em todos os scripts Shell de `deploy/`;
- leitura YAML dos workflows e arquivos Compose;
- `deploy/scripts/validate-version.sh`;
- confirmação de que `deploy/dockge/pdf2ofx/compose.yaml` utiliza somente imagens
  versionadas, sem build no servidor;
- confirmação de que as portas 5001 e 8080 são vinculadas somente a
  `127.0.0.1`;
- confirmação de que Redis, PostgreSQL, FastAPI e PHP-FPM não publicam portas;
- geração de chaves por `openssl` com caracteres seguros para URL e `.env`;
- preservação do `.env` em reinstalações, salvo uso explícito de `--force-env`;
- validação da autenticação opcional no GHCR;
- inclusão do pacote Dockge no workflow de GitHub Release;
- validação dos modelos do CloudPanel e dos scripts operacionais.

## Estrutura esperada na VPS

```text
/opt/dockge/compose.yaml
/opt/dockge/.env
/opt/dockge/data/
/opt/stacks/pdf2ofx/compose.yaml
/opt/stacks/pdf2ofx/.env
/opt/stacks/pdf2ofx/scripts/
/opt/stacks/pdf2ofx/backups/
```

## Resultado esperado

Após a execução de `deploy/dockge/install-vps.sh`, o Dockge fica disponível em
`127.0.0.1:5001`, a aplicação em `127.0.0.1:8080`, as migrations são executadas
e o endpoint `/health` é validado.
