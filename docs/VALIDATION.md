# Validação funcional 1.1.0

A versão 1.1.0 preserva os três parsers calibrados e adiciona catálogo de bancos,
perfis dedicados, aliases e fallback universal. Os documentos originais e os
OFX resultantes usados na validação **não fazem parte do repositório**.

## PDFs reais fornecidos

| Layout | Extração | Transações | Conciliação | Resultado |
|---|---:|---:|---:|---|
| Banco do Nordeste | texto nativo | 42 | diferença R$ 0,00 | concluído |
| Santander | texto posicionado | 177 | diferença R$ 0,00 | revisão de possíveis duplicidades |
| Itaú | OCR em 9 páginas | 299 na validação 1.0.0 | diferença detectada | revisão obrigatória |

Nesta correção, Banco do Nordeste e Santander foram novamente processados com os
arquivos anexados: 42 e 177 transações, respectivamente, com diferença de
R$ 0,00. O OCR completo do Itaú continua sujeito ao tempo e à capacidade do
worker; o parser específico e seus testes de regressão foram preservados.

## Verificações automatizadas

- 15 testes Python aprovados;
- catálogo e aliases dos bancos solicitados validados;
- perfis adicionais exercitados com extratos sintéticos reconciliados;
- compilação sintática de todos os módulos Python;
- sintaxe dos arquivos PHP validada;
- workflow Laravel corrigido para versões compatíveis;
- workflow Python corrigido para os apontamentos do Ruff;
- Docker Compose validado pelo workflow de CI.

## Política de confiança

Um perfil cadastrado não significa que todos os layouts históricos e futuros do
banco sejam idênticos. Quando o resultado não fecha matematicamente ou depende
de inferência, o sistema retorna `review_required`, exibe os lançamentos e
permite correção antes da geração definitiva do OFX.
