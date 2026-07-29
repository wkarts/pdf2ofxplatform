# Implantação do PDF2OFX com Dockge

Este pacote instala o Dockge e registra o PDF2OFX como uma stack Docker Compose
armazenada em `/opt/stacks/pdf2ofx`. O Dockge permanece em `/opt/dockge` e as
portas da interface administrativa e da aplicação são vinculadas somente ao
loopback da VPS.

## Estrutura criada na VPS

```text
/opt/dockge/
├── compose.yaml
├── .env
└── data/

/opt/stacks/pdf2ofx/
├── compose.yaml
├── .env
├── backups/
└── scripts/
    ├── backup.sh
    ├── healthcheck.sh
    ├── logs.sh
    ├── post-deploy.sh
    ├── status.sh
    └── update-version.sh
```

## Instalação completa

Extraia o pacote do projeto ou o pacote `pdf2ofx-dockge-deployment-X.Y.Z` na
VPS e execute:

```bash
cd deploy/dockge
sudo -E bash install-vps.sh \
  --domain https://pdf2ofx.seudominio.com.br \
  --version 1.2.0 \
  --namespace wkarts
```

Quando as imagens GHCR forem privadas:

```bash
export GHCR_USER=wkarts
export GHCR_TOKEN='TOKEN_COM_READ_PACKAGES'
sudo -E bash install-vps.sh \
  --domain https://pdf2ofx.seudominio.com.br \
  --version 1.2.0 \
  --namespace wkarts
```

O token é utilizado pelo `docker login` e não é gravado no `.env` da
aplicação. O diretório `/root/.docker` é montado como somente leitura no
Dockge, permitindo que a interface faça pull das imagens privadas.

O instalador é idempotente: preserva o `.env` existente. Para gerar novas
credenciais e recriar o arquivo:

```bash
sudo -E bash install-vps.sh --force-env
```

## CloudPanel

Crie dois sites do tipo **Reverse Proxy**.

Aplicação:

```text
Domínio: pdf2ofx.seudominio.com.br
Destino: http://127.0.0.1:8080
```

Dockge, opcional:

```text
Domínio: dockge.seudominio.com.br
Destino: http://127.0.0.1:5001
```

A interface Dockge é administrativa. Restrinja o subdomínio por firewall,
VPN, IP permitido ou autenticação adicional. Também é possível não criar o
subdomínio e acessar por túnel SSH:

```bash
ssh -L 5001:127.0.0.1:5001 usuario@IP_DA_VPS
```

Modelos de ajustes NGINX estão em `cloudpanel/`.

## Uso no Dockge

A stack fica em `/opt/stacks/pdf2ofx/compose.yaml`. Caso não seja exibida logo
após o primeiro acesso, abra o menu superior direito e execute **Scan Stacks
Folder**. Depois disso, os comandos Compose, logs, pull, restart e edição do
arquivo ficam disponíveis pela interface.

## Atualização de versão

Pelo terminal da VPS ou terminal da stack:

```bash
cd /opt/stacks/pdf2ofx
bash scripts/update-version.sh 1.2.0
```

O script:

1. preserva uma cópia do `.env`;
2. altera as três tags da aplicação;
3. baixa as imagens;
4. recria os containers;
5. executa migrations e caches;
6. valida o endpoint de saúde.

Também é possível editar `PDF2OFX_VERSION`, `APP_IMAGE`, `GATEWAY_IMAGE` e
`CONVERTER_IMAGE` diretamente na aba `.env` do Dockge, pressionar **Pull** e
então **Update**. Depois execute:

```bash
bash /opt/stacks/pdf2ofx/scripts/post-deploy.sh
```

## Backup

```bash
cd /opt/stacks/pdf2ofx
bash scripts/backup.sh
```

Os arquivos são criados em `/opt/stacks/pdf2ofx/backups`. O backup inclui o
PostgreSQL e uma cópia protegida do `.env`.

## Logs e diagnóstico

```bash
cd /opt/stacks/pdf2ofx
bash scripts/status.sh
bash scripts/healthcheck.sh
bash scripts/logs.sh
bash scripts/logs.sh converter-worker
```

## Portas e serviços

Somente estas portas são vinculadas ao host:

```text
127.0.0.1:5001 -> Dockge
127.0.0.1:8080 -> gateway NGINX do PDF2OFX
```

PostgreSQL, Redis, FastAPI e PHP-FPM permanecem apenas na rede interna da
stack. Os dados são persistidos em volumes Docker nomeados.
