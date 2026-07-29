# Implantação em infraestrutura existente

A distribuição recomendada é `pdf2ofx-stack-deployment-1.2.0`. Ela foi criada para ambientes onde Docker, Docker Compose V2, Dockge e CloudPanel já estão instalados.

Nenhum instalador de infraestrutura é executado. O pacote apenas:

1. adiciona a pasta `/opt/stacks/pdf2ofx`;
2. gera o `.env`;
3. baixa as imagens do GHCR;
4. sobe os serviços;
5. executa migrations e health check;
6. fornece os parâmetros para o Reverse Proxy do CloudPanel.

Consulte `deploy/stack/README.md`.
