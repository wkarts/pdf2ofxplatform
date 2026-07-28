<?php

use App\Http\Controllers\ConversionController;
use Illuminate\Support\Facades\Route;

Route::get(
    '/',
    [ConversionController::class, 'index']
)->name('home');

Route::post(
    '/conversions',
    [ConversionController::class, 'store']
)
    ->middleware('throttle:20,1')
    ->name('conversions.store');

Route::get(
    '/conversions/{conversion}',
    [ConversionController::class, 'show']
)->name('conversions.show');

Route::get(
    '/conversions/{conversion}/status',
    [ConversionController::class, 'status']
)
    ->middleware('throttle:120,1')
    ->name('conversions.status');

Route::patch(
    '/conversions/{conversion}/transactions/{index}',
    [ConversionController::class, 'updateTransaction']
)
    ->middleware('throttle:120,1')
    ->whereNumber('index')
    ->name('conversions.transactions.update');

Route::get(
    '/conversions/{conversion}/download',
    [ConversionController::class, 'download']
)
    ->middleware('throttle:30,1')
    ->name('conversions.download');
