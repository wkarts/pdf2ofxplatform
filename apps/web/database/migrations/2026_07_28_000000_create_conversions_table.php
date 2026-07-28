<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create(
            'conversions',
            function (Blueprint $table): void {
                $table->uuid('id')->primary();
                $table->uuid('job_id')->unique();
                $table->uuid('session_id')->index();
                $table->string('original_name');
                $table->string(
                    'bank_hint',
                    30
                )->default('auto');
                $table->string(
                    'detected_bank'
                )->nullable();
                $table->string(
                    'status',
                    30
                )->index();
                $table->string(
                    'output_format',
                    30
                )->default('ofx_102');
                $table->unsignedInteger(
                    'transaction_count'
                )->default(0);
                $table->text(
                    'error_message'
                )->nullable();
                $table->json(
                    'result_payload'
                )->nullable();
                $table->timestampTz(
                    'completed_at'
                )->nullable();
                $table->timestampTz(
                    'expires_at'
                )->nullable()->index();
                $table->timestampsTz();
            }
        );
    }

    public function down(): void
    {
        Schema::dropIfExists('conversions');
    }
};
