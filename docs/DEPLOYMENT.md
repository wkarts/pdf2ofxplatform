# Implantação

## Pré-requisitos

- VPS Linux em máquina virtual;
- CloudPanel instalado;
- Docker Engine e plugin Docker Compose;
- acesso ao GHCR;
- domínio configurado;
- Git e `curl`.

## Build, GHCR e GitHub Release

O merge em `main` dispara o workflow **CI**. Após a conclusão com sucesso, o
workflow **Build, publish and release** é iniciado automaticamente e:

1. valida a versão declarada em `VERSION`;
2. evita republicar uma release já existente;
3. confirma as imagens-base no GHCR e espelha apenas as ausentes, de forma sequencial;
4. compila as imagens `pdf2ofx-app`, `pdf2ofx-gateway` e
   `pdf2ofx-converter`;
5. publica as tags `X.Y.Z`, `X.Y`, `sha-*` e `latest`;
6. cria a tag Git `vX.Y.Z` e a GitHub Release;
7. anexa os pacotes ZIP/TAR.GZ e os checksums SHA-256 à release e ao workflow.

O workflow pode ser disparado manualmente em **Actions → Build, publish and
release**, inclusive com a opção `force` para recompilar uma release existente.

Para pacotes privados, gere um token com `read:packages` e autentique a VPS:

```bash
echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin
```

## Instalação na VPS

```bash
sudo mkdir -p /opt/pdf2ofx
sudo chown "$USER":"$USER" /opt/pdf2ofx
git clone git@github.com:wkarts/pdf2ofxplatform.git /opt/pdf2ofx
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
  ghcr.io/wkarts/pdf2ofx-app:1.1.3 \
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
./deploy/scripts/rollback.sh 1.1.3
```
