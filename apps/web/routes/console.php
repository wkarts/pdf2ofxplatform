<?php

use App\Models\Conversion;
use Illuminate\Support\Facades\Schedule;

Schedule::call(function (): void {
    Conversion::query()
        ->where(
            'expires_at',
            '<',
            now()->subDays(7)
        )
        ->delete();
})
    ->dailyAt('03:30')
    ->name('cleanup-old-conversions')
    ->withoutOverlapping();
