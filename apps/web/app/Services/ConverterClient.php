<?php

namespace App\Services;

use Illuminate\Http\Client\PendingRequest;
use Illuminate\Http\Client\Response;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Http;
use RuntimeException;

class ConverterClient
{
    private function client(int $timeout): PendingRequest
    {
        return Http::baseUrl(rtrim((string) config('services.converter.base_url'), '/'))
            ->acceptJson()
            ->withHeaders([
                'X-Internal-API-Key' => (string) config('services.converter.api_key'),
            ])
            ->connectTimeout(10)
            ->timeout($timeout)
            ->retry(2, 500, throw: false);
    }

    public function create(
        UploadedFile $file,
        ?string $bankHint,
        string $format
    ): array {
        $stream = fopen($file->getRealPath(), 'rb');

        if ($stream === false) {
            throw new RuntimeException('Não foi possível abrir o arquivo enviado.');
        }

        try {
            $response = $this->client(
                (int) config('services.converter.request_timeout')
            )
                ->attach(
                    'file',
                    $stream,
                    $file->getClientOriginalName()
                )
                ->post('/v1/conversions', [
                    'bank_hint' => $bankHint ?: 'auto',
                    'output_format' => $format,
                ]);
        } finally {
            fclose($stream);
        }

        return $this->jsonOrFail(
            $response,
            'Não foi possível iniciar a conversão.'
        );
    }

    public function status(string $jobId): array
    {
        return $this->jsonOrFail(
            $this->client(
                (int) config('services.converter.request_timeout')
            )->get("/v1/conversions/{$jobId}"),
            'Não foi possível consultar a conversão.'
        );
    }

    public function updateTransaction(
        string $jobId,
        int $index,
        array $payload
    ): array {
        return $this->jsonOrFail(
            $this->client(
                (int) config('services.converter.request_timeout')
            )->patch(
                "/v1/conversions/{$jobId}/transactions/{$index}",
                $payload
            ),
            'Não foi possível alterar a transação.'
        );
    }

    public function download(string $jobId): Response
    {
        $response = $this->client(
            (int) config('services.converter.download_timeout')
        )
            ->withOptions(['stream' => true])
            ->get("/v1/conversions/{$jobId}/download");

        if (! $response->successful()) {
            throw new RuntimeException(
                'O arquivo OFX ainda não está disponível.'
            );
        }

        return $response;
    }

    private function jsonOrFail(
        Response $response,
        string $fallback
    ): array {
        if (! $response->successful()) {
            $message = data_get($response->json(), 'detail')
                ?? data_get($response->json(), 'message')
                ?? $fallback;

            throw new RuntimeException((string) $message);
        }

        return $response->json();
    }
}
