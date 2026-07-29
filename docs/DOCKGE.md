# Dockge

A implantação recomendada pressupõe que o Dockge já está instalado e configurado para ler `/opt/stacks`.

Use o pacote `pdf2ofx-stack-deployment-1.2.0` ou o diretório `deploy/stack`.

```text
Internet
   │
CloudPanel / NGINX / TLS
   └── pdf2ofx.seudominio.com.br -> 127.0.0.1:8080

Dockge
   └── /opt/stacks/pdf2ofx/compose.yaml
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

O pacote não instala Docker, Dockge ou CloudPanel. Consulte `deploy/stack/README.md`.
