# Análise dos logs — build/release 1.1.4

## Resultado dos jobs

- preparação da release: aprovada;
- imagens-base no GHCR: aprovadas;
- validação de versão e origem: aprovada;
- `pdf2ofx-converter`: compilado e publicado;
- `pdf2ofx-app`: falhou;
- `pdf2ofx-gateway`: falhou;
- GitHub Release: não executada porque depende do sucesso de todas as imagens.

## Causa raiz

Os dois targets web compartilhavam o estágio `php-runtime`. O estágio executava:

```dockerfile
pecl install redis
```

O serviço REST do PECL não forneceu o XML esperado para a versão localizada:

```text
Package "redis" Version "6.3.0" does not have REST xml available
install failed
```

O target `gateway` também construía o estágio `app` por causa de:

```dockerfile
COPY --from=app /var/www/html/public /var/www/html/public
```

Por isso uma imagem NGINX, que não necessita de PHP, repetiu e herdou a mesma
falha de compilação.

## Correção

- PhpRedis passa a ser compilado de uma tag fixa do código-fonte;
- o download possui retry e falha explícita;
- o build confirma que `extension_loaded("redis")` retorna verdadeiro;
- o gateway copia `apps/web/public` diretamente do contexto;
- o CI executa build real e valida o runtime antes do merge;
- a release continua condicionada à publicação das três imagens.
