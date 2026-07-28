# Pull Request 1.1.8

## Branch

`fix/dockge-mock-sudo-validation-v1.1.8`

## Título

`fix(ci): isolar o teste Dockge e corrigir permissões após sudo`

## Descrição

### Objetivo

Corrigir a falha do job `Workflows e scripts de implantação` sem remover ou
reduzir as validações da implantação Dockge.

### Diagnóstico

O teste preparava um executável `docker` simulado no `PATH`. Ao detectar um
usuário não root, o instalador executava novamente por `sudo -E`. O
`secure_path` do sudo descartava o diretório do mock, fazendo o teste usar o
Docker real do GitHub Runner.

Isso iniciou o Dockge real e criou arquivos root com permissão `0600`, causando
`Permission denied` nas asserções e na limpeza do diretório temporário.

### Alterações

- criado helper `run_as_root` no teste;
- `PATH` do Docker simulado aplicado depois da elevação por `sudo`;
- asserções sobre `.env` executadas como root;
- limpeza temporária executada com o mesmo contexto;
- adicionada prova de que o log do Docker simulado foi utilizado;
- CI Laravel prepara `.env` antes do Composer;
- validação de metadados reforçada contra regressão;
- versão atualizada para `1.1.8`.

### Resultado esperado

1. o teste do Dockge não baixa nem inicia containers reais;
2. o instalador continua sendo validado em contexto root;
3. permissões `0600` são verificadas corretamente;
4. todos os jobs do CI são aprovados;
5. depois do merge em `main`, o fluxo publica as imagens `1.1.8` e a GitHub
   Release correspondente.

### Validação

- [x] erro reproduzido pelos logs;
- [x] Docker simulado preservado após `sudo`;
- [x] arquivos root verificados e removidos sem falha;
- [x] scripts Shell validados;
- [x] metadados de versão validados;
- [x] documentação atualizada;
- [x] nenhum dado bancário real incluído.
