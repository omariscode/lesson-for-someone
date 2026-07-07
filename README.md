# NutriAI — IA a trabalhar com dados de uma API externa

Este projeto foi feito para **ensinar** como é que um modelo de IA pode consumir e trabalhar com dados vindos de uma API externa.

A ideia é pegar numa API de nutrição, pedir dados sobre uma refeição, e usar esses dados para alimentar um modelo de IA que avalia se a refeição é saudável ou não.

---

## O grande problema que vamos resolver

Imagina que queres criar uma app que diz se a comida que comes é saudável. Tu tens uma API que dá dados nutricionais, mas a API só devolve **JSON bruto** — números soltos sem contexto. Como é que transformas esses números numa **resposta útil** ("Saudável", "Moderado", "Pouco Saudável")?

**Resposta:** usas um modelo de IA (mesmo que simples) para processar esses números e tomar uma decisão.

---

## Arquitetura do projeto

```
┌──────────────────────────────────────────────────────────┐
│                         index.py                          │
│  (interface com o utilizador + chamada à API)            │
│                                                           │
│  1. Pede ao user o nome da refeição                      │
│  2. Chama a API Nutrition → recebe JSON                  │
│  3. Passa o JSON ao modelo (ia.py)                       │
│  4. Mostra o resultado                                   │
└─────────────────────┬────────────────────────────────────┘
                      │ dados da API (JSON)
                      ▼
┌──────────────────────────────────────────────────────────┐
│                         ia.py                              │
│  (modelo de IA)                                           │
│                                                           │
│  1. Recebe o JSON da API                                  │
│  2. Extrai os nutrientes de cada alimento                 │
│  3. Calcula a média dos nutrientes                        │
│  4. Aplica pesos a cada nutriente → score                │
│  5. Classifica o score → devolve resultado                │
└──────────────────────────────────────────────────────────┘
```

---

## Explicação passo a passo

### 1. O que a API devolve

Quando fazemos um pedido à API Nutrition com o texto `"rice and beans"`, ela devolve isto:

```json
[
  {
    "name": "rice and beans",
    "serving_size_g": 100.0,
    "fat_total_g": 3.8,
    "fat_saturated_g": 0.7,
    "sodium_mg": 415,
    "cholesterol_mg": 0,
    "carbohydrates_total_g": 24.3,
    "fiber_g": 3.4,
    "sugar_g": 0.9
  }
]
```

**Isto é uma lista de objetos (dicionários) Python.** Cada objeto representa um alimento. Cada alimento tem campos como `fat_total_g`, `sodium_mg`, `fiber_g`, etc.

> **Importante:** A API pode devolver vários alimentos se a query tiver mais que um. Ex: `"rice and beans and chicken"` devolve 2 ou 3 objetos na lista.

### 2. Como o modelo recebe e processa os dados

No `index.py`, depois de receber os dados da API, fazemos:

```python
dados = buscar_dados("rice and beans")   # → [{"name":"rice and beans", "fat_total_g":3.8, ...}]
resultado = modelo.analisar(dados)        # → chama o método analisar() da classe NutriAI
```

O método `analisar()` no `ia.py` faz o seguinte:

#### a) Verifica se os dados são válidos

```python
if not dados_api or not isinstance(dados_api, list):
    return None
```

Se a API devolver algo vazio ou inválido, não vale a pena continuar.

#### b) Extrai os nutrientes de cada alimento

Para cada objeto na lista, o modelo extrai os valores dos nutrientes:

```python
valor = item.get("fat_total_g", 0)   # procura o campo "fat_total_g" no JSON
```

Mapeamos os nomes dos campos da API (em inglês) para nomes mais simples (em português):

| Nome da API (JSON) | Nome no modelo | Descrição          |
|---------------------|----------------|--------------------|
| `fat_total_g`      | `gordura`      | Gordura total      |
| `fat_saturated_g`  | `saturada`     | Gordura saturada   |
| `sodium_mg`        | `sodio`        | Sódio              |
| `cholesterol_mg`   | `colesterol`   | Colesterol         |
| `fiber_g`          | `fibra`        | Fibra              |
| `sugar_g`          | `acucar`       | Açúcar             |
| `carbohydrates_total_g` | `carboidratos` | Hidratos de carbono |

#### c) Calcula a média dos nutrientes

Se houver mais que um alimento, calculamos a média aritmética de cada nutriente:

```python
for chave in nutrientes_medio:
    nutrientes_medio[chave] /= n   # n = número de alimentos
```

Isto garante que cada refeição é avaliada de forma justa, independentemente de ter 1 ou 5 alimentos.

#### d) Aplica os pesos — **aqui é onde a IA decide**

O modelo tem pesos definidos para cada nutriente:

```python
self.pesos = {
    "gordura": -0.3,      # quanto mais gordura, pior
    "saturada": -0.6,     # gordura saturada é pior que a normal
    "sodio": -0.005,      # sódio em excesso é mau
    "colesterol": -0.04,  # colesterol elevado é mau
    "fibra": 2.0,         # fibra é muito bom (peso positivo alto)
    "acucar": -0.4,       # açúcar é mau
    "carboidratos": -0.1, # hidratos em excesso são maus
}
```

O score começa em **70** (valor base neutro). Depois, para cada nutriente, fazemos:

```python
score = 70
for chave, valor in nutrientes_medio.items():
    score += peso_da_chave * valor
```

**Exemplo prático:**

Para `"rice and beans"`:
- `gordura` = 3.8 → 70 + (-0.3 × 3.8) = 70 - 1.14 = 68.86
- `saturada` = 0.7 → 68.86 + (-0.6 × 0.7) = 68.86 - 0.42 = 68.44
- `sodio` = 415 → 68.44 + (-0.005 × 415) = 68.44 - 2.08 = 66.36
- `colesterol` = 0 → sem alteração
- `fibra` = 3.4 → 66.36 + (2.0 × 3.4) = 66.36 + 6.80 = **73.16**
- `acucar` = 0.9 → 73.16 + (-0.4 × 0.9) = 73.16 - 0.36 = 72.80
- `carboidratos` = 24.3 → 72.80 + (-0.1 × 24.3) = 72.80 - 2.43 = **70.37**

Score final: **70.4 → "Saudável"** ✅

> **Nota:** O `max(0, min(100, score))` garante que o score está sempre entre 0 e 100.

#### e) Classifica o score

Depois de calcular o score, o modelo classifica:

| Score      | Classificação        |
|------------|----------------------|
| ≥ 70       | Saudável ✅          |
| ≥ 45       | Moderado ⚠️          |
| < 45       | Pouco Saudável ❌     |

#### f) Devolve o resultado

O modelo devolve um dicionário com tudo organizado:

```python
return {
    "alimentos": ["rice and beans"],
    "score": 70.4,
    "classificacao": "Saudável",
    "nutrientes_medio": {"gordura": 3.8, "saturada": 0.7, ...},
}
```

### 3. Como o `index.py` usa o resultado

```python
resultado = modelo.analisar(dados)

print(f"Score: {resultado['score']}/100 → {resultado['classificacao']}")
print(f"Alimentos: {', '.join(resultado['alimentos'])}")
```

---

## A parte mais importante para perceber

O modelo de IA **não é mágica**. É matemática simples:

1. **Entrada:** JSON com números (os nutrientes)
2. **Processamento:** Multiplicar cada número por um peso e somar
3. **Saída:** Um score final

O que torna isto "IA" é que o modelo **toma uma decisão baseada em dados** — e podes ajustar os pesos para afinar o comportamento. Se achas que a fibra devia valer ainda mais, aumentas o peso. Se achas que o açúcar devia penalizar mais, aumentas o peso negativo.

---

## Como correr

### 1. Instalar dependências

```bash
pip install requests python-dotenv
```

### 2. Criar `.env`

```
API_KEY=a_tua_chave_da_api_ninjas
```

Podes obter uma chave gratuita em [https://api-ninjas.com](https://api-ninjas.com).

### 3. Correr

```bash
python3 index.py
```

### Exemplo de sessão

```
=== NutriAI ===
Exemplos: 'rice and beans', '2 eggs and bacon', 'salad and grilled chicken'

O que comeste? (ou 'sair'): 2 eggs and bacon

Alimentos: eggs, bacon
Score: 49.3/100 → Moderado

Nutrientes (média por alimento):
  gordura: 17.0
  saturada: 6.0
  sodio: 437.5
  colesterol: 186.0
  fibra: 0.0
  acucar: 0.1
  carboidratos: 0.6
```

---

## Tabela de pesos (para experimentar)

Podes abrir o `ia.py` e alterar os pesos para ver como o comportamento muda:

| Nutriente      | Peso atual | O que acontece se aumentares |
|----------------|-----------|-------------------------------|
| `gordura`      | -0.3      | Penaliza mais alimentos gordos |
| `saturada`     | -0.6      | Penaliza ainda mais gorduras saturadas |
| `sodio`        | -0.005    | Penaliza mais comida salgada |
| `colesterol`   | -0.04     | Penaliza mais alimentos com colesterol |
| `fibra`        | +2.0      | Recompensa ainda mais alimentos ricos em fibra |
| `acucar`       | -0.4      | Penaliza mais alimentos açucarados |
| `carboidratos` | -0.1      | Penaliza mais hidratos |

Experimenta mudar e corre outra vez para veres a diferença.

---

## Para o professor / mentor

Este projeto foi pensado para explicar conceitos fundamentais:

### O que se aprende

| Conceito | Onde se vê no código |
|----------|----------------------|
| Consumir APIs REST | `index.py:buscar_dados()` — `requests.get()` com headers e API Key |
| JSON como formato de dados | A API devolve uma lista de dicionários Python |
| Extrair dados de JSON | `ia.py` — percorrer a lista com `for`, aceder a campos com `item.get("chave", 0)` |
| Pré-processamento | Calcular médias, normalizar, tratar erros de tipo |
| Modelo de decisão baseado em regras | Pesos lineares que transformam features num score |
| Separação de responsabilidades | `index.py` (IO) separado do `ia.py` (lógica) |
| CLI interativa | `input()` dentro de um `while True` |
| Variáveis de ambiente | `.env` com `python-dotenv` |

### Exercícios para dar a quem está a aprender

1. **Muda os pesos** — faz com que ovos com bacon passe a "Pouco Saudável"
2. **Adiciona um novo nutriente** — se a API devolver `protein_g`, adiciona ao modelo
3. **Muda os limiares** — faz com que "Saudável" seja ≥ 80 em vez de ≥ 70
4. **Adiciona sugestão** — se o score for < 45, imprime uma dica tipo "Tenta adicionar mais vegetais"
5. **Acumula refeições** — guarda o score de cada refeição e mostra a média no final
