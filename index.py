import requests
from dotenv import load_dotenv
import os
from ia import NutriAI

load_dotenv()

API_KEY = os.getenv("API_KEY")
URL = "https://api.api-ninjas.com/v1/nutrition"


def buscar_dados(alimento: str) -> list:
    """Chama a API e devolve a lista de alimentos com nutrientes."""
    resposta = requests.get(
        f"{URL}?query={alimento}",
        headers={"X-Api-Key": API_KEY},
    )
    return resposta.json() if resposta.status_code == 200 else []


def mostrar_resultado(resultado: dict):
    """Mostra o resultado de forma legível."""
    print(f"\nAlimentos: {', '.join(resultado['alimentos'])}")
    print(f"Score: {resultado['score']}/100 → {resultado['classificacao']}")
    print("\nNutrientes (média por alimento):")
    for chave, valor in resultado["nutrientes_medio"].items():
        print(f"  {chave}: {valor:.1f}")


def main():
    modelo = NutriAI()

    print("=== NutriAI ===")
    print("Exemplos: 'rice and beans', '2 eggs and bacon', 'salad and grilled chicken'\n")

    while True:
        entrada = input("O que comeste? (ou 'sair'): ").strip()
        if entrada.lower() == "sair":
            break

        dados = buscar_dados(entrada)
        if not dados:
            print("Não encontrei dados para essa refeição.")
            continue

        resultado = modelo.analisar(dados)
        mostrar_resultado(resultado)


if __name__ == "__main__":
    main()