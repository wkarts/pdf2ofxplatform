# PDF2OFX Platform

Aplicação web completa para converter extratos bancários em PDF para OFX 1.02
(SGML/Windows-1252), com processamento assíncrono, OCR, revisão de transações,
conciliação e parsers bancários extensíveis.

## Stack

- Laravel 12 / PHP 8.4;
- Blade + JavaScript, sem dependência de build frontend;
- Python 3.13, FastAPI e Celery;
- Redis 8 e PostgreSQL 17;
- pdfplumber, pypdf, Tesseract OCR e OpenCV headless;
- Docker Compose;
- GitHub Container Registry (GHCR);
- CloudPanel como Reverse Proxy e terminador TLS.

## Cobertura bancária

A plataforma possui três níveis de processamento:

- **parsers calibrados:** Itaú (341), Banco do Nordeste (004) e Santander
  (033), validados com os PDFs reais fornecidos;
- **perfis bancários dedicados:** Banco do Brasil, Inter, Caixa, Bradesco,
  Next, Nubank, Mercado Pago, Sicoob, Sicredi, C6, PagBank, Stone, Safra,
  Banrisul, BTG, Original, BV, PicPay, XP, PAN, BS2, Banco da Amazônia,
  BRB, Banpará, Banestes, BMG, Daycoval, Mercantil, Unicred e Cresol;
- **parser bancário universal:** fallback para outros bancos e novos layouts,
  sempre sinalizando revisão quando não houver conciliação completa.

O catálogo é extensível e não vincula a API a um layout específico. Mudanças no
PDF de uma instituição podem ser tratadas por um parser calibrado sem alterar o
Laravel, o contrato HTTP ou o gerador OFX.

O Itaú e qualquer documento processado por OCR podem exigir revisão manual
quando a qualidade da imagem não permitir reconciliação automática. A interface
destaca lançamentos de baixa confiança e mantém o OFX editável antes do download.

## Funcionalidades

- upload por seleção ou arrastar e soltar;
- detecção automática do banco;
- OCR automático somente quando necessário;
- fila assíncrona e acompanhamento de progresso;
- edição, exclusão e restauração de transações;
- conciliação de saldo inicial, movimentos e saldo final;
- detecção de possíveis duplicidades;
- exportação OFX 1.02 em Windows-1252;
- isolamento das conversões por sessão anônima;
- expiração e limpeza automática dos artefatos temporários;
- API interna protegida por chave;
- Docker, CloudPanel, CI, release e deploy pelo GitHub.

## Estrutura

```text
apps/web                 Laravel, interface e metadados
services/converter       FastAPI, Celery, PDF/OCR, parsers e OFX
deploy                   scripts, systemd e configuração CloudPanel
docs                     arquitetura, API, parsers e implantação
.github/workflows        CI, imagens GHCR, release e deploy
compose.yaml              ambiente completo
compose.production.yaml   sobreposição para imagens publicadas
```

## Build e release automáticos

Depois que um push em `main` conclui o workflow **CI** com sucesso, o workflow
**Build, publish and release** executa automaticamente o fluxo completo:

1. lê e valida a versão do arquivo `VERSION`;
2. verifica se a release correspondente já existe;
3. confirma as imagens-base no GHCR e espelha apenas as ausentes, de forma sequencial;
4. compila e publica `pdf2ofx-app`, `pdf2ofx-gateway` e
   `pdf2ofx-converter`;
5. cria a tag `vX.Y.Z` e a GitHub Release;
6. anexa ZIP, TAR.GZ, lista de imagens e checksums SHA-256 à release e ao workflow.

Para gerar uma nova release, atualize o arquivo `VERSION` e os metadados do
projeto antes do merge. O workflow também pode ser executado manualmente, com a
opção de recompilar uma versão já existente.

Nenhuma imagem produzida pelo projeto é publicada no Docker Hub. As imagens da
aplicação e os espelhos de runtime ficam no GHCR do próprio repositório/owner.

## Inicialização local

```bash
cp .env.example .env
# Edite as senhas, chaves e o namespace GHCR.
docker login ghcr.io
make init
```

A aplicação ficará disponível em:

```text
http://127.0.0.1:8080
```

## Produção com CloudPanel

No CloudPanel, crie um site **Reverse Proxy** apontando para:

```text
http://127.0.0.1:8080
```

Depois:

```bash
cp .env.production.example .env
# Preencha domínio, APP_KEY, senhas, chave interna e imagens GHCR.
./deploy/scripts/deploy.sh
```

Somente a porta do gateway é vinculada ao loopback da VPS. Redis, PostgreSQL e
FastAPI permanecem na rede interna do Docker.

## Testes

```bash
make test
make lint
```

Validações disponíveis:

- testes PHP/Laravel;
- testes unitários dos parsers Python;
- geração e codificação OFX;
- reconciliação;
- sintaxe PHP, Python, JavaScript, YAML e Shell;
- validação do Docker Compose no workflow de CI.

## Segurança e privacidade

- o PDF é removido pelo worker após sucesso ou falha;
- JSON intermediário e OFX expiram conforme o TTL;
- metadados do Laravel não armazenam o conteúdo bancário;
- histórico anônimo é visível apenas para a mesma sessão;
- serviços internos não possuem portas públicas;
- logs não devem registrar valores, descrições ou documentos bancários;
- `.env`, extratos reais, OFX reais e backups não devem entrar no Git.

## Documentação

- `docs/ARCHITECTURE.md`;
- `docs/API.md`;
- `docs/PARSERS.md`;
- `docs/DEPLOYMENT.md`;
- `docs/VALIDATION.md`;
- `deploy/cloudpanel/README.md`.

## Versão

`1.1.3`

## Licença

Projeto proprietário. Consulte `LICENSE`.
