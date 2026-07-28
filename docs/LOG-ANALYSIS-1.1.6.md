# Análise dos logs — versão 1.1.7

## Resultado dos jobs

- Metadados da release: aprovado;
- Laravel: aprovado, 19 asserções;
- Conversor Python: aprovado, 15 testes;
- Docker Compose: aprovado;
- Workflows e scripts de implantação: aprovado;
- Build real `app`: aprovado e runtime Laravel/Redis validado;
- Build real `runtime`: aprovado e pacote Python 1.1.5 validado;
- Build real `gateway`: imagem compilada, mas validação isolada reprovada.

## Erro determinante

```text
host not found in upstream "app:9000" in /etc/nginx/conf.d/default.conf:2
nginx: configuration file /etc/nginx/nginx.conf test failed
Process completed with exit code 1
```

## Causa

A configuração NGINX está preparada para o serviço `app` do Docker Compose.
No job de CI, `nginx -t` era executado em um container isolado, sem o DNS da
rede Compose e sem entrada de host para `app`.

Não houve falha no build da imagem. O problema era exclusivamente a forma de
validar a imagem fora da topologia de produção.

## Correção

A validação agora fornece a resolução temporária `app -> 127.0.0.1`, executa
`nginx -t`, inicia o gateway e confirma a resposta do endpoint `/health`.
