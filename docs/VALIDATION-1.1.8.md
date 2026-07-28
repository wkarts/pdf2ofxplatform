# Validação da versão 1.1.8

## Escopo

Correção do teste automatizado da implantação Dockge e eliminação dos avisos de
`.env` ausente na suíte Laravel.

## Validações obrigatórias

- `bash -n` em todos os scripts Shell;
- `deploy/dockge/tests/test-install-vps.sh` com Docker simulado;
- execução do instalador em contexto root sem perder o `PATH` do mock;
- confirmação de que o mock recebeu `docker compose version`, `config`, `pull`
  e `up -d`;
- confirmação de permissão `0600` no `.env` da stack;
- limpeza do diretório temporário com arquivos criados como root;
- consistência de `VERSION`, pacote Python, imagens GHCR e documentação;
- testes Laravel com `.env` de teste preparado pelo CI;
- testes Python, Ruff, compilação dos módulos e parsers;
- validação dos arquivos Compose e builds reais das três imagens.

## Critério de conclusão

A validação é aprovada somente quando o teste Dockge termina sem acessar o
Docker real do runner e todos os demais jobs do CI permanecem aprovados.
