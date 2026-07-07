# NutriAI — Ensinar IA a Trabalhar com Dados de uma API

Projeto educativo que demonstra como **alimentar um modelo de IA com dados reais de uma API externa**.

## O que este projeto ensina

1. **Consumir uma API externa** com `requests` e API Key
2. **Extrair dados do JSON** devolvido pela API
3. **Alimentar um modelo de IA simples** com esses dados
4. **Obter uma decisão** (score + classificação) a partir dos dados

## Como funciona

```
Utilizador descreve a refeição
       ↓
API Nutrition → devolve JSON com nutrientes
       ↓
Modelo IA (NutriAI) processa os dados
       ↓
Score 0-100 + classificação (Saudável / Moderado / Pouco Saudável)
```

### Fluxo de dados

```python
# 1. Chamar a API → JSON
dados = buscar_dados("rice and beans")
# Resultado: [{"name": "rice and beans", "fat_total_g": 3.8, "sodium_mg": 415, ...}]

# 2. Passar o JSON ao modelo
resultado = modelo.analisar(dados)
# Resultado: {"score": 70.4, "classificacao": "Saudável", ...}

# 3. Usar o resultado
print(f"Score: {resultado['score']}/100 → {resultado['classificacao']}")
```

## Estrutura

```
├── .env           # API_KEY da API Nutrition
├── ia.py          # Modelo de IA (NutriAI)
├── index.py       # Interface + chamada à API
└── README.md      # (este ficheiro)
```

## Como correr

```bash
pip install requests python-dotenv
```

Cria um ficheiro `.env` com:
```
API_KEY=a_tua_chave_aqui
```

Depois:
```bash
python3 index.py
```

## O modelo de IA (ia.py)

O `NutriAI` é propositadamente simples para ser didático:

- Cada nutriente tem um **peso** (positivo ou negativo)
- O score parte de 70 e é ajustado conforme os nutrientes
- Quanto mais fibra, melhor (peso +2.0). Quanto mais gordura saturada, pior (peso -0.6)

```python
self.pesos = {
    "gordura": -0.3,
    "saturada": -0.6,
    "sodio": -0.005,
    "colesterol": -0.04,
    "fibra": 2.0,
    "acucar": -0.4,
    "carboidratos": -0.1,
}
```

Podes ajustar estes pesos para mudar o comportamento do modelo — é essa a graça.

## API utilizada

[API-Ninjas Nutrition](https://api-ninjas.com/api/nutrition) — devolve dados nutricionais para alimentos em texto natural (ex: "1lb brisket and fries").

## Para ensinar alguém

Este projeto serve como exemplo concreto de:

- **Integração com APIs** — como chamar, como tratar erros, como extrair dados
- **Pré-processamento** — transformar JSON bruto em features para o modelo
- **Modelo de decisão** — usar regras/pesos para tomar decisões com base em dados
- **Separação de responsabilidades** — API (`index.py`) separada do modelo (`ia.py`)
