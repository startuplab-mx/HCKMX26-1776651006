# NAHUAL — Dataset Auto-Alimentación + Capa Estadística
## Correr 90 minutos sin pausa. Dos tracks en paralelo.

---

## TRACK 1: AUTO-ALIMENTACIÓN DEL DATASET (90 min continuo)

### Objetivo
Expandir el dataset de 870 a 1200+ patrones buscando en internet, validando cada patrón contra el clasificador en producción (http://159.223.187.6/analyze), y registrando solo los que aporten valor real.

### Metodología de búsqueda por rondas

**Ronda 1 (0-20 min): Perspectiva víctima — el gap más grande**

Buscar testimonios reales de menores reclutados. Queries:
```
"me ofrecieron trabajo" redes sociales menor México
"me amenazaron" WhatsApp menor
"me pidieron fotos" Instagram amenaza México
testimonio menor reclutado cartel México 2025 2026
"me contactaron por TikTok" crimen
"me dijeron que si no" amenaza menor
víctima reclutamiento digital México testimonio
```

Por cada frase encontrada:
1. Extraer la frase EXACTA del testimonio
2. Clasificarla en fase (1-4)
3. Probar contra http://159.223.187.6/analyze
4. Si da SEGURO cuando debería dar ATENCIÓN/PELIGRO → agregar como patrón nuevo
5. Si ya da ATENCIÓN/PELIGRO → skip (ya está cubierto)
6. Registrar en CSV con: id, fase, señal_base, variantes, intención, fuente, tipo, peso, url, confiabilidad

**Ronda 2 (20-40 min): Jerga juvenil MX 2025-2026**

Buscar cómo hablan los adolescentes mexicanos actualmente:
```
jerga juvenil México 2025 2026 slang
"cómo hablan los jóvenes" México redes sociales
slang narco TikTok México 2025
códigos secretos adolescentes México
"lenguaje de los jóvenes" México digital
abreviaciones chat WhatsApp México jóvenes
```

Objetivo: encontrar variantes de patrones existentes en jerga actual que no matchean:
- "jalar" = trabajar para el narco → ¿"darle al jale"? ¿"entrarle"? ¿"meterle"?
- "lana" = dinero → ¿"baro"? ¿"morralla"? ¿"varo"? ¿"billete"?
- Abreviaciones: "ntp" = no te preocupes, "nmms" = no mames, "alv" = a la verga

**Ronda 3 (40-55 min): Sextorsión — frases de chantaje**

Buscar patrones específicos de sextorsión que los testers reportaron pero que no matchean:
```
sextorsión frases amenaza México 2025
"voy a publicar tus fotos" chantaje
"mándame fotos o" amenaza
extorsión sexual menores frases México
grooming frases predador español
catfishing menores México frases
```

Frases a cubrir que testers reportaron y no matchearon:
- "si no me mandas fotos voy a publicar las que ya tengo"
- "tengo screenshots de todo lo que me mandaste"
- "le voy a mandar todo a tu mamá/escuela/amigos"
- "te hice un deepfake y lo voy a subir"

**Ronda 4 (55-70 min): Gaming y plataformas emergentes**

```
reclutamiento Roblox México menores
grooming Fortnite Free Fire Discord
"me contactaron en Roblox" amenaza
gaming reclutamiento criminal adolescentes
predadores Discord gaming menores
```

**Ronda 5 (70-85 min): Validación cruzada masiva**

Tomar los 50 mensajes más comunes que un adolescente mexicano podría enviar al bot y verificar que no dan falsos positivos:
```
Mensajes que DEBEN dar SEGURO:
- "hola qué onda"
- "me pelee con mi novia"
- "no me gusta la escuela"
- "quiero dinero para comprar un juego"
- "mi mamá no me deja salir"
- "estoy aburrido"
- "quién gana en un pelea, naruto o goku"
- "me ganaron en free fire"
- "tengo un chorro de tarea"
- "me reprobaron en mate"
```

Probar cada uno contra http://159.223.187.6/analyze y documentar cualquier falso positivo.

### Formato de registro

Archivo: `scripts/dataset_self_feed_results.csv`

```csv
id,fase,señal_base,variantes,intención,fuente,tipo,peso,url_fuente,confiabilidad,validated_score,validated_level,should_be,gap_type
```

Donde:
- validated_score: score que dio el clasificador actual
- validated_level: nivel que dio (SEGURO/ATENCIÓN/PELIGRO)
- should_be: nivel correcto
- gap_type: "false_negative" | "false_positive" | "correct" | "needs_llm"

### Reglas de validación directa

Para CADA patrón nuevo:
1. POST al clasificador en producción
2. Si el resultado es correcto → registrar como "correct", no agregar al dataset (ya funciona)
3. Si es falso negativo → agregar al dataset con peso basado en qué tan peligroso es
4. Si es falso positivo → agregar a whitelist
5. Cada 20 patrones, imprimir estadísticas de gaps encontrados

---

## TRACK 2: CAPA ESTADÍSTICA / ML

### Diseño: Procesador Bayesiano Ligero (sin GPU, sin entrenamiento pesado)

En lugar de un modelo ML completo (que requiere datos de entrenamiento que no tenemos en suficiente cantidad), implementar un **clasificador Bayesiano Naive** que aprende de la interacción en tiempo real. Esto complementa el heurístico y el LLM sin reemplazarlos.

### Arquitectura: 4 capas ahora

```
TEXTO
  │
  ├── Capa 1: Heurístico (regex, determinista, 870 patrones)
  │
  ├── Capa 1.5: Bayesiano (probabilístico, aprende de feedback)
  │
  ├── Capa 2: LLM (Claude API, zona gris + score=0 con keywords)
  │
  └── Capa 3: Escalamiento (trayectoria por sesión)
```

### Implementación: backend/classifier/bayesian.py

```python
"""
backend/classifier/bayesian.py
Clasificador Bayesiano Naive para detección de reclutamiento.

No requiere GPU ni entrenamiento previo. Aprende incrementalmente
de cada análisis confirmado (feedback confirm/deny).

Complementa al heurístico — no lo reemplaza.
El score final es un merge ponderado de ambos.
"""

import math
import json
import os
import re
from collections import defaultdict
from typing import Optional

class NaiveBayesClassifier:
    """
    Bayesiano Naive adaptado para detección de reclutamiento.
    
    Características:
    - Aprende de feedback (confirm/deny) sin reentrenamiento batch
    - Usa n-gramas (1,2,3) como features en lugar de bag-of-words
    - Prior informado: usa la distribución de las 4 fases como prior
    - Smoothing Laplace para evitar probabilidad 0
    - Persistencia en JSON para sobrevivir reinicios
    """
    
    CLASSES = ['seguro', 'captacion', 'enganche', 'coercion', 'explotacion']
    SMOOTHING = 1.0  # Laplace smoothing
    
    def __init__(self, model_path: str = "classifier/bayesian_model.json"):
        self.model_path = model_path
        
        # Contadores: class → {feature: count}
        self.feature_counts: dict[str, dict[str, int]] = {c: defaultdict(int) for c in self.CLASSES}
        
        # Contadores por clase
        self.class_counts: dict[str, int] = {c: 0 for c in self.CLASSES}
        
        # Total de documentos
        self.total_docs = 0
        
        # Vocabulario
        self.vocab: set[str] = set()
        
        # Cargar modelo persistido si existe
        self._load()
    
    def _tokenize(self, text: str) -> list[str]:
        """Extrae n-gramas (1,2,3) del texto normalizado."""
        # Normalizar
        text = text.lower().strip()
        text = re.sub(r'[^\w\sáéíóúñü]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        words = text.split()
        
        features = []
        # Unigramas
        features.extend(words)
        # Bigramas
        features.extend([f"{words[i]}_{words[i+1]}" for i in range(len(words)-1)])
        # Trigramas
        features.extend([f"{words[i]}_{words[i+1]}_{words[i+2]}" for i in range(len(words)-2)])
        
        return features
    
    def train_one(self, text: str, label: str):
        """Entrenamiento incremental con un solo ejemplo."""
        if label not in self.CLASSES:
            return
        
        features = self._tokenize(text)
        self.class_counts[label] += 1
        self.total_docs += 1
        
        for f in features:
            self.feature_counts[label][f] += 1
            self.vocab.add(f)
        
        # Auto-persistir cada 10 entrenamientos
        if self.total_docs % 10 == 0:
            self._save()
    
    def predict(self, text: str) -> dict:
        """
        Predice la clase más probable y retorna probabilidades por clase.
        Retorna: {
            "predicted_class": "coercion",
            "confidence": 0.87,
            "probabilities": {"seguro": 0.05, "captacion": 0.03, ...},
            "risk_score": 0.82  # Mapped to 0-1
        }
        """
        if self.total_docs < 5:
            # No hay suficientes datos para predecir
            return {
                "predicted_class": None,
                "confidence": 0.0,
                "probabilities": {},
                "risk_score": None,
                "insufficient_data": True
            }
        
        features = self._tokenize(text)
        vocab_size = len(self.vocab) or 1
        
        log_probs = {}
        for cls in self.CLASSES:
            # Prior: P(class) con Laplace
            log_prior = math.log((self.class_counts[cls] + self.SMOOTHING) / 
                                 (self.total_docs + self.SMOOTHING * len(self.CLASSES)))
            
            # Likelihood: P(features | class)
            total_features_in_class = sum(self.feature_counts[cls].values())
            log_likelihood = 0.0
            
            for f in features:
                count = self.feature_counts[cls].get(f, 0)
                log_likelihood += math.log((count + self.SMOOTHING) / 
                                          (total_features_in_class + self.SMOOTHING * vocab_size))
            
            log_probs[cls] = log_prior + log_likelihood
        
        # Normalizar a probabilidades (log-sum-exp trick)
        max_log = max(log_probs.values())
        exp_probs = {cls: math.exp(lp - max_log) for cls, lp in log_probs.items()}
        total_exp = sum(exp_probs.values())
        probs = {cls: ep / total_exp for cls, ep in exp_probs.items()}
        
        # Clase predicha
        predicted = max(probs, key=probs.get)
        confidence = probs[predicted]
        
        # Mapear a risk_score (0-1)
        # seguro = 0, captación = 0.3, enganche = 0.5, coerción = 0.8, explotación = 0.9
        risk_map = {'seguro': 0.0, 'captacion': 0.3, 'enganche': 0.5, 'coercion': 0.8, 'explotacion': 0.9}
        risk_score = sum(probs[cls] * risk_map[cls] for cls in self.CLASSES)
        
        return {
            "predicted_class": predicted,
            "confidence": round(confidence, 3),
            "probabilities": {k: round(v, 3) for k, v in probs.items()},
            "risk_score": round(risk_score, 3),
            "insufficient_data": False
        }
    
    def _save(self):
        """Persistir modelo a JSON."""
        data = {
            "total_docs": self.total_docs,
            "class_counts": dict(self.class_counts),
            "feature_counts": {cls: dict(counts) for cls, counts in self.feature_counts.items()},
            "vocab_size": len(self.vocab)
        }
        try:
            os.makedirs(os.path.dirname(self.model_path) or '.', exist_ok=True)
            with open(self.model_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception:
            pass
    
    def _load(self):
        """Cargar modelo de JSON si existe."""
        if not os.path.exists(self.model_path):
            return
        try:
            with open(self.model_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.total_docs = data.get("total_docs", 0)
            self.class_counts = data.get("class_counts", {c: 0 for c in self.CLASSES})
            for cls in self.CLASSES:
                if cls in data.get("feature_counts", {}):
                    self.feature_counts[cls] = defaultdict(int, data["feature_counts"][cls])
            self.vocab = set()
            for counts in self.feature_counts.values():
                self.vocab.update(counts.keys())
        except Exception:
            pass
    
    def get_stats(self) -> dict:
        """Estadísticas del modelo."""
        return {
            "total_training_examples": self.total_docs,
            "class_distribution": dict(self.class_counts),
            "vocabulary_size": len(self.vocab),
            "top_features_per_class": {
                cls: sorted(counts.items(), key=lambda x: -x[1])[:10]
                for cls, counts in self.feature_counts.items()
                if counts
            }
        }
```

### Integración en pipeline.py

```python
# En pipeline.py

from classifier.bayesian import NaiveBayesClassifier

class Pipeline:
    def __init__(self, ...):
        ...
        self.bayesian = NaiveBayesClassifier()
    
    def analyze(self, text, session_id=None):
        # Capa 1: Heurístico
        h_result = self.heuristic.classify(text)
        
        # Capa 1.5: Bayesiano (si tiene datos suficientes)
        b_result = self.bayesian.predict(text)
        
        # Capa 2: LLM (si aplica)
        ...
        
        # Merge: Heurístico 50% + Bayesiano 20% + LLM 30% (cuando todos activos)
        # Si bayesiano no tiene datos: Heurístico 60% + LLM 40%
        # Si LLM no activo: Heurístico 70% + Bayesiano 30%
        
        if not b_result.get("insufficient_data") and b_result["risk_score"] is not None:
            # Bayesiano aporta
            if llm_used:
                final = heuristic_score * 0.50 + b_result["risk_score"] * 0.20 + llm_score * 0.30
            else:
                final = heuristic_score * 0.70 + b_result["risk_score"] * 0.30
            
            result["bayesian"] = {
                "risk_score": b_result["risk_score"],
                "predicted_class": b_result["predicted_class"],
                "confidence": b_result["confidence"]
            }
        
        return result
```

### Alimentación del Bayesiano

El Bayesiano se entrena AUTOMÁTICAMENTE de dos fuentes:

**Fuente 1: Feedback del usuario (ya existe)**
```python
# Cuando el usuario confirma (da teléfono del tutor):
bayesian.train_one(text, dominant_phase)  # Ejemplo positivo

# Cuando el usuario niega ("no es", "falso"):
bayesian.train_one(text, "seguro")  # Ejemplo negativo
```

**Fuente 2: Pre-entrenamiento con el dataset existente**
```python
# Script de bootstrap: entrenar con los 870 patrones del dataset
# scripts/bootstrap_bayesian.py

import json
from classifier.bayesian import NaiveBayesClassifier

bayes = NaiveBayesClassifier()

phase_map = {
    'phase1_captacion': 'captacion',
    'phase2_enganche': 'enganche', 
    'phase3_coercion': 'coercion',
    'phase4_explotacion': 'explotacion'
}

for filename, label in phase_map.items():
    with open(f'classifier/keywords/{filename}.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    for pattern in data['patterns']:
        signal = pattern.get('signal_base', pattern.get('pattern', ''))
        if signal and len(signal) > 5:
            bayes.train_one(signal, label)

# También entrenar con whitelist como "seguro"
whitelist_phrases = [
    "estoy trabajando ahorita", "vienes al cumple", "me fue bien en el examen",
    "vi la serie de narcos", "quiero comprar un juego", "hola qué onda",
    "me pelee con mi novia", "tengo mucha tarea", "me ganaron en fortnite",
    # ... agregar más frases inocuas
]
for phrase in whitelist_phrases:
    bayes.train_one(phrase, "seguro")

bayes._save()
print(f"Bayesiano bootstrapped: {bayes.total_docs} ejemplos, vocab={len(bayes.vocab)}")
```

### Endpoints nuevos

```python
@app.get("/bayesian/stats")
async def bayesian_stats():
    """Estadísticas del modelo bayesiano."""
    return app.state.pipeline.bayesian.get_stats()

@app.post("/bayesian/predict")
async def bayesian_predict(request: AnalyzeRequest):
    """Predicción bayesiana pura (para debug/comparación)."""
    return app.state.pipeline.bayesian.predict(request.text)
```

### Por qué Bayesiano y no algo más pesado

| Opción | Requiere | Ventaja | Problema para hackathon |
|--------|----------|---------|------------------------|
| **Naive Bayes** | 0 deps, 0 GPU, JSON file | Aprende en runtime, explicable, <1ms | Accuracy limitada sin muchos datos |
| Random Forest | scikit-learn | Más preciso con features manuales | Necesita batch retraining |
| BERT/DistilBERT | torch, GPU, >1GB RAM | Comprensión semántica real | 1GB RAM en el droplet, sin GPU |
| TF-IDF + SVM | scikit-learn | Buen balance precision/recall | Batch retraining, no incremental |
| FastText | fasttext lib | Rápido, embeddings | Necesita corpus pre-entrenado en español MX |

Naive Bayes es la opción correcta para el hackathon porque:
- 0 dependencias nuevas (puro Python stdlib)
- Entrenamiento incremental (cada feedback lo mejora)
- Funciona con pocos datos (el prior informado compensa)
- <1ms de inferencia (no agrega latencia)
- Persistencia trivial (JSON file)
- Explicable (puedes ver las top features por clase)
- Complementa sin reemplazar — si el Bayesiano no tiene datos suficientes, no afecta el score

El pitch: "Nuestro clasificador tiene 3 capas cognitivas: regex determinista que detecta patrones conocidos, un modelo bayesiano que aprende de cada interacción real, y un LLM que entiende contexto cuando las otras capas no son concluyentes. La capa bayesiana mejora con cada usuario que confirma o niega un resultado — es un sistema que se vuelve más inteligente con el uso."

---

## PROMPT PARA CLAUDE CODE

```
Lee CLAUDE.md. Este prompt tiene 2 tracks que ejecutas en paralelo por 90 minutos.

TRACK 1: AUTO-ALIMENTACIÓN DEL DATASET
Busca en internet patrones de reclutamiento criminal de menores en México.
Por cada patrón encontrado, valida contra http://159.223.187.6/analyze.
Si da SEGURO cuando debería dar ATENCIÓN/PELIGRO (falso negativo), agrégalo al dataset.
Si ya da resultado correcto, skip.
Registra todo en scripts/dataset_self_feed_results.csv.
Foco: perspectiva víctima, jerga juvenil MX 2025, sextorsión, gaming.
Meta: encontrar 100+ gaps y agregar 50+ patrones nuevos validados.

TRACK 2: CAPA BAYESIANA
1. Crear backend/classifier/bayesian.py con NaiveBayesClassifier
   - Naive Bayes con n-gramas (1,2,3)
   - Entrenamiento incremental (train_one)
   - Persistencia en JSON
   - Smoothing Laplace
   - Mapeo a risk_score 0-1
2. Crear scripts/bootstrap_bayesian.py que entrene con los 870 patrones existentes + 50 frases inocuas
3. Integrar en pipeline.py como Capa 1.5: merge heurístico 50% + bayesiano 20% + LLM 30%
4. Si bayesiano tiene insufficient_data, ignorar y usar merge normal
5. Alimentar bayesiano desde feedback (confirm → train con fase, deny → train como "seguro")
6. Agregar endpoints: GET /bayesian/stats, POST /bayesian/predict
7. Correr bootstrap, verificar que predict funciona
8. Tests: bayesiano con datos insuficientes no afecta score, bayesiano entrenado aporta al merge
9. Deploy al droplet

Al terminar los 90 minutos, reportar:
- Patrones nuevos encontrados y validados
- Gaps de falsos negativos descubiertos
- Falsos positivos descubiertos
- Estadísticas del modelo bayesiano (vocab size, class distribution, top features)
- Score comparison: heurístico solo vs heurístico+bayesiano en 20 test cases
```
