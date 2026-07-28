# Implantação

A implantação oficial utiliza **Docker Compose + GHCR + CloudPanel Reverse
Proxy**. Não é necessário instalar PHP, Composer, Python, PostgreSQL, Redis,
Tesseract ou NGINX da aplicação diretamente na VPS.

## Modelo recomendado

```text
Internet
   │
   ▼
CloudPanel / NGINX / TLS :443
   │
   ▼
127.0.0.1:8080
   │
   ▼
Docker gateway
   ├── Laravel/PHP-FPM
   ├── Queue e Scheduler
   ├── FastAPI e Celery/OCR
   ├── Redis
   └── PostgreSQL
```

## Pacote pronto de implantação

Todos os arquivos operacionais estão em:

```text
deploy/docker/
```

A documentação completa, incluindo instalação inicial, atualização, rollback,
backup, restauração, systemd e CloudPanel, está em:

```text
deploy/docker/README.md
```

## Instalação rápida

```bash
sudo mkdir -p /opt/pdf2ofx
sudo chown "$USER":"$USER" /opt/pdf2ofx
git clone https://github.com/wkarts/pdf2ofxplatform.git /opt/pdf2ofx
cd /opt/pdf2ofx/deploy/docker

export GHCR_USER=wkarts
export GHCR_TOKEN='TOKEN_COM_READ_PACKAGES' # somente para pacotes privados

bash install.sh \
  --domain https://pdf2ofx.codisplan.com.br \
  --version 1.1.7 \
  --namespace wkarts \
  --port 8080
```

No CloudPanel, crie **Create a Reverse Proxy** apontando para:

```text
http://127.0.0.1:8080
```

## Implantação gerenciada pelo Dockge

O pacote `deploy/dockge/` prepara o gerenciador e a stack no padrão oficial de
diretórios do Dockge:

```text
/opt/dockge
/opt/stacks/pdf2ofx/compose.yaml
```

Instalação completa:

```bash
cd deploy/dockge
export GHCR_USER=wkarts
export GHCR_TOKEN='TOKEN_COM_READ_PACKAGES' # somente para imagens privadas
sudo -E bash install-vps.sh \
  --domain https://pdf2ofx.codisplan.com.br \
  --version 1.1.7 \
  --namespace wkarts
```

Destinos no CloudPanel:

```text
Aplicação: http://127.0.0.1:8080
Dockge:    http://127.0.0.1:5001
```

A exposição web do Dockge é opcional. Para maior isolamento, mantenha a porta
somente no loopback e acesse por túnel SSH. A documentação completa está em
`deploy/dockge/README.md`.

## Build, GHCR e GitHub Release

O merge em `main` dispara o workflow **CI**. Depois de todas as validações e
builds reais dos containers, o workflow **Build, publish and release**:

1. valida a versão declarada em `VERSION`;
2. espelha somente imagens-base ausentes;
3. compila `pdf2ofx-app`, `pdf2ofx-gateway` e `pdf2ofx-converter`;
4. publica as tags `X.Y.Z`, `X.Y`, `sha-*` e `latest`;
5. cria a tag `vX.Y.Z`;
6. publica a GitHub Release;
7. anexa o código-fonte, os pacotes Docker e Dockge, a relação de imagens e os checksums.

A release só é criada quando as três imagens forem publicadas com sucesso.

## Atualização e rollback

```bash
cd /opt/pdf2ofx/deploy/docker
bash update.sh 1.1.7
bash rollback.sh 1.1.7
```

## Backup e restauração

```bash
bash backup.sh
RESTORE_CONFIRM=YES bash restore.sh backups/ARQUIVO.sql.gz
```

## Diagnóstico

```bash
bash status.sh
bash healthcheck.sh
bash logs.sh
bash logs.sh converter-worker
```
