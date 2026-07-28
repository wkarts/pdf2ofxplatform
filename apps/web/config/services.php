<?php

return [
    'converter' => [
        'base_url' => env(
            'CONVERTER_BASE_URL',
            'http://converter-api:8000'
        ),
        'api_key' => env(
            'CONVERTER_API_KEY'
        ),
        'request_timeout' => (int) env(
            'CONVERTER_REQUEST_TIMEOUT',
            60
        ),
        'download_timeout' => (int) env(
            'CONVERTER_DOWNLOAD_TIMEOUT',
            300
        ),
    ],
];
