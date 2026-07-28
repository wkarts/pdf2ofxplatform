<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class HomePageTest extends TestCase
{
    use RefreshDatabase;

    public function test_home_page_is_available(): void
    {
        $this->get('/')
            ->assertOk()
            ->assertSee('Converta extratos PDF para OFX');
    }

    public function test_home_page_lists_requested_banks_and_universal_fallback(): void
    {
        $this->get('/')
            ->assertOk()
            ->assertSee('Banco do Brasil')
            ->assertSee('Santander')
            ->assertSee('Banco Inter')
            ->assertSee('Caixa Econômica Federal')
            ->assertSee('Bradesco')
            ->assertSee('Banco do Nordeste')
            ->assertSee('Itaú')
            ->assertSee('Next')
            ->assertSee('Nubank')
            ->assertSee('Mercado Pago')
            ->assertSee('Outro banco · parser universal');
    }
}
