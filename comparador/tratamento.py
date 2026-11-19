"""Tratamento dos dados coletados.

Nada aqui depende do navegador: são funções puras, fáceis de testar.
"""
import re
from statistics import mean

# "R$ 1.299,90" ou "R$1.299,90"
PADRAO_PRECO = re.compile(r"R\$\s?[\d.]+,\d{2}")
# "4,5" ou "4.5" (nota de avaliação)
PADRAO_NOTA = re.compile(r"\d[.,]\d")


def preco_para_float(texto):
    """Converte "R$ 1.299,90" em 1299.9. Retorna None quando não há preço válido."""
    if not texto:
        return None
    limpo = texto.replace("R$", "").replace("ou ", "").strip()
    limpo = limpo.replace(".", "")   # tira o ponto de milhar
    limpo = limpo.replace(",", ".")  # vírgula decimal vira ponto
    try:
        valor = float(limpo)
    except ValueError:
        return None
    return valor if valor > 0 else None


def preco_no_texto(texto):
    """Plano B: procura um preço no texto do card quando o seletor da página falha."""
    if not texto:
        return None
    # Em promoções, o preço final costuma vir depois de "por R$"
    if "por R$" in texto:
        depois = texto.split("por R$", 1)[1]
        achado = re.search(r"[\d.]+,\d{2}", depois)
        if achado:
            return f"R$ {achado.group()}"
    achado = PADRAO_PRECO.search(texto)
    return achado.group() if achado else None


def avaliacao_no_texto(texto):
    """Plano B da avaliação: procura algo como "4,5 (120)" no texto do card."""
    if not texto:
        return None
    achado = re.search(r"\d[.,]\d\s\(\d+\)", texto)
    return achado.group() if achado else None


def nota_para_float(texto):
    """Extrai a nota de uma avaliação ("4,5 de 5 estrelas" -> 4.5)."""
    if not texto:
        return None
    achado = PADRAO_NOTA.search(texto)
    if not achado:
        return None
    return float(achado.group().replace(",", "."))


def tratar(produtos):
    """Acrescenta a cada produto o preço e a nota em formato numérico."""
    for produto in produtos:
        produto["preco"] = preco_para_float(produto.get("preco_texto"))
        produto["nota"] = nota_para_float(produto.get("avaliacao"))
    return produtos


def resumir(produtos):
    """Média por loja, produto mais barato e mais caro (só produtos com preço)."""
    com_preco = [p for p in produtos if p["preco"] is not None]
    medias = {}
    for loja in sorted({p["loja"] for p in com_preco}):
        medias[loja] = mean(p["preco"] for p in com_preco if p["loja"] == loja)
    return {
        "total_coletado": len(produtos),
        "total_com_preco": len(com_preco),
        "medias": medias,
        "mais_barato": min(com_preco, key=lambda p: p["preco"]) if com_preco else None,
        "mais_caro": max(com_preco, key=lambda p: p["preco"]) if com_preco else None,
    }


def classificar_faixa(preco, valor_base):
    """Compara o preço com um valor de referência."""
    if preco >= valor_base * 0.8:
        return "Acima da faixa (80% ou mais)"
    if preco >= valor_base * 0.5:
        return "Dentro da faixa (50% a 80%)"
    return "Muito barato (menos de 50%)"


def filtrar(produtos, preco_min=None, nota_min=None, loja=None, marca=None):
    """Aplica só os filtros informados (os que forem None são ignorados)."""
    resultado = []
    for p in produtos:
        if preco_min is not None and (p["preco"] is None or p["preco"] < preco_min):
            continue
        if nota_min is not None and (p["nota"] is None or p["nota"] < nota_min):
            continue
        if loja and p["loja"].lower() != loja.lower():
            continue
        if marca and marca.lower() not in p["titulo"].lower():
            continue
        resultado.append(p)
    return resultado
