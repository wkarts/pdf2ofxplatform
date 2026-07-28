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
camada textual seguem para `pdfplumber`. PDFs impressos como vetores ou imagens
seguem para Tesseract OCR. A camada de extração entrega texto e palavras
posicionadas; os parsers não dependem diretamente do framework FastAPI.

## Parsers calibrados

- **Itaú (341):** OCR, linhas posicionadas, datas completas e sinais inferidos
  pelo lançamento;
- **Banco do Nordeste (004):** seção textual de conta corrente, dia herdado e
  sufixos `+`/`-`;
- **Santander (033):** colunas físicas de crédito/débito e descrições
  continuadas.

Esses parsers foram exercitados com os PDFs reais fornecidos para o projeto.

## Perfis bancários dedicados

O arquivo `parsers/catalog.py` cadastra chave, nome, código bancário,
identificadores e aliases. O `ProfiledBankParser` usa o perfil da instituição e
o `UniversalBrazilianParser` para interpretar layouts com:

- datas completas ou sem ano;
- sinal antes ou depois do valor;
- débito/crédito por texto, sufixo `D/C`, coluna ou variação do saldo;
- saldo inicial, saldo final e saldo após o lançamento;
- número de documento opcional;
- descrições continuadas em linhas seguintes;
- valores negativos entre parênteses;
- texto nativo ou OCR.

Perfis incluídos: Banco do Brasil, Inter, Caixa, Bradesco, Next, Nubank,
Mercado Pago, Sicoob, Sicredi, C6, PagBank, Stone, Safra, Banrisul, BTG,
Original, BV, PicPay, XP, PAN, BS2, Banco da Amazônia, BRB, Banpará,
Banestes, BMG, Daycoval, Mercantil, Unicred e Cresol.

## Outros bancos

Quando nenhuma instituição é identificada, o registro seleciona o parser
`generic`. Ele usa o mesmo mecanismo universal, grava código bancário `000` e
mantém o job em revisão quando saldos, direção dos movimentos ou confiança não
puderem ser confirmados.

## Calibrar um novo layout

1. anonimize uma amostra PDF e o OFX esperado;
2. crie `services/converter/src/pdf2ofx/parsers/meu_banco.py`;
3. implemente `StatementParser` ou especialize o parser universal;
4. registre a classe antes do parser perfilado em `ParserRegistry`;
5. adicione teste sintético e regressão anonimizada;
6. valide `saldo inicial + movimentos = saldo final`.

Não inclua extratos reais no repositório.
