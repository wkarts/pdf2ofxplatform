# Changelog

## [1.1.2] - 2026-07-28

### Corrigido

- build e release agora são iniciados automaticamente após o workflow `CI`
  concluir com sucesso em `main`;
- o workflow de release passou a criar a tag Git, GitHub Release, ZIP, TAR.GZ,
  lista de imagens e checksums SHA-256;
- o workflow de imagens passou a aceitar execução reutilizável e manual com
  versão e commit explicitamente validados;
- o espelhamento das imagens-base no GHCR tornou-se pré-requisito automático da
  release e preserva manifestos multi-arquitetura;
- removida a dependência de criação manual da tag para iniciar a publicação;
- adicionada prevenção contra republicação acidental da mesma versão;
- adicionada validação de consistência entre `VERSION`, pacote Python,
  documentação e imagens;
- corrigida a URL de clone para `wkarts/pdf2ofxplatform.git`;
- os pacotes da release também são preservados como artifact do workflow;
- o deploy valida previamente a existência da release e das três imagens no
  GHCR.

### Publicação

- imagens `pdf2ofx-app`, `pdf2ofx-gateway` e `pdf2ofx-converter` publicadas no
  GHCR com tags `X.Y.Z`, `X.Y`, `sha-*` e `latest`;
- release vinculada exatamente ao commit aprovado pelo CI.

## [1.1.1] - 2026-07-28

### Corrigido

- Ordenação dos imports padrão em `parsers/helpers.py`, eliminando a falha `Ruff I001` no job `converter` do GitHub Actions.
- Metadados, exemplos de imagens GHCR e documentação de implantação atualizados para a versão 1.1.1.

### Validado

- `ruff check src tests`;
- compilação dos módulos Python;
- suíte de testes do conversor;
- sintaxe dos arquivos PHP, JSON, YAML e Shell;
- integridade do pacote de distribuição.

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
