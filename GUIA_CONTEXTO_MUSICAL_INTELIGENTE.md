# 🧠 Sistema de Contexto Musical Inteligente - Roxy Assistant

## 📋 Descripción General

El **Sistema de Contexto Musical Inteligente** es una implementación avanzada que analiza múltiples dimensiones del contexto del usuario para proporcionar selecciones musicales altamente personalizadas y contextualmente apropiadas.

## 🎯 Características Principales

### 1. **Análisis Multi-Dimensional de Contexto**
- **Detección de Estado de Ánimo**: Análisis avanzado usando keywords, LLM y patrones conversacionales
- **Inferencia de Actividad**: Detección automática de la actividad actual (trabajo, ejercicio, estudio, etc.)
- **Contexto Temporal**: Análisis de hora del día, día de la semana, estación
- **Situación Social**: Detección de contexto social (solo, con amigos, familia, etc.)
- **Análisis del Sistema**: Monitoreo de aplicaciones activas y recursos del sistema

### 2. **Recomendaciones Musicales Contextuales**
- Géneros musicales apropiados para el contexto
- Características de audio optimizadas (energía, valencia, tempo)
- Términos de búsqueda inteligentes
- Filtros de contenido adaptativos

### 3. **Integración con Sistema Existente**
- Compatible con `IntelligentMusicSelector`
- Integrado con historial conversacional
- Soporte para APIs de Spotify
- Cache inteligente para optimizar rendimiento

## 🏗️ Arquitectura del Sistema

```
MusicContextAnalyzer
├── Análisis de Mood
│   ├── Keywords directos
│   ├── Análisis con LLM (Ollama)
│   └── Patrones conversacionales
├── Inferencia de Actividad
│   ├── Patrones en input del usuario
│   ├── Aplicaciones activas del sistema
│   └── Heurísticas de comportamiento
├── Contexto Temporal
│   ├── Hora del día
│   ├── Día de la semana
│   ├── Estación del año
│   └── Clima (opcional)
├── Situación Social
│   ├── Indicadores en conversación
│   ├── Tamaño estimado del grupo
│   └── Nivel de formalidad
└── Recomendaciones Musicales
    ├── Géneros apropiados
    ├── Características de audio
    ├── Términos de búsqueda
    └── Filtros de contenido
```

## 📊 Estructuras de Datos

### `MoodAnalysis`
```python
@dataclass
class MoodAnalysis:
    primary_mood: str          # happy, sad, energetic, calm, etc.
    secondary_moods: List[str] # Moods secundarios
    confidence: float          # 0.0 - 1.0
    indicators: List[str]      # Evidencia que llevó a la conclusión
    energy_level: float        # 0.0 - 1.0
    valence: float            # 0.0 - 1.0 (negativo a positivo)
```

### `ActivityContext`
```python
@dataclass
class ActivityContext:
    primary_activity: str      # working, exercising, relaxing, etc.
    confidence: float          # Confianza en la detección
    indicators: List[str]      # Evidencia de la actividad
    activity_intensity: float # 0.0 - 1.0
    duration_estimate: int     # Duración estimada en minutos
    location_context: str      # home, office, gym, car, etc.
```

### `MusicContext`
```python
@dataclass
class MusicContext:
    mood: MoodAnalysis
    activity: ActivityContext
    temporal: TemporalContext
    social: SocialContext
    system: SystemContext
    overall_confidence: float
    context_summary: str
    music_recommendations: Dict[str, Any]
```

## 🚀 Uso del Sistema

### Inicialización Básica

```python
from music_context_analyzer import MusicContextAnalyzer

# Inicializar analizador
analyzer = MusicContextAnalyzer()

# Analizar contexto
user_input = "Pon música alegre para la fiesta con mis amigos"
conversation_history = [
    {"user": "Hola", "roxy": "¡Hola! ¿Cómo estás?"},
    {"user": user_input, "roxy": ""}
]

context = analyzer.analyze_music_context(user_input, conversation_history)
```

### Integración con Selector Inteligente

```python
from intelligent_music_selector import IntelligentMusicSelector

# El selector ahora usa automáticamente el análisis de contexto
selector = IntelligentMusicSelector()

# Selección con contexto avanzado
result = selector.select_music_intelligently(
    user_input="Música para estudiar", 
    context="general",
    conversation_history=conversation_history
)

# El resultado incluye información de contexto
context_info = result.get('context_analysis', {})
print(f"Mood detectado: {context_info.get('mood')}")
print(f"Actividad: {context_info.get('activity')}")
```

## 🎭 Detección de Estados de Ánimo

### Moods Soportados
- **happy**: Feliz, alegre, contento
- **sad**: Triste, melancólico, deprimido
- **energetic**: Energético, motivado, activo
- **calm**: Tranquilo, relajado, zen
- **focused**: Concentrado, estudiando, trabajando
- **romantic**: Romántico, íntimo, para citas
- **party**: Fiesta, celebración, social
- **nostalgic**: Nostálgico, recuerdos
- **angry**: Enojado, frustrado
- **anxious**: Ansioso, estresado, preocupado

### Métodos de Detección

1. **Keywords Directos**: Análisis de palabras clave en el input
2. **Análisis con LLM**: Uso de Ollama para análisis contextual profundo
3. **Patrones Conversacionales**: Análisis del historial de conversación
4. **Características de Audio**: Mapeo a energía y valencia

## 🏃 Inferencia de Actividades

### Actividades Detectadas
- **working**: Trabajo, oficina, reuniones
- **exercising**: Ejercicio, gym, deportes
- **studying**: Estudio, concentración, tareas
- **cooking**: Cocinar, preparar comida
- **driving**: Conducir, viajes en auto
- **cleaning**: Limpieza, organización
- **socializing**: Socialización, tiempo con amigos
- **relaxing**: Relajación, descanso
- **gaming**: Videojuegos, entretenimiento
- **reading**: Lectura, libros

### Métodos de Inferencia

1. **Patrones en Input**: Regex patterns para detectar actividades
2. **Aplicaciones Activas**: Análisis de procesos del sistema
3. **Heurísticas**: Reglas basadas en comportamiento típico

## 🕐 Contexto Temporal

### Períodos del Día
- **morning** (5:00 - 12:00): Música energizante, café, despertar
- **afternoon** (12:00 - 17:00): Música productiva, trabajo
- **evening** (17:00 - 21:00): Música sofisticada, cena
- **night** (21:00 - 5:00): Música ambient, relajante

### Consideraciones Adicionales
- **Fin de semana**: Ajuste de energía +10%
- **Estaciones**: Influencia en géneros y mood
- **Clima**: Integración opcional con APIs meteorológicas

## 👥 Contexto Social

### Situaciones Detectadas
- **alone**: Solo, música personal
- **with_friends**: Con amigos, música social
- **family**: En familia, música apropiada
- **party**: Fiesta, música bailable
- **work**: Trabajo, música de fondo
- **romantic**: Romántico, música íntima

### Ajustes por Situación
- **Volumen recomendado**
- **Contenido explícito** (evitar en contextos formales)
- **Géneros apropiados**
- **Nivel de energía**

## 🎵 Recomendaciones Musicales

### Características de Audio

```python
recommendations = {
    'genres': ['pop', 'rock', 'electronic'],
    'energy_range': [0.6, 0.9],      # Nivel de energía
    'valence_range': [0.7, 1.0],     # Positividad emocional
    'tempo_range': [120, 140],        # BPM
    'danceability_range': [0.5, 0.8], # Qué tan bailable
    'acousticness_range': [0.0, 0.3], # Nivel acústico
    'instrumentalness_range': [0.0, 0.2], # Instrumental vs vocal
    'search_terms': ['happy music', 'upbeat'],
    'avoid_explicit': False
}
```

### Mapeo Mood → Características

| Mood | Energía | Valencia | Géneros Típicos |
|------|---------|----------|-----------------|
| happy | 0.6-0.9 | 0.7-1.0 | pop, funk, disco |
| sad | 0.1-0.5 | 0.0-0.4 | indie, alternative, acoustic |
| energetic | 0.7-1.0 | 0.6-0.9 | electronic, rock, hip hop |
| calm | 0.1-0.4 | 0.4-0.8 | ambient, classical, chill |
| focused | 0.2-0.5 | 0.4-0.6 | instrumental, ambient, lo-fi |

## 🔧 Configuración y Personalización

### Variables de Entorno

```bash
# Opcional: API key para clima
WEATHER_API_KEY=your_openweather_api_key

# Configuración de Ollama (si está disponible)
OLLAMA_MODEL=llama3:latest
```

### Personalización de Keywords

```python
# Personalizar keywords de mood
analyzer.mood_keywords['custom_mood'] = ['keyword1', 'keyword2']

# Personalizar patrones de actividad
analyzer.activity_patterns['custom_activity'] = [r'\bpattern\b']
```

### Cache de Contexto

```python
# Configurar duración del cache (segundos)
analyzer.cache_duration = 600  # 10 minutos

# Limpiar cache manualmente
analyzer.context_cache.clear()
```

## 📈 Métricas y Confianza

### Cálculo de Confianza General

La confianza general se calcula como:
```python
def calculate_overall_confidence(confidences):
    avg_confidence = sum(confidences) / len(confidences)
    min_confidence = min(confidences)
    
    # Penalizar si alguna confianza es muy baja
    if min_confidence < 0.3:
        avg_confidence *= 0.7
    
    return min(0.95, avg_confidence)
```

### Niveles de Confianza

- **0.8 - 1.0**: Muy alta confianza, usar recomendaciones directamente
- **0.6 - 0.8**: Alta confianza, combinar con preferencias del usuario
- **0.4 - 0.6**: Confianza media, usar como guía con fallbacks
- **0.0 - 0.4**: Baja confianza, usar métodos tradicionales

## 🧪 Testing y Validación

### Demo Automático

```bash
python demo_contexto_musical_inteligente.py
# Seleccionar opción 1 para demo automático
```

### Demo Interactivo

```bash
python demo_contexto_musical_inteligente.py
# Seleccionar opción 2 para demo interactivo
```

### Casos de Prueba

El sistema incluye casos de prueba para:
- Diferentes estados de ánimo
- Variadas actividades
- Contextos sociales diversos
- Períodos temporales
- Combinaciones complejas

## 🔍 Debugging y Monitoreo

### Logs de Análisis

```python
# Habilitar logging detallado
import logging
logging.basicConfig(level=logging.DEBUG)

# Ver análisis paso a paso
context = analyzer.analyze_music_context(user_input, history)
summary = analyzer.get_context_summary_for_display(context)
print(json.dumps(summary, indent=2))
```

### Métricas de Rendimiento

```python
# Medir tiempo de análisis
import time
start = time.time()
context = analyzer.analyze_music_context(user_input)
analysis_time = time.time() - start
print(f"Tiempo de análisis: {analysis_time:.2f}s")
```

## 🚀 Optimizaciones y Mejoras Futuras

### Optimizaciones Implementadas
- **Cache inteligente**: Evita re-análisis innecesarios
- **Análisis paralelo**: Múltiples dimensiones simultáneamente
- **Fallbacks robustos**: Graceful degradation si falla algún componente

### Mejoras Futuras Sugeridas

1. **Integración con APIs de Clima**
   - OpenWeatherMap para influencia meteorológica
   - Ajustes estacionales automáticos

2. **Machine Learning Avanzado**
   - Modelos entrenados en preferencias del usuario
   - Aprendizaje continuo basado en feedback

3. **Análisis de Sentimientos Avanzado**
   - Modelos de NLP especializados en música
   - Análisis de emociones multi-label

4. **Integración con Dispositivos IoT**
   - Sensores de luz y sonido ambiente
   - Detección de actividad física

5. **Personalización Avanzada**
   - Perfiles de usuario múltiples
   - Preferencias contextuales dinámicas

## 📚 Referencias y Recursos

### APIs Utilizadas
- **Spotify Web API**: Para datos musicales y características de audio
- **Ollama**: Para análisis de contexto con LLM
- **psutil**: Para monitoreo del sistema

### Documentación Relacionada
- [Guía del Selector Inteligente de Música](GUIA_SELECTOR_INTELIGENTE_SPOTIFY.md)
- [Sistema de Memoria Conversacional](GUIA_MEMORIA_CONVERSACIONAL.md)
- [Detector Unificado de Comandos](unified_command_detector.py)

### Recursos Adicionales
- [Spotify Audio Features Documentation](https://developer.spotify.com/documentation/web-api/reference/get-audio-features)
- [Music Information Retrieval](https://musicinformationretrieval.com/)
- [Emotion Recognition in Music](https://arxiv.org/abs/1905.06947)

---

## 🤝 Contribución

Para contribuir al sistema:

1. **Fork** el repositorio
2. **Crea** una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. **Commit** tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. **Push** a la rama (`git push origin feature/nueva-funcionalidad`)
5. **Crea** un Pull Request

### Guidelines de Contribución

- Mantener compatibilidad con el sistema existente
- Incluir tests para nuevas funcionalidades
- Documentar cambios en este archivo
- Seguir el estilo de código existente
- Agregar logging apropiado para debugging

---

**Desarrollado por**: Roxy Assistant Team  
**Versión**: 1.0.0  
**Última actualización**: 2024

*Sistema de Contexto Musical Inteligente - Haciendo que la música se adapte perfectamente a tu momento* 🎵✨
