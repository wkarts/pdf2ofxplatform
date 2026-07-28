<?php

namespace App\Http\Controllers;

use App\Enums\ConversionStatus;
use App\Models\Conversion;
use App\Services\ConverterClient;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Str;
use Illuminate\Validation\Rule;
use Illuminate\View\View;
use RuntimeException;
use Symfony\Component\HttpFoundation\StreamedResponse;

class ConversionController extends Controller
{
    public function index(Request $request): View
    {
        $sessionId = $this->sessionId($request);

        return view('home', [
            'recentConversions' => Conversion::query()
                ->where('session_id', $sessionId)
                ->latest()
                ->limit(10)
                ->get(),
        ]);
    }

    public function store(
        Request $request,
        ConverterClient $client
    ): RedirectResponse {
        $maxKb = (int) config('pdf2ofx.max_upload_kb', 51200);

        $validated = $request->validate([
            'statement' => [
                'required',
                'file',
                'mimetypes:application/pdf,application/octet-stream',
                "max:{$maxKb}",
            ],
            'bank_hint' => [
                'nullable',
                'string',
                Rule::in([
                    'auto',
                    'generic',
                    ...array_keys((array) config('pdf2ofx.banks', [])),
                ]),
            ],
            'output_format' => [
                'required',
                'string',
                'in:ofx_102',
            ],
        ], [
            'statement.required' => 'Selecione um extrato em PDF.',
            'statement.mimetypes' => 'O arquivo precisa ser um PDF válido.',
            'statement.max' => 'O arquivo excede o limite permitido.',
        ]);

        try {
            $result = $client->create(
                $validated['statement'],
                $validated['bank_hint'] ?? 'auto',
                $validated['output_format']
            );

            $conversion = Conversion::query()->create([
                'job_id' => $result['job_id'],
                'session_id' => $this->sessionId($request),
                'original_name' => Str::limit(
                    $validated['statement']->getClientOriginalName(),
                    255,
                    ''
                ),
                'bank_hint' => $validated['bank_hint'] ?? 'auto',
                'status' => ConversionStatus::Queued,
                'output_format' => $validated['output_format'],
                'expires_at' => now()->addHours(
                    (int) ($result['ttl_hours'] ?? 24)
                ),
                'result_payload' => $result,
            ]);

            return redirect()->route(
                'conversions.show',
                $conversion
            );
        } catch (RuntimeException $exception) {
            return back()
                ->withInput()
                ->withErrors([
                    'statement' => $exception->getMessage(),
                ]);
        }
    }

    public function show(Request $request, Conversion $conversion): View
    {
        $this->guardOwnership($request, $conversion);

        return view(
            'conversions.show',
            compact('conversion')
        );
    }

    public function status(
        Request $request,
        Conversion $conversion,
        ConverterClient $client
    ): JsonResponse {
        $this->guardOwnership($request, $conversion);

        if ($conversion->expires_at?->isPast()) {
            return response()->json([
                'ok' => false,
                'message' => 'Esta conversão expirou. Envie o PDF novamente.',
            ], 410);
        }

        try {
            $payload = $client->status($conversion->job_id);

            $this->synchronize($conversion, $payload);

            $fresh = $conversion->fresh();

            return response()->json([
                'ok' => true,
                'conversion' => [
                    ...$fresh->toArray(),
                    'status_label' => $fresh->status->label(),
                ],
                'payload' => $payload,
            ]);
        } catch (RuntimeException $exception) {
            return response()->json([
                'ok' => false,
                'message' => $exception->getMessage(),
            ], 502);
        }
    }

    public function updateTransaction(
        Request $request,
        Conversion $conversion,
        int $index,
        ConverterClient $client
    ): JsonResponse {
        $this->guardOwnership($request, $conversion);

        $validated = $request->validate([
            'posted_at' => [
                'sometimes',
                'date_format:Y-m-d',
            ],
            'description' => [
                'sometimes',
                'string',
                'max:500',
            ],
            'document_number' => [
                'sometimes',
                'nullable',
                'string',
                'max:100',
            ],
            'amount' => [
                'sometimes',
                'numeric',
            ],
            'deleted' => [
                'sometimes',
                'boolean',
            ],
        ]);

        try {
            $payload = $client->updateTransaction(
                $conversion->job_id,
                $index,
                $validated
            );

            $this->synchronize($conversion, $payload);

            return response()->json([
                'ok' => true,
                'payload' => $payload,
            ]);
        } catch (RuntimeException $exception) {
            return response()->json([
                'ok' => false,
                'message' => $exception->getMessage(),
            ], 422);
        }
    }

    public function download(
        Request $request,
        Conversion $conversion,
        ConverterClient $client
    ): StreamedResponse {
        $this->guardOwnership($request, $conversion);
        abort_if(
            $conversion->expires_at?->isPast(),
            410,
            'Esta conversão expirou. Envie o PDF novamente.'
        );

        $upstream = $client->download(
            $conversion->job_id
        );

        $filename = pathinfo(
            $conversion->original_name,
            PATHINFO_FILENAME
        ).'.ofx';

        return response()->streamDownload(
            function () use ($upstream): void {
                $body = $upstream
                    ->toPsrResponse()
                    ->getBody();

                while (! $body->eof()) {
                    echo $body->read(8192);
                    flush();
                }
            },
            $filename,
            [
                'Content-Type' => (
                    'application/x-ofx; '.
                    'charset=windows-1252'
                ),
                'Cache-Control' => (
                    'private, no-store, max-age=0'
                ),
            ]
        );
    }

    private function synchronize(
        Conversion $conversion,
        array $payload
    ): void {
        $status = ConversionStatus::tryFrom(
            (string) ($payload['status'] ?? 'queued')
        ) ?? ConversionStatus::Queued;

        $conversion->forceFill([
            'status' => $status,
            'detected_bank' => data_get(
                $payload,
                'result.bank.name'
            ),
            'transaction_count' => data_get(
                $payload,
                'result.transaction_count',
                0
            ),
            'error_message' => data_get(
                $payload,
                'error.message'
            ),
            'result_payload' => $payload,
            'completed_at' => (
                $status->isFinished()
                    ? ($conversion->completed_at ?? now())
                    : null
            ),
        ])->save();
    }

    private function sessionId(Request $request): string
    {
        $sessionId = $request->session()->get('pdf2ofx_session_id');

        if (! is_string($sessionId) || ! Str::isUuid($sessionId)) {
            $sessionId = (string) Str::uuid();
            $request->session()->put('pdf2ofx_session_id', $sessionId);
        }

        return $sessionId;
    }

    private function guardOwnership(
        Request $request,
        Conversion $conversion
    ): void {
        abort_unless(
            hash_equals(
                $conversion->session_id,
                $this->sessionId($request)
            ),
            404
        );
    }
}
