@extends('layouts.app')

@section('title', 'Converter extrato PDF para OFX')

@section('content')
<section class="hero">
    <div>
        <span class="eyebrow">
            Conversor bancário
        </span>
        <h1>
            Converta extratos PDF para OFX
        </h1>
        <p>
            Envie o extrato, revise as transações
            identificadas e baixe um OFX compatível
            com sistemas contábeis e ERPs.
        </p>
    </div>

    <div class="hero-points">
        <span>OCR automático</span>
        <span>Revisão antes do download</span>
        <span>Arquivos temporários</span>
    </div>
</section>

<section class="card upload-card">
    <form
        action="{{ route('conversions.store') }}"
        method="post"
        enctype="multipart/form-data"
        id="upload-form"
    >
        @csrf

        <label
            class="dropzone"
            id="dropzone"
            for="statement"
        >
            <input
                id="statement"
                name="statement"
                type="file"
                accept="application/pdf,.pdf"
                required
            >

            <span class="dropzone-icon">PDF</span>

            <strong>
                Arraste o extrato ou clique
                para selecionar
            </strong>

            <small>
                Somente PDF · limite de
                {{
                    number_format(
                        config(
                            'pdf2ofx.max_upload_kb'
                        ) / 1024,
                        0,
                        ',',
                        '.'
                    )
                }}
                MB
            </small>

            <span
                id="selected-file"
                class="selected-file"
            ></span>
        </label>

        <div class="form-grid">
            <label>
                <span>Banco</span>
                <select name="bank_hint">
                    <option value="auto">
                        Detectar automaticamente
                    </option>
                    <optgroup label="Bancos principais">
                        @foreach (config('pdf2ofx.banks', []) as $key => $bank)
                            @if ($bank['featured'])
                                <option value="{{ $key }}">
                                    {{ $bank['name'] }} · {{ $bank['code'] }}
                                </option>
                            @endif
                        @endforeach
                    </optgroup>
                    <optgroup label="Outros bancos cadastrados">
                        @foreach (config('pdf2ofx.banks', []) as $key => $bank)
                            @if (! $bank['featured'])
                                <option value="{{ $key }}">
                                    {{ $bank['name'] }} · {{ $bank['code'] }}
                                </option>
                            @endif
                        @endforeach
                    </optgroup>
                    <option value="generic">
                        Outro banco · parser universal
                    </option>
                </select>
            </label>

            <label>
                <span>Formato</span>
                <select name="output_format">
                    <option value="ofx_102">
                        OFX 1.02 · SGML
                        · Windows-1252
                    </option>
                </select>
            </label>
        </div>

        <button
            class="button button-primary button-large"
            type="submit"
            id="submit-button"
        >
            Converter para OFX
        </button>
    </form>
</section>

<section class="feature-grid">
    <article class="feature">
        <strong>Detecção bancária</strong>
        <p>
            Reconhece bancos brasileiros cadastrados e
            utiliza parser universal para outros layouts.
        </p>
    </article>

    <article class="feature">
        <strong>Conciliação</strong>
        <p>
            Compara saldos e destaca divergências
            antes da exportação.
        </p>
    </article>

    <article class="feature">
        <strong>Privacidade</strong>
        <p>
            O conteúdo é mantido somente durante
            o período necessário.
        </p>
    </article>
</section>

@if ($recentConversions->isNotEmpty())
    <section class="card recent-card">
        <div class="section-heading">
            <h2>Conversões recentes</h2>
        </div>

        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>Arquivo</th>
                        <th>Status</th>
                        <th>Banco</th>
                        <th>Data</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    @foreach ($recentConversions as $item)
                        <tr>
                            <td>
                                {{ $item->original_name }}
                            </td>
                            <td>
                                <span
                                    class="status status-{{
                                        $item->status->value
                                    }}"
                                >
                                    {{
                                        $item->status->label()
                                    }}
                                </span>
                            </td>
                            <td>
                                {{
                                    $item->detected_bank
                                        ?: '—'
                                }}
                            </td>
                            <td>
                                {{
                                    $item->created_at
                                        ->format(
                                            'd/m/Y H:i'
                                        )
                                }}
                            </td>
                            <td>
                                <a
                                    class="text-link"
                                    href="{{
                                        route(
                                            'conversions.show',
                                            $item
                                        )
                                    }}"
                                >
                                    Abrir
                                </a>
                            </td>
                        </tr>
                    @endforeach
                </tbody>
            </table>
        </div>
    </section>
@endif
@endsection
