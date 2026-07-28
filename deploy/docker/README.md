# Implantação Docker pronta para produção

Este diretório é um pacote de implantação independente do código-fonte. Nas GitHub Releases ele também é distribuído como `pdf2ofx-docker-deployment-X.Y.Z.zip`. Ele usa
somente imagens publicadas no **GitHub Container Registry (GHCR)** e não exige
PHP, Composer, Python, Node.js, PostgreSQL ou Redis instalados diretamente na
VPS.

## Arquivos

```text
compose.yaml                         stack completa de produção
docker-compose.yml                  cópia compatível com o nome clássico
.env.example                         modelo de configuração
install.sh                           instalação inicial assistida
deploy.sh                            pull, migração e atualização completa
update.sh X.Y.Z                      atualização para outra versão
rollback.sh X.Y.Z                    retorno a uma versão anterior
backup.sh                            backup PostgreSQL + arquivo .env
restore.sh                           restauração de backup
status.sh                            estado dos containers e imagens
logs.sh [serviço]                    acompanhamento dos logs
healthcheck.sh                       verificação HTTP local
cloudpanel/reverse-proxy.conf.example exemplo de VHost
systemd/pdf2ofx.service              inicialização automática opcional
```

## Requisitos da VPS

- Debian ou Ubuntu em máquina virtual;
- Docker Engine;
- plugin `docker compose`;
- `curl` e `openssl`;
- CloudPanel para domínio, TLS e Reverse Proxy;
- no mínimo 4 GB de RAM; 8 GB é recomendado quando o OCR processar documentos
  grandes ou mais de uma conversão simultânea.

## 1. Instalar Docker no servidor

Em uma VPS nova, use o repositório oficial do Docker adequado à distribuição.
Depois confirme:

```bash
docker --version
docker compose version
```

O usuário da implantação deve conseguir executar Docker. Quando não estiver no
grupo `docker`, execute os comandos com uma conta administrativa ou configure o
grupo antes da implantação.

## 2. Copiar o projeto para a VPS

Modelo usando o repositório:

```bash
sudo mkdir -p /opt/pdf2ofx
sudo chown "$USER":"$USER" /opt/pdf2ofx
git clone https://github.com/wkarts/pdf2ofxplatform.git /opt/pdf2ofx
cd /opt/pdf2ofx/deploy/docker
```

Também é possível extrair o ZIP da GitHub Release em `/opt/pdf2ofx` e entrar no
mesmo diretório.

## 3. Autenticar no GHCR

Quando os pacotes forem públicos, o login pode não ser necessário. Para pacotes
privados, crie um token com `read:packages` e execute:

```bash
export GHCR_USER=wkarts
export GHCR_TOKEN='SEU_TOKEN'
printf '%s' "$GHCR_TOKEN" | docker login ghcr.io \
  -u "$GHCR_USER" --password-stdin
```

O token não é gravado no arquivo `.env`.

## 4. Instalação inicial

```bash
cd /opt/pdf2ofx/deploy/docker
bash install.sh \
  --domain https://pdf2ofx.codisplan.com.br \
  --version 1.1.7 \
  --namespace wkarts \
  --port 8080
```

O instalador:

1. cria `.env` com permissão `0600`;
2. gera senhas aleatórias para PostgreSQL e Redis;
3. gera a chave interna entre Laravel e FastAPI;
4. baixa a imagem Laravel;
5. gera `APP_KEY` dentro do container;
6. valida o Compose;
7. baixa todas as imagens;
8. inicia PostgreSQL, Redis e FastAPI;
9. executa as migrations Laravel;
10. inicia gateway, filas, scheduler, OCR e limpeza;
11. executa o health check.

## 5. Configurar o CloudPanel

No CloudPanel:

1. acesse **Sites**;
2. selecione **Add Site**;
3. escolha **Create a Reverse Proxy**;
4. informe o domínio;
5. use como destino:

```text
http://127.0.0.1:8080
```

6. gere o certificado Let's Encrypt;
7. force o redirecionamento HTTP para HTTPS;
8. ajuste o limite de upload para pelo menos `50M`.

O gateway Docker fica vinculado exclusivamente ao loopback:

```text
127.0.0.1:8080
```

PostgreSQL, Redis e FastAPI não publicam portas na internet.

Um modelo adicional está em:

```text
cloudpanel/reverse-proxy.conf.example
```

## 6. Conferir o ambiente

```bash
bash status.sh
bash healthcheck.sh
bash logs.sh
```

Logs de um serviço específico:

```bash
bash logs.sh app
bash logs.sh converter-worker
bash logs.sh gateway
```

## Atualização

Depois que a versão estiver publicada no GHCR:

```bash
cd /opt/pdf2ofx/deploy/docker
bash update.sh 1.1.7
```

O script preserva uma cópia do `.env`, altera as três imagens, baixa os novos
artefatos, executa migrations, recria os containers e valida a aplicação.

## Rollback

```bash
bash rollback.sh 1.1.7
```

O rollback troca as imagens da aplicação. Migrações destrutivas de banco devem
ser evitadas; quando uma versão incluir alterações incompatíveis, restaure o
backup correspondente.

## Backup

```bash
bash backup.sh
```

Arquivos criados em `deploy/docker/backups`:

```text
pdf2ofx_AAAAMMDD_HHMMSS.sql.gz
pdf2ofx_AAAAMMDD_HHMMSS.env
pdf2ofx_AAAAMMDD_HHMMSS.sha256
```

O `.env` contém segredos e deve permanecer protegido.

## Restauração

```bash
RESTORE_CONFIRM=YES bash restore.sh \
  backups/pdf2ofx_AAAAMMDD_HHMMSS.sql.gz
```

Antes da restauração, confira o checksum e mantenha uma cópia do estado atual.

## Inicialização automática pelo systemd

A política `restart: unless-stopped` já reinicia containers após a subida do
Docker. Para controlar a stack também como unidade systemd:

```bash
sudo cp systemd/pdf2ofx.service /etc/systemd/system/pdf2ofx.service
sudo systemctl daemon-reload
sudo systemctl enable --now pdf2ofx.service
sudo systemctl status pdf2ofx.service
```

O arquivo pressupõe a instalação em:

```text
/opt/pdf2ofx/deploy/docker
```

## Serviços da stack

```text
gateway             NGINX interno publicado em 127.0.0.1:8080
app                 Laravel/PHP-FPM
queue               Laravel Queue Worker
scheduler           Laravel Scheduler
converter-api       FastAPI
converter-worker    Celery + PDF/OCR
converter-cleaner   limpeza de arquivos temporários
redis               filas, cache e sessão
postgres            banco de dados
```

## Volumes persistentes

```text
web_storage       storage do Laravel
converter_jobs    arquivos temporários controlados pelo TTL
redis_data        AOF do Redis
postgres_data     dados PostgreSQL
```

Para listar os volumes:

```bash
docker volume ls --filter label=com.docker.compose.project=pdf2ofx
```

## Comandos manuais úteis

```bash
# Validar a configuração
docker compose --env-file .env -f compose.yaml config

# Atualizar todos os containers
bash deploy.sh

# Executar migrations
docker compose --env-file .env -f compose.yaml \
  exec -T app php artisan migrate --force

# Limpar e recriar caches Laravel
docker compose --env-file .env -f compose.yaml \
  exec -T app php artisan optimize:clear

docker compose --env-file .env -f compose.yaml \
  exec -T app php artisan optimize

# Parar sem remover volumes
docker compose --env-file .env -f compose.yaml down

# Remover também os dados — operação destrutiva
docker compose --env-file .env -f compose.yaml down --volumes
```
