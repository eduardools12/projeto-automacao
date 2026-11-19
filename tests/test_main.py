"""Roda o fluxo completo do main.py com um navegador e lojas falsos (sem internet)."""
import openpyxl
from selenium.common.exceptions import TimeoutException

import main
from comparador import coleta


class NavegadorFalso:
    fechado = False

    def quit(self):
        NavegadorFalso.fechado = True


def loja_ok(navegador, termo, limite):
    return [
        {"loja": "Amazon", "titulo": f"{termo} JBL", "preco_texto": "R$ 199,90", "avaliacao": "4,5 de 5", "link": "x"},
        {"loja": "Amazon", "titulo": f"{termo} Sony", "preco_texto": "R$ 299,90", "avaliacao": None, "link": "y"},
    ][:limite]


def loja_que_falha(navegador, termo, limite):
    raise TimeoutException("demorou")


def test_fluxo_completo(tmp_path, monkeypatch):
    monkeypatch.setattr(coleta, "abrir_navegador", lambda headless: NavegadorFalso())
    monkeypatch.setattr(coleta, "LOJAS", {"amazon": loja_ok, "magalu": loja_que_falha})

    codigo = main.main(["fone", "--saida", str(tmp_path), "--valor-base", "250", "--marca", "jbl"])

    assert codigo == 0
    assert NavegadorFalso.fechado                      # navegador fechado mesmo com erro numa loja
    relatorios = list(tmp_path.glob("comparativo_fone_*.xlsx"))
    assert len(relatorios) == 1
    wb = openpyxl.load_workbook(relatorios[0])
    assert wb.sheetnames == ["Produtos", "Resumo", "Faixas de preço", "Filtrados", "Histórico"]
    assert (tmp_path / "historico_precos.csv").exists()


def test_sem_produtos_retorna_erro(tmp_path, monkeypatch):
    monkeypatch.setattr(coleta, "abrir_navegador", lambda headless: NavegadorFalso())
    monkeypatch.setattr(coleta, "LOJAS", {"amazon": loja_que_falha, "magalu": loja_que_falha})
    assert main.main(["fone", "--saida", str(tmp_path)]) == 1
