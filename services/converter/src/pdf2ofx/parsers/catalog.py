from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BankProfile:
    key: str
    name: str
    code: str
    identifiers: tuple[str, ...]
    aliases: tuple[str, ...] = ()


# O catálogo separa a identificação da instituição do mecanismo de leitura.
# Parsers calibrados podem substituir o parser universal sem alterar a API.
BANK_PROFILES: tuple[BankProfile, ...] = (
    BankProfile(
        key="bb",
        name="Banco do Brasil",
        code="001",
        identifiers=("BANCO DO BRASIL", "BB EMPRESARIAL", "OUROCARD"),
        aliases=("banco_brasil", "brasil"),
    ),
    BankProfile(
        key="santander",
        name="Santander",
        code="033",
        identifiers=("SANTANDER", "SANTANDER EMPRESAS", "CONTAMAX"),
    ),
    BankProfile(
        key="inter",
        name="Banco Inter",
        code="077",
        identifiers=("BANCO INTER", "INTER EMPRESAS", "CONTA DIGITAL INTER"),
    ),
    BankProfile(
        key="caixa",
        name="Caixa Econômica Federal",
        code="104",
        identifiers=("CAIXA ECONOMICA FEDERAL", "CAIXA TEM", "GERENCIADOR CAIXA EMPRESAS"),
        aliases=("cef",),
    ),
    BankProfile(
        key="bradesco",
        name="Bradesco",
        code="237",
        identifiers=("BANCO BRADESCO", "BRADESCO EMPRESAS", "NET EMPRESA"),
    ),
    BankProfile(
        key="bnb",
        name="Banco do Nordeste",
        code="004",
        identifiers=("BANCO DO NORDESTE", "INTERNET BANKING BNB", "BNB"),
        aliases=("nordeste",),
    ),
    BankProfile(
        key="itau",
        name="Itaú",
        code="341",
        identifiers=("ITAU", "ITAU EMPRESAS", "ITAÚ"),
    ),
    BankProfile(
        key="next",
        name="Next",
        code="237",
        identifiers=("BANCO NEXT", "NEXT BANCO", "NEXTJOY", "NEXT"),
    ),
    BankProfile(
        key="nubank",
        name="Nubank",
        code="260",
        identifiers=("NU PAGAMENTOS", "NUBANK", "CONTA PJ NUBANK", "NU EMPRESAS"),
        aliases=("nu", "nubanck"),
    ),
    BankProfile(
        key="mercado_pago",
        name="Mercado Pago",
        code="323",
        identifiers=("MERCADO PAGO", "MERCADOPAGO.COM", "MERCADO PAGO INSTITUICAO"),
        aliases=("mercadopago", "mp"),
    ),
    BankProfile(
        key="sicoob",
        name="Sicoob",
        code="756",
        identifiers=("SICOOB", "SISTEMA DE COOPERATIVAS DE CREDITO DO BRASIL"),
    ),
    BankProfile(
        key="sicredi",
        name="Sicredi",
        code="748",
        identifiers=("SICREDI", "BANCO COOPERATIVO SICREDI"),
    ),
    BankProfile(
        key="c6",
        name="C6 Bank",
        code="336",
        identifiers=("C6 BANK", "BANCO C6", "C6 EMPRESAS"),
        aliases=("c6_bank",),
    ),
    BankProfile(
        key="pagbank",
        name="PagBank",
        code="290",
        identifiers=("PAGBANK", "PAGSEGURO", "PAGSEGURO INTERNET"),
        aliases=("pagseguro",),
    ),
    BankProfile(
        key="stone",
        name="Stone",
        code="197",
        identifiers=("STONE PAGAMENTOS", "STONE INSTITUICAO", "CONTA STONE"),
    ),
    BankProfile(
        key="safra",
        name="Banco Safra",
        code="422",
        identifiers=("BANCO SAFRA", "SAFRA EMPRESAS"),
    ),
    BankProfile(
        key="banrisul",
        name="Banrisul",
        code="041",
        identifiers=("BANRISUL", "BANCO DO ESTADO DO RIO GRANDE DO SUL"),
    ),
    BankProfile(
        key="btg",
        name="BTG Pactual",
        code="208",
        identifiers=("BTG PACTUAL", "BANCO BTG"),
        aliases=("btg_pactual",),
    ),
    BankProfile(
        key="original",
        name="Banco Original",
        code="212",
        identifiers=("BANCO ORIGINAL", "ORIGINAL EMPRESAS"),
    ),
    BankProfile(
        key="bv",
        name="Banco BV",
        code="655",
        identifiers=("BANCO BV", "BANCO VOTORANTIM"),
    ),
    BankProfile(
        key="picpay",
        name="PicPay",
        code="380",
        identifiers=("PICPAY", "PICPAY BANK", "PICPAY SERVICOS"),
    ),
    BankProfile(
        key="xp",
        name="Banco XP",
        code="348",
        identifiers=("BANCO XP", "XP INVESTIMENTOS", "CONTA DIGITAL XP"),
    ),
    BankProfile(
        key="pan",
        name="Banco PAN",
        code="623",
        identifiers=("BANCO PAN", "PAN EMPRESAS"),
    ),
    BankProfile(
        key="bs2",
        name="Banco BS2",
        code="218",
        identifiers=("BANCO BS2", "BS2 EMPRESAS"),
    ),
    BankProfile(
        key="basa",
        name="Banco da Amazônia",
        code="003",
        identifiers=("BANCO DA AMAZONIA", "BASA"),
        aliases=("amazonia",),
    ),
    BankProfile(
        key="brb",
        name="BRB",
        code="070",
        identifiers=("BANCO DE BRASILIA", "BRB BANCO", "BRB EMPRESAS"),
    ),
    BankProfile(
        key="banpara",
        name="Banpará",
        code="037",
        identifiers=("BANCO DO ESTADO DO PARA", "BANPARA"),
    ),
    BankProfile(
        key="banestes",
        name="Banestes",
        code="021",
        identifiers=("BANESTES", "BANCO DO ESTADO DO ESPIRITO SANTO"),
    ),
    BankProfile(
        key="bmg",
        name="Banco BMG",
        code="318",
        identifiers=("BANCO BMG", "BMG EMPRESAS"),
    ),
    BankProfile(
        key="daycoval",
        name="Banco Daycoval",
        code="707",
        identifiers=("BANCO DAYCOVAL", "DAYCOVAL"),
    ),
    BankProfile(
        key="mercantil",
        name="Banco Mercantil",
        code="389",
        identifiers=("BANCO MERCANTIL", "MERCANTIL DO BRASIL"),
    ),
    BankProfile(
        key="unicred",
        name="Unicred",
        code="136",
        identifiers=("UNICRED", "CONFEDERACAO NACIONAL DAS COOPERATIVAS UNICRED"),
    ),
    BankProfile(
        key="cresol",
        name="Cresol",
        code="133",
        identifiers=("CRESOL", "CONFEDERACAO NACIONAL DAS COOPERATIVAS CENTRAIS"),
    ),
)


PROFILE_BY_KEY: dict[str, BankProfile] = {profile.key: profile for profile in BANK_PROFILES}
for profile in BANK_PROFILES:
    for alias in profile.aliases:
        PROFILE_BY_KEY[alias] = profile


def canonical_bank_key(value: str) -> str:
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    profile = PROFILE_BY_KEY.get(normalized)
    return profile.key if profile else normalized


def public_bank_catalog() -> list[dict[str, str]]:
    return [
        {
            "key": profile.key,
            "name": profile.name,
            "code": profile.code,
        }
        for profile in BANK_PROFILES
    ]
