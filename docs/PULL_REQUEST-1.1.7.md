# Pull Request 1.1.7

## Branch

```text
feat/dockge-vps-deployment-v1.1.7
```

## Título

```text
feat: adicionar implantação completa do PDF2OFX com Dockge
```

## Descrição

```markdown
## Objetivo

Adicionar uma implantação completa e reproduzível do PDF2OFX em VPS usando
Docker Compose gerenciado pelo Dockge, mantendo CloudPanel como Reverse Proxy e
terminador TLS.

## Alterações

- criado pacote `deploy/dockge/`;
- incluído instalador idempotente para Debian e Ubuntu;
- instalação automática opcional do Docker Engine e Compose V2;
- criação de `/opt/dockge` e `/opt/stacks/pdf2ofx`;
- geração segura de credenciais e `APP_KEY`;
- autenticação opcional no GHCR para imagens privadas;
- execução automática de pull, migrations, cache e health check;
- adicionados scripts de atualização, backup, status e logs;
- adicionados modelos de Reverse Proxy do CloudPanel;
- portas administrativas vinculadas somente ao loopback;
- CI passa a validar os dois Compose do pacote Dockge;
- GitHub Release passa a publicar ZIP e TAR.GZ específicos para Dockge;
- documentação de implantação atualizada;
- versão atualizada para 1.1.7.

## Resultado esperado

1. executar `sudo -E bash deploy/dockge/install-vps.sh`;
2. acessar o Dockge em `127.0.0.1:5001` ou por Reverse Proxy protegido;
3. visualizar e gerenciar a stack `pdf2ofx` em `/opt/stacks/pdf2ofx`;
4. publicar a aplicação pelo CloudPanel em `127.0.0.1:8080`;
5. atualizar versões pelo Dockge ou pelo script `update-version.sh`.

## Validações

- scripts Shell validados;
- arquivos Compose validados;
- metadados da versão validados;
- pacote Dockge incluído na release;
- persistência, redes internas e portas revisadas.
```

## Mensagem de commit

```text
feat: adicionar implantação Dockge para VPS
```

## Mensagem de merge

```text
feat: disponibilizar implantação Docker gerenciada pelo Dockge
```
