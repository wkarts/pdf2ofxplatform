# Validação da versão 1.1.1

## Correção aplicada

O job `converter` do GitHub Actions falhava no comando `ruff check src tests` com o código `I001` no arquivo `src/pdf2ofx/parsers/helpers.py`.

A ordem dos imports da biblioteca padrão foi corrigida para:

```python
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
```

## Verificações executadas

- suíte Python: 15 testes aprovados;
- compilação de todos os módulos Python;
- sintaxe de 24 arquivos PHP;
- leitura estrutural dos arquivos JSON e YAML;
- sintaxe dos scripts Shell;
- ausência de PDFs e OFX reais no pacote;
- integridade do arquivo ZIP.

A execução local do Ruff não pôde baixar o binário no ambiente de empacotamento por indisponibilidade temporária do repositório de pacotes. A correção aplicada corresponde exatamente à alteração indicada pelo próprio Ruff no log do GitHub Actions.
