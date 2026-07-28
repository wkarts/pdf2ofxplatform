# Parsers bancários

## Contrato

Um parser deve:

1. atribuir confiança de detecção entre 0 e 1;
2. extrair conta, período, saldos e transações;
3. preservar página de origem e confiança;
4. classificar créditos e débitos;
5. gerar FITID determinístico;
6. nunca inventar valores ausentes;
7. informar divergências para revisão.

## Pipeline de extração

Antes do parser, o serviço executa uma inspeção rápida com `pypdf`. PDFs com
camada textual seguem para `pdfplumber`. PDFs impressos como vetores/imagens vão
diretamente para Tesseract, evitando travamentos em documentos sem texto útil.

## Bancos iniciais

- **Itaú (341):** OCR, linhas posicionadas, datas completas e sinais inferidos
  pelo lançamento. Como OCR pode omitir caracteres, divergências ficam em
  `review_required`;
- **Banco do Nordeste (004):** seção textual de conta corrente, dia herdado e
  sufixos `+`/`-`;
- **Santander (033):** colunas físicas de crédito/débito e descrições
  continuadas;
- **Genérico:** data, descrição, valor e saldo opcional na mesma linha.

## Novo parser

1. Crie `services/converter/src/pdf2ofx/parsers/meu_banco.py`;
2. implemente `StatementParser`;
3. registre a classe em `ParserRegistry`;
4. adicione testes sintéticos e arquivos anonimizados de regressão;
5. valide saldo inicial + movimentos = saldo final.

Não inclua extratos reais no repositório.
