# Apontamento no CloudPanel

A infraestrutura já deve possuir CloudPanel, Docker, Docker Compose V2 e Dockge.
Este pacote não instala nem altera esses componentes.

No CloudPanel:

1. abra **Sites**;
2. selecione **Add Site**;
3. escolha **Create a Reverse Proxy**;
4. informe o domínio `pdf2ofx.seudominio.com.br`;
5. use como destino `http://127.0.0.1:8080`;
6. crie/ative o certificado SSL;
7. habilite o redirecionamento de HTTP para HTTPS.

No editor do VHost, preserve o conteúdo gerado pelo CloudPanel e acrescente, dentro do bloco de proxy, as diretivas de `reverse-proxy.conf.example`.

Não publique as portas de PostgreSQL, Redis, FastAPI ou PHP-FPM. Apenas o gateway fica disponível em `127.0.0.1:8080`.
