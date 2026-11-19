"""Geração do relatório em Excel: um arquivo, uma aba para cada análise."""
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font

from comparador.tratamento import classificar_faixa

FORMATO_REAIS = '"R$" #,##0.00'
COLUNAS_PRODUTO = ["Loja", "Produto", "Preço", "Nota", "Avaliação", "Link"]


def _cabecalho(aba, colunas):
    aba.append(colunas)
    for celula in aba[1]:
        celula.font = Font(bold=True)
        celula.alignment = Alignment(horizontal="center")
    aba.freeze_panes = "A2"


def _linha_produto(p):
    return [p["loja"], p["titulo"], p["preco"], p["nota"], p["avaliacao"], p["link"]]


def _ajustar(aba, colunas_reais=()):
    """Formata as colunas de preço em reais e ajusta a largura das colunas."""
    for letra in colunas_reais:
        for celula in aba[letra][1:]:
            celula.number_format = FORMATO_REAIS
    for coluna in aba.columns:
        maior = max(len(str(c.value)) if c.value is not None else 0 for c in coluna)
        aba.column_dimensions[coluna[0].column_letter].width = min(maior + 2, 60)


def gerar(caminho, produtos, resumo, valor_base=None, filtrados=None, evolucao=None):
    wb = openpyxl.Workbook()

    # 1. Todos os produtos coletados, do mais barato ao mais caro
    aba = wb.active
    aba.title = "Produtos"
    _cabecalho(aba, COLUNAS_PRODUTO)
    for p in sorted(produtos, key=lambda p: (p["preco"] is None, p["preco"] or 0)):
        aba.append(_linha_produto(p))
    _ajustar(aba, "C")

    # 2. Resumo estatístico
    aba = wb.create_sheet("Resumo")
    _cabecalho(aba, ["Indicador", "Produto", "Valor", "Link"])
    aba.append(["Produtos coletados", None, resumo["total_coletado"], None])
    aba.append(["Produtos com preço", None, resumo["total_com_preco"], None])
    for nome in ("mais_barato", "mais_caro"):
        p = resumo[nome]
        rotulo = "Mais barato" if nome == "mais_barato" else "Mais caro"
        if p:
            aba.append([rotulo, p["titulo"], p["preco"], p["link"]])
            aba.cell(row=aba.max_row, column=3).number_format = FORMATO_REAIS
    for loja, media in resumo["medias"].items():
        aba.append([f"Média {loja}", None, media, None])
        aba.cell(row=aba.max_row, column=3).number_format = FORMATO_REAIS
    _ajustar(aba)

    # 3. Faixas de preço em relação a um valor de referência (opcional)
    if valor_base:
        aba = wb.create_sheet("Faixas de preço")
        _cabecalho(aba, ["Faixa"] + COLUNAS_PRODUTO)
        for p in produtos:
            if p["preco"] is not None:
                aba.append([classificar_faixa(p["preco"], valor_base)] + _linha_produto(p))
        _ajustar(aba, "D")

    # 4. Produtos que passaram nos filtros (opcional)
    if filtrados is not None:
        aba = wb.create_sheet("Filtrados")
        _cabecalho(aba, COLUNAS_PRODUTO)
        for p in filtrados:
            aba.append(_linha_produto(p))
        _ajustar(aba, "C")

    # 5. Evolução do preço entre execuções (vem do histórico)
    if evolucao:
        aba = wb.create_sheet("Histórico")
        _cabecalho(aba, ["Data e hora", "Loja", "Menor preço", "Preço médio", "Qtd. produtos"])
        for e in evolucao:
            aba.append([e["data_hora"], e["loja"], e["menor_preco"], e["preco_medio"], e["qtd"]])
        _ajustar(aba, "CD")

    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    wb.save(caminho)
    return caminho
