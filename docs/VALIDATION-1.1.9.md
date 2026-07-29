# Validação da versão 1.2.0

## Escopo

Correção da preparação do ambiente Laravel no GitHub Actions e inclusão do
arquivo de ambiente que faltava dentro de `apps/web`.

## Validações executadas

- análise integral dos oito logs resumidos e dos logs detalhados por etapa;
- confirmação de que a única etapa com `exit code 1` era o preparo Laravel;
- validação de sintaxe PHP da aplicação;
- compilação dos módulos Python;
- execução da suíte Python;
- validação YAML dos workflows;
- validação de sintaxe de todos os scripts Shell;
- testes do espelhamento GHCR e do instalador Dockge com Docker simulado;
- validação de consistência da versão;
- validação de presença e conteúdo de `apps/web/.env.example`;
- geração e verificação dos pacotes ZIP, TAR.GZ e checksums.

## Limitação do ambiente local

O Composer não estava disponível no ambiente de empacotamento. Nos logs, o job
Laravel falhou antes do `composer validate` e do `composer install`; as mesmas
dependências e testes já haviam sido aprovados em execuções anteriores. O novo
CI continuará executando Composer e a suíte Laravel integralmente.
