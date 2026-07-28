# API interna do conversor

A API FastAPI é acessível somente pela rede interna do Compose. Todas as rotas
`/v1` exigem:

```text
X-Internal-API-Key: <PDF2OFX_API_KEY>
```

## Listar bancos

`GET /v1/banks`

Retorna as chaves, nomes e códigos dos bancos cadastrados e informa o fallback
`generic`.

## Criar conversão

`POST /v1/conversions`, `multipart/form-data`:

- `file`: PDF;
- `bank_hint`: `auto`, uma chave retornada por `/v1/banks` ou `generic`;
- `output_format`: `ofx_102`.

Aliases aceitos incluem `nubanck`, `mercadopago`, `banco_brasil`, `cef` e
`nordeste`. Retorna HTTP 202, `job_id`, status e TTL.

## Consultar conversão

`GET /v1/conversions/{job_id}`

Estados possíveis:

- `queued`;
- `processing`;
- `completed`;
- `review_required`;
- `failed`.

`review_required` significa que o OFX foi gerado, mas existem divergências,
duplicidades, parser universal ou lançamentos de baixa confiança. O arquivo
permanece disponível para revisão e download.

## Corrigir transação

`PATCH /v1/conversions/{job_id}/transactions/{index}`

Campos opcionais:

- `posted_at` (`YYYY-MM-DD`);
- `description`;
- `document_number`;
- `amount`;
- `deleted`.

Após cada alteração, o extrato é reconciliado e o OFX é regenerado.

## Download

`GET /v1/conversions/{job_id}/download`

Permitido para `completed` e `review_required`, enquanto o job não tiver
expirado.

## Saúde

`GET /health`
