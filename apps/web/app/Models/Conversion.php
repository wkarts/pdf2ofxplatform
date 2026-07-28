<?php

namespace App\Models;

use App\Enums\ConversionStatus;
use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Model;

class Conversion extends Model
{
    use HasUuids;

    protected $fillable = [
        'job_id',
        'session_id',
        'original_name',
        'bank_hint',
        'detected_bank',
        'status',
        'output_format',
        'transaction_count',
        'error_message',
        'result_payload',
        'completed_at',
        'expires_at',
    ];

    protected function casts(): array
    {
        return [
            'status' => ConversionStatus::class,
            'result_payload' => 'array',
            'completed_at' => 'datetime',
            'expires_at' => 'datetime',
            'transaction_count' => 'integer',
        ];
    }
}
