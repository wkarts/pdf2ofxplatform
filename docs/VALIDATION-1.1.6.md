# Validação da versão 1.1.6

## Falha analisada

O build real da imagem `pdf2ofx-gateway` foi concluído. A falha ocorreu apenas
no passo de validação do runtime:

```text
host not found in upstream "app:9000"
nginx: configuration file /etc/nginx/nginx.conf test failed
```

O hostname `app` é fornecido pelo DNS interno do Docker Compose. O comando
anterior executava a imagem isoladamente, sem a rede Compose, portanto o NGINX
não conseguia resolver o upstream mesmo com a configuração correta para
produção.

## Correção

Foi criado `deploy/scripts/validate-gateway-image.sh`, responsável por:

1. registrar `app` no `/etc/hosts` temporário do container de validação;
2. executar `nginx -t` sem alterar o arquivo de configuração da imagem;
3. iniciar o gateway real;
4. consultar `http://127.0.0.1:8080/health` dentro do container;
5. exibir os logs e falhar caso o container encerre ou o endpoint não responda;
6. remover o container temporário ao finalizar.

O CI passou a chamar esse script no target `gateway`.

## Validações locais

- sintaxe Bash de todos os scripts em `deploy`;
- carregamento YAML de todos os workflows;
- consistência de `VERSION`, pacote Python, documentação e imagens;
- comparação entre `deploy/docker/compose.yaml` e
  `deploy/docker/docker-compose.yml`;
- compilação dos módulos Python;
- suíte de testes Python;
- sintaxe dos arquivos PHP;
- criação, extração e verificação dos pacotes de distribuição.

## Limitação do ambiente

O ambiente local usado para empacotamento não dispõe do daemon Docker. O build
real permanece obrigatório no GitHub Actions. A correção corresponde diretamente
à falha observada: o upstream passa a ser resolvido durante a validação isolada,
sem modificar a configuração usada em produção.
