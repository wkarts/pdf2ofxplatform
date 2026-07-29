# PDF2OFX — stack pronta para Dockge

Distribuição destinada a uma VPS que **já possui**:

- Docker Engine;
- Docker Compose V2;
- Dockge configurado com o diretório de stacks, normalmente `/opt/stacks`;
- CloudPanel funcionando como proxy reverso e responsável pelo SSL.

Este pacote **não instala** Docker, Dockge ou CloudPanel. Ele somente cria e parametriza a nova stack PDF2OFX.

## Estrutura

```text
pdf2ofx/
├── compose.yaml
├── .env.example
├── VERSION
├── backups/
├── cloudpanel/
└── scripts/
    ├── configure.sh
    ├── preflight.sh
    ├── deploy.sh
    ├── post-deploy.sh
    ├── update.sh
    ├── rollback.sh
    ├── backup.sh
    ├── restore.sh
    ├── healthcheck.sh
    ├── status.sh
    └── logs.sh
```

## 1. Copiar para o diretório de stacks

```bash
sudo mkdir -p /opt/stacks/pdf2ofx
sudo chown -R "$USER":"$USER" /opt/stacks/pdf2ofx
unzip pdf2ofx-stack-deployment-1.2.0.zip -d /tmp/pdf2ofx-stack
cp -a /tmp/pdf2ofx-stack/pdf2ofx-stack-deployment-1.2.0/. /opt/stacks/pdf2ofx/
cd /opt/stacks/pdf2ofx
```

## 2. Autenticar no GHCR

Quando os pacotes estiverem privados:

```bash
echo "$GHCR_TOKEN" | docker login ghcr.io -u wkarts --password-stdin
```

O token precisa de permissão `read:packages`. Ele não é gravado no `.env` da aplicação.

## 3. Parametrizar

```bash
bash scripts/configure.sh \
  --domain pdf2ofx.seudominio.com.br \
  --version 1.2.0 \
  --namespace wkarts \
  --port 8080
```

O script gera:

- `APP_KEY`;
- senha PostgreSQL;
- senha Redis;
- chave interna Laravel/FastAPI;
- URLs e imagens versionadas;
- `.env` protegido com permissão `0600`.

Para recriar credenciais deliberadamente, use `--force`.

## 4. Subir a stack

Pelo terminal:

```bash
bash scripts/deploy.sh
```

Ou pelo Dockge:

1. execute **Scan Stacks Folder** caso a stack ainda não apareça;
2. abra `pdf2ofx`;
3. confira `compose.yaml` e `.env`;
4. use **Pull**;
5. use **Deploy/Update**;
6. execute no terminal da stack:

```bash
bash /opt/stacks/pdf2ofx/scripts/post-deploy.sh
```

O pós-deploy executa migrations, cache Laravel, reinício da fila e health check.

## 5. Reverse Proxy no CloudPanel

Crie um site **Reverse Proxy**:

```text
Domínio: pdf2ofx.seudominio.com.br
Destino: http://127.0.0.1:8080
```

Ative SSL e redirecionamento HTTPS. Consulte `cloudpanel/README.md` para os ajustes de upload e timeout.

## Atualização

```bash
cd /opt/stacks/pdf2ofx
bash scripts/update.sh 1.2.1
```

## Rollback

```bash
bash scripts/rollback.sh 1.2.0
```

## Operação

```bash
bash scripts/status.sh
bash scripts/healthcheck.sh
bash scripts/logs.sh
bash scripts/logs.sh converter-worker
bash scripts/backup.sh
```

## Portas

Somente o gateway é vinculado ao host:

```text
127.0.0.1:8080 -> gateway NGINX
```

PostgreSQL, Redis, FastAPI, Celery e PHP-FPM permanecem na rede interna da stack.
