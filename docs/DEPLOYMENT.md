# Implantação

## Pré-requisitos

- VPS Linux em máquina virtual;
- CloudPanel instalado;
- Docker Engine e plugin Docker Compose;
- acesso ao GHCR;
- domínio configurado;
- Git e `curl`.

## Preparar o GHCR

Execute no GitHub, nesta ordem:

1. **Mirror base images to GHCR**;
2. crie a tag `v1.1.0` ou execute **Build and publish images**;
3. confirme a existência das imagens:
   - `pdf2ofx-app`;
   - `pdf2ofx-gateway`;
   - `pdf2ofx-converter`;
   - espelhos `pdf2ofx-base-*`.

Para pacotes privados, gere um token com `read:packages` e autentique a VPS:

```bash
echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin
```

## Instalação na VPS

```bash
sudo mkdir -p /opt/pdf2ofx
sudo chown "$USER":"$USER" /opt/pdf2ofx
git clone git@github.com:wkarts/pdf2ofx-platform.git /opt/pdf2ofx
cd /opt/pdf2ofx
cp .env.production.example .env
chmod +x deploy/scripts/*.sh
```

Preencha no `.env`:

- `APP_URL`;
- `APP_KEY`;
- senhas PostgreSQL e Redis;
- `CONVERTER_API_KEY` e `PDF2OFX_API_KEY` com o mesmo valor;
- `GHCR_NAMESPACE`;
- tags das imagens;
- caminhos das imagens-base espelhadas.

Gere uma chave Laravel sem instalar Composer no host:

```bash
docker run --rm \
  ghcr.io/wkarts/pdf2ofx-app:1.1.0 \
  php artisan key:generate --show
```

Cole o resultado em `APP_KEY` e execute:

```bash
./deploy/scripts/deploy.sh
```

## CloudPanel

Crie um **Reverse Proxy** para:

```text
http://127.0.0.1:8080
```

Ative o certificado SSL e aplique os ajustes descritos em
`deploy/cloudpanel/README.md`.

## GitHub Actions de deploy

Configure o environment `production` e os secrets:

- `PRODUCTION_HOST`;
- `PRODUCTION_USER`;
- `PRODUCTION_SSH_KEY`;
- `PRODUCTION_SSH_PORT`;
- `GHCR_USER`;
- `GHCR_TOKEN`.

O workflow recebe uma versão `X.Y.Z`, faz checkout da tag, altera as imagens no
`.env` e executa o script de deploy.

## Backup

```bash
./deploy/scripts/backup.sh
```

Agende no cron. O script guarda somente o PostgreSQL. O PDF original é removido
pelo worker e os artefatos temporários expiram pelo TTL.

## Rollback

```bash
./deploy/scripts/rollback.sh 1.1.0
```
