# Changelog

## [1.1.0] - 2026-07-28

### Corrigido

- dependências incompatíveis do Laravel no workflow de CI;
- Laravel ajustado para a linha 12, Collision 8 e PHPUnit 11;
- imports e tratamento de exceção apontados pelo Ruff;
- actions atualizadas para runtimes sem o aviso do Node.js 20;
- validação dinâmica de `bank_hint` na API e no Laravel.
- detecção automática para evitar classificar layouts desconhecidos como outro banco.

### Adicionado

- catálogo centralizado de instituições e aliases;
- suporte dedicado solicitado para Banco do Brasil, Santander, Inter, Caixa,
  Bradesco, Banco do Nordeste, Itaú, Next, Nubank e Mercado Pago;
- perfis adicionais para Sicoob, Sicredi, C6, PagBank, Stone, Safra, Banrisul,
  BTG, Original, BV, PicPay, XP, PAN, BS2, Banco da Amazônia, BRB, Banpará,
  Banestes, BMG, Daycoval, Mercantil, Unicred e Cresol;
- parser bancário universal com inferência por sinais, texto, colunas e saldos;
- rota `GET /v1/banks`;
- seletor bancário completo na interface;
- testes de catálogo, aliases, perfis e fallback universal.

## [1.0.0] - 2026-07-28

- Aplicação web Laravel, API FastAPI e workers Celery.
- Parsers iniciais de Itaú, Banco do Nordeste e Santander.
- OCR Tesseract, conciliação e geração OFX 1.02.
- Docker Compose, GHCR, CloudPanel e workflows GitHub Actions.
