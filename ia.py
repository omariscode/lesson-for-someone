class NutriAI:
    def __init__(self):
        self.pesos = {
            "gordura": -0.3,
            "saturada": -0.6,
            "sodio": -0.005,
            "colesterol": -0.04,
            "fibra": 2.0,
            "acucar": -0.4,
            "carboidratos": -0.1,
        }

    def analisar(self, dados_api):
        if not dados_api or not isinstance(dados_api, list):
            return None

        score_total = 0
        nutrientes_medio = {"gordura": 0, "saturada": 0, "sodio": 0,
                            "colesterol": 0, "fibra": 0, "acucar": 0, "carboidratos": 0}
        alimentos = []

        for item in dados_api:
            alimentos.append(item.get("name", "desconhecido"))
            for chave in nutrientes_medio:
                valor = item.get({
                    "gordura": "fat_total_g",
                    "saturada": "fat_saturated_g",
                    "sodio": "sodium_mg",
                    "colesterol": "cholesterol_mg",
                    "fibra": "fiber_g",
                    "acucar": "sugar_g",
                    "carboidratos": "carbohydrates_total_g",
                }[chave], 0)
                try:
                    nutrientes_medio[chave] += float(valor)
                except (ValueError, TypeError):
                    nutrientes_medio[chave] += 0

        n = len(dados_api)
        for chave in nutrientes_medio:
            nutrientes_medio[chave] /= n

        score = 70
        for chave, valor in nutrientes_medio.items():
            score += self.pesos[chave] * valor
        score = max(0, min(100, score))

        if score >= 70:
            classificacao = "Saudável"
        elif score >= 45:
            classificacao = "Moderado"
        else:
            classificacao = "Pouco Saudável"

        return {
            "alimentos": alimentos,
            "score": round(score, 1),
            "classificacao": classificacao,
            "nutrientes_medio": nutrientes_medio,
        }