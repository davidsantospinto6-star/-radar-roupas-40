import json
import os
import requests
from urllib.parse import quote

MAX_PRICE = 40.00
MAX_SIZE = 12

QUERIES = [
    "camiseta esportiva adidas tamanho 12",
    "camiseta esportiva nike tamanho 12",
    "camiseta esportiva puma tamanho 12",
    "camiseta esportiva umbro tamanho 12",
    "camiseta esportiva fila tamanho 12",
    "short esportivo adidas tamanho 12",
    "short esportivo nike tamanho 12",
    "bermuda esportiva puma tamanho 12",
]

SEEN_FILE = "ofertas_enviadas.json"


def carregar_enviados():
    if not os.path.exists(SEEN_FILE):
        return set()

    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()


def salvar_enviados(enviados):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(enviados), f, ensure_ascii=False, indent=2)


def buscar(query):
    url = (
        "https://api.mercadolibre.com/sites/MLB/search"
        f"?q={quote(query)}&condition=new&price=0-40&limit=50"
    )

    resposta = requests.get(url, timeout=20)
    resposta.raise_for_status()

    return resposta.json().get("results", [])


def produto_valido(produto):
    preco = produto.get("price")

    if preco is None or float(preco) > MAX_PRICE:
        return False

    titulo = produto.get("title", "").lower()

    palavras_esportivas = [
        "camiseta", "camisa", "short", "bermuda",
        "calção", "calca", "calça"
    ]

    if not any(palavra in titulo for palavra in palavras_esportivas):
        return False

    return True


def main():
    enviados = carregar_enviados()
    novas_ofertas = []

    for query in QUERIES:
        try:
            produtos = buscar(query)

            for produto in produtos:
                if not produto_valido(produto):
                    continue

                item_id = produto.get("id")

                if not item_id or item_id in enviados:
                    continue

                oferta = {
                    "id": item_id,
                    "titulo": produto.get("title"),
                    "preco": produto.get("price"),
                    "link": produto.get("permalink"),
                }

                novas_ofertas.append(oferta)
                enviados.add(item_id)

        except Exception as erro:
            print(f"Erro na busca {query}: {erro}")

    salvar_enviados(enviados)

    print(f"Novas ofertas encontradas: {len(novas_ofertas)}")

    for oferta in novas_ofertas:
        print("\n🔥 OFERTA ENCONTRADA")
        print(f"👕 {oferta['titulo']}")
        print(f"💰 R$ {oferta['preco']:.2f}")
        print(f"🔗 {oferta['link']}")


if __name__ == "__main__":
    main()