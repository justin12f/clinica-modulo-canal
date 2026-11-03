# tests/unit/test_phone.py
import pytest

from app.core.types import PhoneNumber

CANONICO = "+5214793066911"


@pytest.mark.parametrize(
    "crudo",
    [
        "4793066911",
        "479 306 6911",
        "479-306-6911",
        "(479) 306-6911",
        "044 479 306 6911",
        "045 479 306 6911",
        "01 479 306 6911",
        "+52 479 306 6911",
        "52 479 306 6911",
        "+52 1 479 306 6911",
        "+5214793066911",
        "5214793066911",
    ],
)
def test_todas_las_variantes_de_un_movil_resuelven_al_mismo_numero(crudo):
    assert PhoneNumber.parse(crudo).e164 == CANONICO


def test_la_canonicalizacion_mx_es_por_longitud_no_por_tipo():
    """POSITIVA. Desde la renumeracion de 2019, phonenumbers no distingue fijo de
    movil en Mexico: casi todo resuelve a FIXED_LINE_OR_MOBILE. La regla es por
    LONGITUD: 10 digitos nacionales -> +521 + 10. Un fijo recibe un 1 que no le
    corresponde, y es inocuo: un fijo no puede tener WhatsApp, asi que nunca
    colisiona con un wa_id real."""
    assert PhoneNumber.parse("+52 55 5555 5555").e164 == "+5215555555555"


def test_la_regla_del_uno_es_solo_para_mexico():
    """NEGATIVA. Ningun otro pais recibe el tratamiento."""
    assert PhoneNumber.parse("+1 415 555 0123").e164 == "+14155550123"
    assert PhoneNumber.parse("+34 612 345 678").e164 == "+34612345678"


@pytest.mark.parametrize("basura", ["", "hola", "12", "+999999999999999999"])
def test_lo_que_no_parsea_lanza(basura):
    with pytest.raises(ValueError):
        PhoneNumber.parse(basura)


def test_sin_prefijo_se_lee_con_el_pais_que_se_le_pasa():
    """POSITIVA. El país de la clínica (`tenant.country`) decide la lectura."""
    assert PhoneNumber.parse("612 345 678", "ES").e164 == "+34612345678"
    assert PhoneNumber.parse("300 123 4567", "CO").e164 == "+573001234567"


def test_un_numero_espanol_no_se_lee_como_mexicano():
    """NEGATIVA. Con país México, nueve dígitos españoles no son un número."""
    with pytest.raises(ValueError):
        PhoneNumber.parse("612 345 678", "MX")
