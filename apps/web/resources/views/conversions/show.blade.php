@extends('layouts.app')

@section('title', 'Conversão '.$conversion->original_name)

@section('content')
<section class="page-heading">
    <div>
        <a href="{{ route('home') }}" class="back-link">← Nova conversão</a>
        <h1>{{ $conversion->original_name }}</h1>
        <p>Acompanhe o processamento, revise os lançamentos e gere o arquivo OFX.</p>
    </div>
    <span
        id="status-badge"
        class="status status-{{ $conversion->status->value }}"
    >{{ $conversion->status->label() }}</span>
</section>

<section
    class="card conversion-card"
    id="conversion-app"
    data-status-url="{{ route('conversions.status', $conversion) }}"
    data-download-url="{{ route('conversions.download', $conversion) }}"
    data-update-url-template="{{ route('conversions.transactions.update', [$conversion, '__INDEX__']) }}"
    data-initial-status="{{ $conversion->status->value }}"
>
    <div id="processing-panel" class="processing-panel">
        <div class="spinner" aria-hidden="true"></div>
        <div>
            <strong id="processing-title">Preparando o extrato...</strong>
            <p id="processing-message">O arquivo está na fila de processamento.</p>
        </div>
    </div>

    <div id="error-panel" class="alert alert-error hidden">
        <strong>Não foi possível converter o extrato.</strong>
        <p id="error-message"></p>
    </div>

    <div id="result-panel" class="hidden">
        <div class="summary-grid">
            <article>
                <span>Banco detectado</span>
                <strong id="bank-name">—</strong>
            </article>
            <article>
                <span>Agência</span>
                <strong id="branch-number">—</strong>
            </article>
            <article>
                <span>Conta</span>
                <strong id="account-number">—</strong>
            </article>
            <article>
                <span>Transações</span>
                <strong id="transaction-count">0</strong>
            </article>
            <article>
                <span>Confiança</span>
                <strong id="confidence">—</strong>
            </article>
            <article>
                <span>Conciliação</span>
                <strong id="reconciliation-status">—</strong>
            </article>
        </div>

        <div id="warnings-panel" class="alert alert-warning hidden">
            <strong>Atenção antes de exportar</strong>
            <ul id="warnings-list"></ul>
        </div>

        <div class="section-heading result-heading">
            <div>
                <h2>Transações identificadas</h2>
                <p>Edite qualquer linha que tenha sido interpretada incorretamente.</p>
            </div>
            <a
                id="download-button"
                href="{{ route('conversions.download', $conversion) }}"
                class="button button-primary"
            >Baixar OFX</a>
        </div>

        <div class="table-wrap transactions-table-wrap">
            <table class="transactions-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Data</th>
                        <th>Descrição</th>
                        <th>Documento</th>
                        <th class="text-right">Valor</th>
                        <th class="text-right">Saldo</th>
                        <th>Conf.</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody id="transactions-body"></tbody>
            </table>
        </div>
    </div>
</section>

<template id="transaction-template">
    <tr>
        <td class="transaction-index"></td>
        <td><input class="transaction-date" type="date"></td>
        <td><input class="transaction-description" type="text" maxlength="500"></td>
        <td><input class="transaction-document" type="text" maxlength="100"></td>
        <td><input class="transaction-amount text-right" type="number" step="0.01"></td>
        <td class="transaction-balance text-right"></td>
        <td class="transaction-confidence"></td>
        <td class="actions-cell">
            <button type="button" class="icon-button save-transaction" title="Salvar">✓</button>
            <button type="button" class="icon-button danger delete-transaction" title="Excluir">×</button>
        </td>
    </tr>
</template>
@endsection

@push('scripts')
<script src="{{ asset('assets/conversion.js') }}" defer></script>
@endpush
