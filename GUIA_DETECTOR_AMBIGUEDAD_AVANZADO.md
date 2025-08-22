# 🔍 DETECTOR DE AMBIGÜEDAD AVANZADO - GUÍA COMPLETA

## Descripción General

El **Detector de Ambigüedad Avanzado** es un sistema inteligente que identifica y maneja comandos confusos, incompletos o ambiguos en el asistente virtual Roxy. Proporciona análisis detallado, sugerencias de clarificación y resolución automática cuando es posible.

## 🎯 Características Principales

### 1. **Detección Multidimensional**
- **Múltiples interpretaciones**: Detecta cuando un comando puede referirse a varias aplicaciones o acciones
- **Comandos incompletos**: Identifica cuando falta información esencial
- **Referencias vagas**: Detecta pronombres o referencias sin antecedente claro
- **Conflictos históricos**: Analiza inconsistencias con comandos recientes
- **Baja confianza**: Identifica cuando el análisis inicial tiene poca certeza
- **Targets conflictivos**: Detecta múltiples objetivos posibles en un mismo comando

### 2. **Sistema de Puntuación Inteligente**
- Calcula un **score de ambigüedad** (0.0 - 1.0)
- Considera múltiples factores: severidad de señales, confianza original, contexto
- Ajusta automáticamente los umbrales según el tipo de ambigüedad

### 3. **Generación de Clarificaciones**
- Preguntas específicas y contextuales
- Sugerencias basadas en aplicaciones conocidas
- Alternativas ordenadas por probabilidad
- Máximo 5 preguntas para evitar saturación

### 4. **Resolución Automática**
- Tres modos de acción: `execute`, `suggest_alternatives`, `clarify`
- Resolución basada en selección numérica del usuario
- Re-análisis con contexto enriquecido
- Fallback inteligente a la opción más probable

## 🏗️ Arquitectura del Sistema

### Clases Principales

#### `AmbiguitySignal`
```python
@dataclass
class AmbiguitySignal:
    signal_type: str        # Tipo de ambigüedad detectada
    severity: float         # Severidad (0.0 - 1.0)
    description: str        # Descripción legible
    suggested_clarifications: List[str]  # Preguntas sugeridas
    context_data: Dict[str, Any]        # Datos adicionales
```

#### `AmbiguityAnalysis`
```python
@dataclass 
class AmbiguityAnalysis:
    has_ambiguity: bool                    # ¿Hay ambigüedad?
    ambiguity_score: float                 # Puntuación (0.0 - 1.0)
    signals: List[AmbiguitySignal]         # Señales detectadas
    primary_interpretations: List[Dict]    # Interpretaciones posibles
    confidence_factors: Dict[str, float]   # Factores de confianza
    recommended_action: str                # Acción recomendada
    clarification_questions: List[str]     # Preguntas generadas
```

#### `AmbiguityDetector`
Clase principal que implementa toda la lógica de detección y análisis.

## 🔧 Uso del Sistema

### Integración Básica

```python
from unified_command_detector import UnifiedCommandDetector

# El detector se inicializa automáticamente
detector = UnifiedCommandDetector()

# Analizar comando (incluye detección de ambigüedad)
result = detector.analyze_command("abre música")

# Verificar si hay ambigüedad
if result.action == "request_clarification":
    print("Ambigüedad detectada:")
    print(result.natural_response)
    
    # Obtener análisis detallado
    analysis = result.execution_data['ambiguity_analysis']
    print(f"Score: {analysis.ambiguity_score}")
    print(f"Señales: {len(analysis.signals)}")
```

### Resolución de Ambigüedad

```python
# Si el usuario responde a una clarificación
user_response = "me refiero a spotify"
original_analysis = result.execution_data['ambiguity_analysis']

# Resolver ambigüedad
resolved = detector.resolve_ambiguity(user_response, original_analysis)
print(f"Resuelto: {resolved.action} - {resolved.target}")
```

### Uso Independiente

```python
from unified_command_detector import AmbiguityDetector, CommandResult

# Crear detector independiente
ambiguity_detector = AmbiguityDetector()

# Crear resultado simulado
result = CommandResult(
    is_command=True,
    command_type="app",
    action="open_app",
    target="música",
    confidence=0.6,
    natural_response=None,
    execution_data={}
)

# Analizar ambigüedad
analysis = ambiguity_detector.analyze_ambiguity("abre música", result)

print(f"¿Ambiguo? {analysis.has_ambiguity}")
print(f"Score: {analysis.ambiguity_score}")
print(f"Acción: {analysis.recommended_action}")
```

## 📊 Tipos de Ambigüedad Detectados

### 1. **Múltiples Interpretaciones**
**Ejemplos:**
- "abre música" → Spotify, YouTube Music, VLC, Windows Media Player
- "busca video" → YouTube, Netflix, VLC
- "abre navegador" → Chrome, Firefox, Edge, Opera

**Detección:**
- Términos genéricos sin especificación
- Múltiples aplicaciones que coinciden con el patrón
- Similitud entre nombres de aplicaciones

### 2. **Comandos Incompletos**
**Ejemplos:**
- "abre" (sin especificar qué)
- "reproduce" (sin especificar qué música)
- "busca" (sin términos de búsqueda)

**Detección:**
- Comandos de una sola palabra que requieren objetivo
- Comandos muy cortos con baja confianza
- Verbos de acción sin complemento

### 3. **Referencias Vagas**
**Ejemplos:**
- "reproduce eso anterior"
- "abre lo mismo que antes"
- "busca algo de anime"

**Detección:**
- Pronombres demostrativos sin antecedente
- Referencias temporales sin contexto
- Términos indefinidos ("algo", "alguna")

### 4. **Falta de Contexto**
**Ejemplos:**
- "siguiente" (sin saber qué está reproduciéndose)
- "continúa" (sin estado de reproducción conocido)
- "el anterior" (sin historial disponible)

**Detección:**
- Comandos que dependen del estado actual
- Referencias a elementos previos sin historial
- Acciones contextuales sin información de contexto

### 5. **Baja Confianza**
**Ejemplos:**
- "xyz abc 123" (sin sentido)
- "haz algo" (extremadamente vago)
- Inputs con errores tipográficos graves

**Detección:**
- Confianza del análisis inicial < 0.7
- Comandos sin estructura reconocible
- Términos desconocidos o sin sentido

### 6. **Targets Conflictivos**
**Ejemplos:**
- "abre spotify y youtube" (múltiples aplicaciones)
- "busca netflix en disney plus" (plataformas conflictivas)

**Detección:**
- Múltiples nombres de aplicaciones en un comando
- Plataformas incompatibles mencionadas juntas
- Objetivos contradictorios

## ⚙️ Configuración y Personalización

### Umbrales Ajustables

```python
# En AmbiguityDetector.__init__()
self.confidence_threshold = 0.7  # Umbral mínimo de confianza
self.ambiguity_threshold = 0.4   # Umbral para considerar ambiguo
```

### Aplicaciones Conocidas

```python
# Personalizar categorías de aplicaciones
self.known_apps = {
    'music': ['spotify', 'youtube music', 'vlc', 'apple music'],
    'browsers': ['chrome', 'firefox', 'edge', 'brave'],
    'games': ['steam', 'epic games', 'origin', 'gog'],
    # ... más categorías
}
```

### Patrones de Ambigüedad

```python
# Agregar patrones personalizados
self.ambiguous_patterns = {
    'custom_pattern': [
        r'\b(tu_patrón_aquí)\b',
        r'otro_patrón_regex'
    ]
}
```

## 📈 Sistema de Puntuación

### Cálculo del Score de Ambigüedad

1. **Base**: Suma de severidades de señales / número de señales
2. **Penalización por confianza**: (1.0 - confianza_original) × 0.3
3. **Bonus por señales críticas**: número_señales_críticas × 0.1
4. **Score final**: min(1.0, base + penalización + bonus)

### Factores de Confianza

- **input_length**: Longitud óptima ~5 palabras
- **specificity**: Número de términos específicos (>4 caracteres)
- **context_availability**: Disponibilidad de contexto histórico
- **clarity**: Inverso del número de señales de ambigüedad
- **original_confidence**: Confianza del análisis inicial

## 🔄 Flujo de Procesamiento

1. **Análisis inicial** con Ollama/LLM
2. **Detección de ambigüedad** con múltiples verificaciones
3. **Cálculo de score** y determinación de acción
4. **Generación de respuesta** según el tipo de ambigüedad:
   - `execute`: Continuar con la interpretación original
   - `suggest_alternatives`: Mostrar opciones pero proceder
   - `clarify`: Solicitar clarificación del usuario
5. **Actualización de contexto** para futuros análisis

## 🧪 Casos de Prueba

El archivo `demo_ambiguity_detector.py` incluye casos de prueba organizados:

- **Múltiples interpretaciones**: 3 casos
- **Comandos incompletos**: 3 casos  
- **Referencias vagas**: 3 casos
- **Baja confianza**: 2 casos
- **Comandos claros**: 3 casos (control negativo)

## 📝 Registro y Aprendizaje

### Actualización de Contexto

```python
# Automático después de cada análisis
self.ambiguity_detector.update_context(user_input, result)
```

### Integración con Sistema de Aprendizaje

- Los fallos de ambigüedad se registran en `LearningSystem`
- Mejoras automáticas del prompt basadas en patrones
- Historial de comandos recientes para análisis contextual

## 🚀 Ejemplos Prácticos

### Ejemplo 1: Comando Ambiguo Simple

```
Usuario: "abre música"
Sistema: He detectado que tu comando podría tener múltiples interpretaciones:

¿Te refieres a Spotify?
¿Te refieres a YouTube Music?
¿Te refieres a VLC?

Usuario: "spotify"
Sistema: Perfecto, abriendo Spotify.
```

### Ejemplo 2: Comando Incompleto

```
Usuario: "reproduce"
Sistema: He detectado que tu comando podría tener múltiples interpretaciones:

¿Qué música o video quieres reproducir?

Usuario: "bad bunny"
Sistema: Entendido, buscando música de Bad Bunny en Spotify.
```

### Ejemplo 3: Referencia Vaga

```
Usuario: "reproduce eso anterior"
Sistema: He detectado que tu comando podría tener múltiples interpretaciones:

¿A qué te refieres específicamente?
¿Puedes ser más específico sobre lo que mencionas?

Usuario: "la canción de bad bunny que escuchamos ayer"
Sistema: Entendido, buscando música de Bad Bunny.
```

## 🔧 Solución de Problemas

### Problema: Muchas falsas alarmas
**Solución**: Ajustar `ambiguity_threshold` a un valor más alto (ej: 0.6)

### Problema: No detecta ambigüedades obvias
**Solución**: Reducir `confidence_threshold` o agregar patrones específicos

### Problema: Preguntas de clarificación confusas
**Solución**: Personalizar `suggested_clarifications` en los métodos de detección

### Problema: Resolución lenta
**Solución**: Limitar el número de interpretaciones alternativas generadas

## 📚 Referencias y Recursos

- **Archivo principal**: `unified_command_detector.py`
- **Demo**: `demo_ambiguity_detector.py`
- **Casos de prueba**: Incluidos en el demo
- **Integración**: Automática en `UnifiedCommandDetector`

## 🤝 Contribuciones

Para extender el sistema:

1. **Agregar nuevos tipos de señales**: Implementar métodos `_detect_*`
2. **Personalizar respuestas**: Modificar `_generate_clarification_questions`
3. **Mejorar resolución**: Extender `resolve_ambiguity`
4. **Agregar contexto**: Enriquecer `ambiguity_context` en el análisis principal

---

**¡El Detector de Ambigüedad Avanzado está listo para hacer que Roxy sea más inteligente y conversacional!** 🎉
