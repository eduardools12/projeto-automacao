"""Histórico de preços em CSV.

Cada execução acrescenta linhas ao arquivo. Rodando a automação todo dia
(por exemplo pelo Agendador de Tarefas do Windows), o histórico mostra como
o preço de um produto muda com o tempo.
"""
import csv
from pathlib import Path
from statistics import mean

COLUNAS = ["data_hora", "termo", "loja", "titulo", "preco", "link"]


def registrar(produtos, termo, caminho, momento):
    """Acrescenta ao CSV os produtos com preço desta execução."""
    caminho = Path(caminho)
    arquivo_novo = not caminho.exists()
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("a", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=COLUNAS)
        if arquivo_novo:
            escritor.writeheader()
        for p in produtos:
            if p["preco"] is None:
                continue
            escritor.writerow({
                "data_hora": momento.strftime("%Y-%m-%d %H:%M"),
                "termo": termo,
                "loja": p["loja"],
                "titulo": p["titulo"],
                "preco": f"{p['preco']:.2f}",
                "link": p["link"] or "",
            })


def evolucao(caminho, termo):
    """Menor preço e preço médio por execução e loja, para um termo de busca."""
    caminho = Path(caminho)
    if not caminho.exists():
        return []
    grupos = {}
    with caminho.open(newline="", encoding="utf-8") as arquivo:
        for linha in csv.DictReader(arquivo):
            if linha["termo"].lower() != termo.lower():
                continue
            chave = (linha["data_hora"], linha["loja"])
            grupos.setdefault(chave, []).append(float(linha["preco"]))
    return [
        {"data_hora": data_hora, "loja": loja,
         "menor_preco": min(precos), "preco_medio": mean(precos), "qtd": len(precos)}
        for (data_hora, loja), precos in sorted(grupos.items())
    ]
