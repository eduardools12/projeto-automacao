from datetime import datetime

import openpyxl

from comparador import historico, relatorio, tratamento


def _produtos():
    return tratamento.tratar([
        {"loja": "Amazon", "titulo": "Fone JBL", "preco_texto": "R$ 200,00", "avaliacao": "4,6 de 5", "link": "a"},
        {"loja": "Magalu", "titulo": "Fone Sony", "preco_texto": "R$ 100,00", "avaliacao": None, "link": "b"},
        {"loja": "Magalu", "titulo": "Sem preço", "preco_texto": None, "avaliacao": None, "link": None},
    ])


def test_historico_acumula_execucoes(tmp_path):
    csv = tmp_path / "historico.csv"
    produtos = _produtos()
    historico.registrar(produtos, "fone", csv, datetime(2026, 11, 10, 9, 0))
    produtos[0]["preco"] = 180.0
    historico.registrar(produtos, "fone", csv, datetime(2026, 11, 11, 9, 0))
    historico.registrar(produtos, "outro produto", csv, datetime(2026, 11, 11, 9, 0))

    linhas = csv.read_text(encoding="utf-8").splitlines()
    assert linhas[0] == ",".join(historico.COLUNAS)  # cabeçalho só uma vez
    assert len(linhas) == 1 + 2 * 3                    # sem a linha sem preço

    evolucao = historico.evolucao(csv, "FONE")
    amazon = [e["menor_preco"] for e in evolucao if e["loja"] == "Amazon"]
    assert amazon == [200.0, 180.0]


def test_evolucao_sem_arquivo(tmp_path):
    assert historico.evolucao(tmp_path / "nao_existe.csv", "fone") == []


def test_relatorio_tem_as_abas_e_precos_numericos(tmp_path):
    produtos = _produtos()
    caminho = relatorio.gerar(
        tmp_path / "saida" / "teste.xlsx",
        produtos,
        tratamento.resumir(produtos),
        valor_base=250,
        filtrados=tratamento.filtrar(produtos, marca="jbl"),
        evolucao=[{"data_hora": "2026-11-10 09:00", "loja": "Amazon",
                   "menor_preco": 200.0, "preco_medio": 200.0, "qtd": 1}],
    )
    wb = openpyxl.load_workbook(caminho)
    assert wb.sheetnames == ["Produtos", "Resumo", "Faixas de preço", "Filtrados", "Histórico"]

    aba = wb["Produtos"]
    assert aba["C2"].value == 100.0                    # ordenado do mais barato
    assert aba["C2"].number_format == relatorio.FORMATO_REAIS
    assert aba.max_row == 4                            # cabeçalho + 3 produtos
    assert wb["Filtrados"].max_row == 2


def test_relatorio_sem_opcionais(tmp_path):
    produtos = _produtos()
    caminho = relatorio.gerar(tmp_path / "x.xlsx", produtos, tratamento.resumir(produtos))
    assert openpyxl.load_workbook(caminho).sheetnames == ["Produtos", "Resumo"]
