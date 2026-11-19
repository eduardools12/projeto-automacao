"""Coleta dos produtos nos sites com Selenium.

Cada função recebe o navegador já aberto e devolve uma lista de dicionários
com os dados em texto, do jeito que aparecem na página. A conversão para
número fica em tratamento.py.
"""
import logging
from urllib.parse import quote, quote_plus

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from comparador.tratamento import avaliacao_no_texto, preco_no_texto

log = logging.getLogger(__name__)


def abrir_navegador(headless=False):
    """Abre o Chrome. O Selenium baixa o ChromeDriver certo sozinho."""
    opcoes = webdriver.ChromeOptions()
    opcoes.add_argument("--start-maximized")
    opcoes.add_argument("--disable-blink-features=AutomationControlled")
    if headless:
        opcoes.add_argument("--headless=new")  # roda sem abrir janela
    return webdriver.Chrome(options=opcoes)


def _texto(card, seletor, atributo=None):
    """Lê o texto (ou um atributo) de um elemento do card. None se não existir."""
    try:
        elemento = card.find_element(By.CSS_SELECTOR, seletor)
    except NoSuchElementException:
        return None
    valor = elemento.get_attribute(atributo) if atributo else elemento.text
    return valor.strip() if valor else None


def buscar_amazon(navegador, termo, limite=20, espera=10):
    navegador.get(f"https://www.amazon.com.br/s?k={quote_plus(termo)}")
    cards = WebDriverWait(navegador, espera).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'div[data-component-type="s-search-result"]')
        )
    )
    log.info("Amazon: %d produtos na página, lendo até %d", len(cards), limite)

    produtos = []
    for card in cards[:limite]:
        # O preço vem em duas partes: reais e centavos
        reais = _texto(card, "span.a-price-whole")
        centavos = _texto(card, "span.a-price-fraction")
        preco = f"R$ {reais},{centavos}" if reais and centavos else None

        avaliacao = (_texto(card, "div.a-row.a-size-small span", "aria-label")
                     or _texto(card, "div.a-row.a-size-small span"))

        produtos.append({
            "loja": "Amazon",
            "titulo": _texto(card, "h2") or "Sem título",
            "preco_texto": preco,
            "avaliacao": avaliacao,
            "link": _texto(card, "div.s-product-image-container a.a-link-normal", "href"),
        })
    return produtos


def buscar_magalu(navegador, termo, limite=20, espera=10):
    navegador.get(f"https://www.magazineluiza.com.br/busca/{quote(termo)}/")
    WebDriverWait(navegador, espera).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="product-card-container"]'))
    )
    cards = navegador.find_elements(By.CSS_SELECTOR, '[data-testid="product-card-container"]')
    log.info("Magalu: %d produtos na página, lendo até %d", len(cards), limite)

    produtos = []
    for card in cards[:limite]:
        texto_card = card.text
        if len(texto_card) < 10:  # card vazio ou ainda carregando
            continue

        titulo = _texto(card, '[data-testid="product-title"]')
        if not titulo:
            titulo = texto_card.split("\n")[0]

        # Plano A: seletor do preço. Plano B: procurar o preço no texto (Regex).
        preco = _texto(card, '[data-testid="price-value"]') or preco_no_texto(texto_card)

        produtos.append({
            "loja": "Magalu",
            "titulo": titulo,
            "preco_texto": preco,
            "avaliacao": (_texto(card, '[data-testid="review-primary-information"]')
                          or avaliacao_no_texto(texto_card)),
            "link": card.get_attribute("href") or _texto(card, "a", "href"),
        })
    return produtos


LOJAS = {
    "amazon": buscar_amazon,
    "magalu": buscar_magalu,
}
