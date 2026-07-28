# Validação funcional 1.0.0

A versão 1.0.0 foi executada contra três extratos reais fornecidos apenas para
validação local. Os documentos originais e os OFX resultantes **não fazem parte
do repositório**.

| Layout | Extração | Transações | Conciliação | Resultado |
|---|---:|---:|---:|---|
| Banco do Nordeste | texto nativo | 42 | diferença R$ 0,00 | concluído |
| Santander | texto posicionado | 177 | diferença R$ 0,00 | revisão de possíveis duplicidades |
| Itaú | OCR em 9 páginas | 299 | diferença detectada | revisão obrigatória |

O comportamento do Itaú é deliberadamente conservador: quando a camada OCR não
permite fechar matematicamente o extrato, o sistema não declara sucesso
silencioso. As transações ficam disponíveis para conferência, edição, exclusão,
restauração e nova geração do OFX.

## Verificações automatizadas

- 9 testes unitários Python aprovados;
- compilação sintática de todos os módulos Python;
- sintaxe de todos os arquivos PHP validada;
- sintaxe dos JavaScripts validada;
- YAML, JSON e scripts Shell validados;
- workflow de CI preparado para testes Laravel, Python e Docker Compose.
