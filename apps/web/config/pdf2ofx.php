<?php

return [
    'max_upload_kb' => (int) env(
        'MAX_UPLOAD_KB',
        51200
    ),

    'banks' => [
        'bb' => ['name' => 'Banco do Brasil', 'code' => '001', 'featured' => true],
        'santander' => ['name' => 'Santander', 'code' => '033', 'featured' => true],
        'inter' => ['name' => 'Banco Inter', 'code' => '077', 'featured' => true],
        'caixa' => ['name' => 'Caixa Econômica Federal', 'code' => '104', 'featured' => true],
        'bradesco' => ['name' => 'Bradesco', 'code' => '237', 'featured' => true],
        'bnb' => ['name' => 'Banco do Nordeste', 'code' => '004', 'featured' => true],
        'itau' => ['name' => 'Itaú', 'code' => '341', 'featured' => true],
        'next' => ['name' => 'Next', 'code' => '237', 'featured' => true],
        'nubank' => ['name' => 'Nubank', 'code' => '260', 'featured' => true],
        'mercado_pago' => ['name' => 'Mercado Pago', 'code' => '323', 'featured' => true],
        'sicoob' => ['name' => 'Sicoob', 'code' => '756', 'featured' => false],
        'sicredi' => ['name' => 'Sicredi', 'code' => '748', 'featured' => false],
        'c6' => ['name' => 'C6 Bank', 'code' => '336', 'featured' => false],
        'pagbank' => ['name' => 'PagBank / PagSeguro', 'code' => '290', 'featured' => false],
        'stone' => ['name' => 'Stone', 'code' => '197', 'featured' => false],
        'safra' => ['name' => 'Banco Safra', 'code' => '422', 'featured' => false],
        'banrisul' => ['name' => 'Banrisul', 'code' => '041', 'featured' => false],
        'btg' => ['name' => 'BTG Pactual', 'code' => '208', 'featured' => false],
        'original' => ['name' => 'Banco Original', 'code' => '212', 'featured' => false],
        'bv' => ['name' => 'Banco BV', 'code' => '655', 'featured' => false],
        'picpay' => ['name' => 'PicPay', 'code' => '380', 'featured' => false],
        'xp' => ['name' => 'Banco XP', 'code' => '348', 'featured' => false],
        'pan' => ['name' => 'Banco PAN', 'code' => '623', 'featured' => false],
        'bs2' => ['name' => 'Banco BS2', 'code' => '218', 'featured' => false],
        'basa' => ['name' => 'Banco da Amazônia', 'code' => '003', 'featured' => false],
        'brb' => ['name' => 'BRB', 'code' => '070', 'featured' => false],
        'banpara' => ['name' => 'Banpará', 'code' => '037', 'featured' => false],
        'banestes' => ['name' => 'Banestes', 'code' => '021', 'featured' => false],
        'bmg' => ['name' => 'Banco BMG', 'code' => '318', 'featured' => false],
        'daycoval' => ['name' => 'Banco Daycoval', 'code' => '707', 'featured' => false],
        'mercantil' => ['name' => 'Banco Mercantil', 'code' => '389', 'featured' => false],
        'unicred' => ['name' => 'Unicred', 'code' => '136', 'featured' => false],
        'cresol' => ['name' => 'Cresol', 'code' => '133', 'featured' => false],
    ],
];
