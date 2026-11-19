import pytest

from comparador import tratamento as t


@pytest.mark.parametrize("texto, esperado", [
    ("R$ 1.299,90", 1299.90),
    ("R$1.299,90", 1299.90),
    ("ou R$ 89,90", 89.90),
    ("R$ 0,00", None),
    ("Indisponível", None),
    (None, None),
])
def test_preco_para_float(texto, esperado):
    assert t.preco_para_float(texto) == esperado


def test_preco_no_texto_prefere_o_preco_depois_de_por():
    card = "Fone JBL\nde R$ 399,90\npor R$ 249,90\nem 10x"
    assert t.preco_no_texto(card) == "R$ 249,90"


def test_preco_no_texto_sem_promocao():
    assert t.preco_no_texto("Fone JBL\nR$ 1.199,00 à vista") == "R$ 1.199,00"


def test_preco_no_texto_sem_preco():
    assert t.preco_no_texto("Produto esgotado") is None


def test_avaliacao_e_nota():
    assert t.avaliacao_no_texto("Fone\n4,7 (1532)\nR$ 99,90") == "4,7 (1532)"
    assert t.nota_para_float("4,5 de 5 estrelas") == 4.5
    assert t.nota_para_float("Sem avaliação") is None


def _produtos():
    return t.tratar([
        {"loja": "Amazon", "titulo": "Fone JBL Tune", "preco_texto": "R$ 200,00", "avaliacao": "4,6 de 5 estrelas", "link": "a"},
        {"loja": "Amazon", "titulo": "Fone Sony", "preco_texto": "R$ 400,00", "avaliacao": None, "link": "b"},
        {"loja": "Magalu", "titulo": "Fone JBL Wave", "preco_texto": "R$ 100,00", "avaliacao": "4,1 (30)", "link": "c"},
        {"loja": "Magalu", "titulo": "Fone sem preço", "preco_texto": None, "avaliacao": None, "link": "d"},
    ])


def test_resumir():
    r = t.resumir(_produtos())
    assert r["total_coletado"] == 4
    assert r["total_com_preco"] == 3
    assert r["medias"] == {"Amazon": 300.0, "Magalu": 100.0}
    assert r["mais_barato"]["titulo"] == "Fone JBL Wave"
    assert r["mais_caro"]["titulo"] == "Fone Sony"


def test_resumir_sem_precos():
    r = t.resumir(t.tratar([{"loja": "Amazon", "titulo": "x", "preco_texto": None, "avaliacao": None}]))
    assert r["mais_barato"] is None and r["medias"] == {}


@pytest.mark.parametrize("preco, faixa", [
    (80, "Acima"), (100, "Acima"), (50, "Dentro"), (79.99, "Dentro"), (49.99, "Muito barato"),
])
def test_classificar_faixa(preco, faixa):
    assert t.classificar_faixa(preco, 100).startswith(faixa)


def test_filtrar_combina_criterios():
    produtos = _produtos()
    assert [p["titulo"] for p in t.filtrar(produtos, marca="jbl")] == ["Fone JBL Tune", "Fone JBL Wave"]
    assert [p["titulo"] for p in t.filtrar(produtos, marca="JBL", nota_min=4.5)] == ["Fone JBL Tune"]
    assert [p["titulo"] for p in t.filtrar(produtos, preco_min=150, loja="amazon")] == ["Fone JBL Tune", "Fone Sony"]
    assert len(t.filtrar(produtos)) == 4
