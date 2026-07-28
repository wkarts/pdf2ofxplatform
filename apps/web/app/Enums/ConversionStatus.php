<?php

namespace App\Enums;

enum ConversionStatus: string
{
    case Queued = 'queued';
    case Processing = 'processing';
    case Completed = 'completed';
    case ReviewRequired = 'review_required';
    case Failed = 'failed';

    public function label(): string
    {
        return match ($this) {
            self::Queued => 'Na fila',
            self::Processing => 'Processando',
            self::Completed => 'Concluído',
            self::ReviewRequired => 'Revisão necessária',
            self::Failed => 'Falhou',
        };
    }

    public function isFinished(): bool
    {
        return in_array($this, [
            self::Completed,
            self::ReviewRequired,
            self::Failed,
        ], true);
    }
}
