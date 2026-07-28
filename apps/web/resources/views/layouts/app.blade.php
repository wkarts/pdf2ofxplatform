<!doctype html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1"
    >
    <meta
        name="csrf-token"
        content="{{ csrf_token() }}"
    >
    <title>
        @yield('title', config('app.name'))
    </title>
    <link
        rel="stylesheet"
        href="{{ asset('assets/app.css') }}"
    >
</head>
<body>
<header class="topbar">
    <div class="container topbar-inner">
        <a
            href="{{ route('home') }}"
            class="brand"
            aria-label="Início"
        >
            <span class="brand-mark">OFX</span>
            <span>{{ config('app.name') }}</span>
        </a>
        <span class="privacy-badge">
            Processamento temporário e seguro
        </span>
    </div>
</header>

<main class="container page-content">
    @if ($errors->any())
        <div class="alert alert-error">
            <strong>
                Não foi possível continuar.
            </strong>
            <ul>
                @foreach ($errors->all() as $error)
                    <li>{{ $error }}</li>
                @endforeach
            </ul>
        </div>
    @endif

    @yield('content')
</main>

<footer class="footer">
    <div class="container">
        {{ config('app.name') }}
        · PDF para OFX
        · {{ date('Y') }}
    </div>
</footer>

<script
    src="{{ asset('assets/app.js') }}"
    defer
></script>

@stack('scripts')
</body>
</html>
