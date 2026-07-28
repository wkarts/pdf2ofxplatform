<?php

namespace Tests\Feature;

use App\Enums\ConversionStatus;
use App\Models\Conversion;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Str;
use Tests\TestCase;

class ConversionPrivacyTest extends TestCase
{
    use RefreshDatabase;

    public function test_conversion_is_visible_only_to_its_anonymous_session(): void
    {
        $ownerSession = (string) Str::uuid();
        $otherSession = (string) Str::uuid();

        $conversion = Conversion::query()->create([
            'job_id' => (string) Str::uuid(),
            'session_id' => $ownerSession,
            'original_name' => 'extrato.pdf',
            'bank_hint' => 'auto',
            'status' => ConversionStatus::Queued,
            'output_format' => 'ofx_102',
            'expires_at' => now()->addHour(),
        ]);

        $this->withSession([
            'pdf2ofx_session_id' => $ownerSession,
        ])->get(route('conversions.show', $conversion))
            ->assertOk();

        $this->withSession([
            'pdf2ofx_session_id' => $otherSession,
        ])->get(route('conversions.show', $conversion))
            ->assertNotFound();
    }

    public function test_home_lists_only_current_session_conversions(): void
    {
        $session = (string) Str::uuid();

        Conversion::query()->create([
            'job_id' => (string) Str::uuid(),
            'session_id' => $session,
            'original_name' => 'meu-extrato.pdf',
            'bank_hint' => 'auto',
            'status' => ConversionStatus::Queued,
            'output_format' => 'ofx_102',
            'expires_at' => now()->addHour(),
        ]);

        Conversion::query()->create([
            'job_id' => (string) Str::uuid(),
            'session_id' => (string) Str::uuid(),
            'original_name' => 'extrato-de-outra-sessao.pdf',
            'bank_hint' => 'auto',
            'status' => ConversionStatus::Queued,
            'output_format' => 'ofx_102',
            'expires_at' => now()->addHour(),
        ]);

        $this->withSession([
            'pdf2ofx_session_id' => $session,
        ])->get('/')
            ->assertOk()
            ->assertSee('meu-extrato.pdf')
            ->assertDontSee('extrato-de-outra-sessao.pdf');
    }
}
