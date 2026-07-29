# Changelog

## [1.2.0] - 2026-07-28

### Alterado

- removidas referências de domínio específico e adotado `seudominio`;
- adicionada distribuição `pdf2ofx-stack-deployment-1.2.0` para VPS com Docker, Dockge e CloudPanel já instalados;
- implantação reduzida ao fluxo de parametrizar, baixar imagens, subir a stack e configurar o Reverse Proxy;
- scripts de preflight, configuração, deploy, atualização, rollback, backup, restauração, logs, status e health check;
- release e CI atualizados para validar e publicar o novo pacote.

## [1.1.8] - 2026-07-28

### Corrigido

- teste do instalador Dockge passa a preservar explicitamente o Docker simulado após `sudo`;
- removida a possibilidade de o CI baixar e iniciar o Dockge real durante a validação;
- validações de arquivos protegidos são executadas com o mesmo contexto root da instalação;
- limpeza do diretório temporário passou a funcionar mesmo quando os arquivos são criados como root;
- ambiente Laravel de testes passa a criar `.env` antes do Composer, eliminando avisos de arquivo ausente.

### Validado

- instalação Dockge simulada sem acesso ao daemon Docker real;
- permissões `0600` dos arquivos `.env`;
- comandos Compose esperados registrados exclusivamente pelo mock;
- scripts Shell, metadados, parsers e pacotes de implantação.

## [1.1.7] - 2026-07-28

### Adicionado

- implantação completa com Dockge em `deploy/dockge/`;
- instalador idempotente para Debian/Ubuntu, com instalação opcional do Docker;
- criação automática de `/opt/dockge` e `/opt/stacks/pdf2ofx`;
- geração segura de `APP_KEY`, senhas PostgreSQL/Redis e chave interna da API;
- autenticação opcional no GHCR sem persistir o token no `.env` da aplicação;
- scripts para atualização, migrations, backup, status, logs e health check;
- modelos de Reverse Proxy do CloudPanel para a aplicação e para o Dockge;
- pacote de release independente `pdf2ofx-dockge-deployment-X.Y.Z`.

### Validado

- sintaxe dos scripts Shell do Dockge;
- configuração Compose do Dockge e da stack PDF2OFX;
- consistência das imagens e metadados da versão;
- geração dos pacotes ZIP e TAR.GZ do Dockge no workflow de release.

## [1.1.6] - 2026-07-28

### Corrigido

- validação isolada da imagem `pdf2ofx-gateway`, que falhava porque o NGINX tentava resolver o upstream `app:9000` fora da rede do Docker Compose;
- teste do gateway agora registra explicitamente o hostname `app`, valida `nginx -t`, inicia o container e confirma o endpoint `/health`;
- validação de versão reforçada para exigir o script reutilizável `validate-gateway-image.sh` e sua utilização pelo CI.

### Validado

- logs do GitHub Actions confirmam que os builds `app` e `converter` foram aprovados e que a única falha ocorreu na validação isolada do gateway;
- sintaxe dos workflows e scripts Shell;
- metadados da versão;
- pacote independente de implantação Docker;
- testes Python e sintaxe PHP.

## [1.1.5] - 2026-07-28

### Corrigido

- removida a dependência do endpoint REST do PECL durante o build da extensão Redis;
- extensão PhpRedis compilada a partir de uma versão fixa do código-fonte, com retry no download;
- gateway NGINX desacoplado do estágio PHP, evitando recompilação desnecessária do Laravel;
- CI alterado de verificação estática para build real das três imagens;
- validação do runtime confirma Redis, Artisan, NGINX e pacote Python;
- release permanece bloqueada quando qualquer imagem não é publicada.

### Implantação

- adicionado pacote independente em `deploy/docker/`;
- incluídos Compose de produção, modelo `.env`, instalador, update, rollback, backup, restore, status, logs e health check;
- incluídos modelos para CloudPanel Reverse Proxy e systemd;
- documentação de implantação reestruturada com procedimento completo.

## [1.1.4] - 2026-07-28

### Corrigido

- falha `Permission denied`/exit code `126` no teste de espelhamento;
- scripts de implantação deixam de depender do bit executável Unix;
- chamadas internas e exemplos passam a executar scripts explicitamente com `bash`;
- workflow de imagens-base recebe e usa o commit exato aprovado pelo CI;
- release automática volta a prosseguir após o merge validado em `main`.

### Validado

- teste de espelhamento com o script alvo propositalmente sem permissão de execução;
- sintaxe Shell e YAML;
- metadados da versão;
- testes Laravel e Python;
- Docker Compose e Dockerfiles.

## [1.1.3] - 2026-07-28

### Corrigido

- eliminado o espelhamento simultâneo de manifestos multi-arquitetura, que
  excedia o limite de requisições do GHCR e retornava `429 Too Many Requests`;
- imagens-base agora são espelhadas somente para `linux/amd64`, arquitetura
  efetivamente utilizada pelo build e pela VPS;
- espelhamento passou a ser sequencial, idempotente e protegido por até seis
  tentativas com espera exponencial;
- imagens-base já existentes no GHCR são detectadas e não são republicadas;
- publicação das imagens da aplicação passou a usar `max-parallel: 1`, reduzindo
  rajadas de upload no registro;
- o build valida explicitamente a presença de todas as imagens-base antes de
  compilar as imagens da aplicação;
- a preparação da release executa novamente a validação completa dos metadados;
- GitHub Actions atualizadas para runtimes Node.js 24, removendo os avisos de
  actions baseadas em Node.js 20.

### Validações adicionadas

- validação YAML de todos os workflows;
- validação sintática de todos os scripts Shell de implantação;
- bloqueio de versões obsoletas das actions utilizadas no projeto;
- bloqueio do comando de espelhamento multi-arquitetura que causou a falha;
- verificação estática dos três targets Docker antes da publicação;
- validação final do catálogo completo de imagens-base no GHCR.

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
