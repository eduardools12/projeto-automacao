"""Ponto de entrada: busca um produto nas lojas e gera o relatório em Excel.

Exemplos:
    python main.py "fone bluetooth"
    python main.py "fone bluetooth" --valor-base 300 --nota-min 4 --marca jbl
    python main.py "air fryer" --lojas magalu --limite 10 --headless
"""
import argparse
import logging
import re
import sys
from datetime import datetime
from pathlib import Path

from selenium.common.exceptions import TimeoutException, WebDriverException

from comparador import coleta, historico, relatorio, tratamento

log = logging.getLogger("comparador")


def ler_argumentos(argv=None):
    parser = argparse.ArgumentParser(description="Compara preços de um produto em e-commerces.")
    parser.add_argument("termo", help='produto a buscar, por exemplo "fone bluetooth"')
    parser.add_argument("--lojas", nargs="+", choices=sorted(coleta.LOJAS), default=sorted(coleta.LOJAS),
                        help="lojas onde buscar (padrão: todas)")
    parser.add_argument("--limite", type=int, default=20, help="máximo de produtos por loja (padrão: 20)")
    parser.add_argument("--valor-base", type=float, help="valor de referência para a aba de faixas de preço")
    parser.add_argument("--preco-min", type=float, help="filtro: preço mínimo")
    parser.add_argument("--nota-min", type=float, help="filtro: nota mínima de avaliação (ex.: 4.0)")
    parser.add_argument("--loja", help="filtro: mostrar só uma loja")
    parser.add_argument("--marca", help="filtro: marca que precisa aparecer no título")
    parser.add_argument("--saida", default="relatorios", help="pasta dos relatórios (padrão: relatorios)")
    parser.add_argument("--headless", action="store_true", help="roda sem abrir a janela do navegador")
    return parser.parse_args(argv)


def nome_arquivo(termo, momento):
    slug = re.sub(r"[^a-z0-9]+", "-", termo.lower()).strip("-") or "busca"
    return f"comparativo_{slug}_{momento:%Y-%m-%d_%H%M}.xlsx"


def coletar(args):
    """Busca em cada loja. Se uma loja falhar, registra o erro e segue para a próxima."""
    produtos = []
    navegador = coleta.abrir_navegador(headless=args.headless)
    try:
        for nome in args.lojas:
            try:
                produtos += coleta.LOJAS[nome](navegador, args.termo, args.limite)
            except TimeoutException:
                log.error("%s: a página não carregou os produtos a tempo", nome)
            except WebDriverException as erro:
                log.error("%s: erro do navegador: %s", nome, erro.msg)
    finally:
        navegador.quit()
    return produtos


def main(argv=None):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        datefmt="%H:%M:%S")
    args = ler_argumentos(argv)
    momento = datetime.now()
    pasta = Path(args.saida)

    produtos = tratamento.tratar(coletar(args))
    if not produtos:
        log.error("Nenhum produto coletado. Confira a conexão ou se os sites mudaram.")
        return 1

    resumo = tratamento.resumir(produtos)
    usou_filtro = any(v is not None for v in (args.preco_min, args.nota_min, args.loja, args.marca))
    filtrados = tratamento.filtrar(produtos, args.preco_min, args.nota_min, args.loja, args.marca) \
        if usou_filtro else None

    arquivo_historico = pasta / "historico_precos.csv"
    historico.registrar(produtos, args.termo, arquivo_historico, momento)

    caminho = relatorio.gerar(
        pasta / nome_arquivo(args.termo, momento),
        produtos,
        resumo,
        valor_base=args.valor_base,
        filtrados=filtrados,
        evolucao=historico.evolucao(arquivo_historico, args.termo),
    )
    log.info("%d produtos coletados (%d com preço). Relatório: %s",
             resumo["total_coletado"], resumo["total_com_preco"], caminho)
    return 0


if __name__ == "__main__":
    sys.exit(main())
