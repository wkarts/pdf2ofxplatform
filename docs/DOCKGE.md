# Dockge

A implantação oficial para VPS pode ser gerenciada pelo Dockge. Os arquivos
estão em `deploy/dockge` e não dependem do código-fonte durante a execução: a
stack utiliza somente as imagens versionadas no GHCR.

## Topologia

```text
Internet
   │
CloudPanel / NGINX / TLS
   ├── domínio da aplicação -> 127.0.0.1:8080
   └── domínio administrativo opcional -> 127.0.0.1:5001

Docker
   ├── Dockge
   └── stack pdf2ofx
       ├── gateway
       ├── app
       ├── queue
       ├── scheduler
       ├── converter-api
       ├── converter-worker
       ├── converter-cleaner
       ├── redis
       └── postgres
```

O diretório de stacks segue o padrão `/opt/stacks`, com a aplicação em
`/opt/stacks/pdf2ofx/compose.yaml`.

Consulte `deploy/dockge/README.md` para instalação, atualização, backup,
CloudPanel e operação diária.
