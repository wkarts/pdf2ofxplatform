# Validação da versão 1.1.2

## Problema corrigido

Os workflows de build de imagens e GitHub Release eram disparados apenas por
`push` de tags no padrão `v*.*.*`. O merge do Pull Request executava o CI, mas
não criava uma tag. Portanto, CI aprovado não resultava em imagens no GHCR nem
em GitHub Release.

## Comportamento implementado

- o workflow de release aguarda a conclusão do workflow `CI`;
- somente execuções aprovadas de `push` em `main` podem iniciar uma release
  automática;
- a versão é obtida do arquivo `VERSION` e validada;
- releases já existentes são ignoradas, salvo execução manual com `force`;
- imagens-base são espelhadas no GHCR antes do build;
- as três imagens da aplicação são compiladas e publicadas;
- a tag e a GitHub Release são criadas somente após todos os builds passarem;
- ZIP, TAR.GZ, lista de imagens e checksums são anexados à release e ao workflow;
- tags existentes não podem ser movidas para outro commit;
- o CI valida a consistência dos metadados de versão.

## Validações locais

- sintaxe YAML carregada e validada;
- referências de versão atualizadas para `1.1.2`;
- scripts Shell embutidos revisados com `set -Eeuo pipefail`;
- Docker Compose validado com o arquivo `.env.example`;
- módulos Python compilados;
- testes Python executados;
- sintaxe PHP validada.
