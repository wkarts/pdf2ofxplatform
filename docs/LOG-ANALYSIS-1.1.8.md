# Análise dos logs — versão 1.1.8

## Falha identificada

O job `Workflows e scripts de implantação` falhou no teste do instalador Dockge.
O teste adicionava um binário `docker` simulado ao `PATH`, mas o instalador se
elevava novamente com `sudo -E`. A política `secure_path` do sudo substituiu o
`PATH` recebido e fez o instalador executar o Docker real do runner.

Como consequência, o CI:

- baixou a imagem real do Dockge;
- iniciou um container real durante um teste que deveria ser isolado;
- criou os arquivos temporários como root e com `.env` em modo `0600`;
- falhou ao ler e remover esses arquivos usando o usuário comum do runner.

Trechos determinantes do log:

```text
Container dockge-dockge-1 Started
grep: .../stacks/pdf2ofx-test/.env: Permission denied
rm: cannot remove ... Permission denied
Process completed with exit code 1
```

## Correção

O teste agora executa o instalador com um helper `run_as_root` e injeta o
`PATH` do mock por meio de `env` **depois** da elevação de privilégio. As
asserções sobre arquivos protegidos e a limpeza também usam o mesmo helper.

Dessa forma, o teste continua reproduzindo a instalação como root, mas nenhum
pull, container ou alteração é realizado no daemon Docker real do runner.
