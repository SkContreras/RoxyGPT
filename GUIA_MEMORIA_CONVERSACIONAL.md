# 🧠 Sistema de Memoria Conversacional Persistente - Roxy Megurdy

## 📋 Descripción General

El Sistema de Memoria Conversacional Persistente es una funcionalidad avanzada que permite a Roxy aprender de las interacciones con el usuario, mantener contexto entre sesiones y mejorar las respuestas con el tiempo.

## ✨ Características Principales

### 🧠 Memoria Persistente
- **Historial de conversación**: Mantiene registro de todas las interacciones
- **Preferencias del usuario**: Aprende y recuerda gustos y hábitos
- **Comandos fallidos**: Rastrea y aprende de errores para evitarlos
- **Contexto temporal**: Considera el tiempo y patrones de uso

### 💡 Aprendizaje Inteligente
- **Preferencias musicales**: Artistas, géneros, plataformas favoritas
- **Aplicaciones frecuentes**: Apps más usadas y preferidas
- **Patrones temporales**: Comandos típicos por hora del día
- **Continuidad conversacional**: Mantiene contexto entre mensajes

### 🔧 Mejoras Automáticas
- **Comandos genéricos mejorados**: "pon música" → "pon música de Bad Bunny"
- **Plataformas sugeridas**: Selección automática basada en preferencias
- **Advertencias de fallos**: Alerta sobre comandos que suelen fallar
- **Targets inteligentes**: Completa información faltante

## 🚀 Implementación

### Archivos Principales

#### `conversation_memory.py`
Núcleo del sistema de memoria con las siguientes clases:

```python
class ConversationMemory:
    """Sistema principal de memoria conversacional"""
    
    def __init__(self, memory_file="conversation_memory.json"):
        # Inicializa estructuras de memoria
        self.conversation_history = deque(maxlen=1000)
        self.user_preferences = {}
        self.recent_actions = deque(maxlen=50)
        self.failed_commands = []
```

#### Estructuras de Datos

```python
@dataclass
class ConversationEntry:
    """Entrada individual de conversación"""
    timestamp: float
    user_input: str
    command_result: Dict[str, Any]
    response: str
    success: bool
    context: Dict[str, Any]

@dataclass  
class UserPreference:
    """Preferencia del usuario"""
    category: str  # 'music', 'app', 'content'
    preference_type: str  # 'artist', 'genre', 'platform'
    value: str
    frequency: int
    last_used: float
    confidence: float
```

### Integración con UnifiedCommandDetector

El detector de comandos ha sido mejorado para usar la memoria:

```python
class UnifiedCommandDetector:
    def __init__(self, grok_callback=None):
        # Inicializar memoria conversacional
        if CONVERSATION_MEMORY_AVAILABLE:
            self.conversation_memory = ConversationMemory()
    
    def analyze_command(self, user_input: str) -> CommandResult:
        # 1. Obtener contexto de memoria
        memory_context = self.conversation_memory.analyze_command_with_context(user_input)
        
        # 2. Mejorar input con preferencias
        enhanced_input = self._enhance_input_with_memory(user_input, memory_context)
        
        # 3. Analizar con Ollama
        result = self._analyze_with_ollama_priority(enhanced_input, memory_context)
        
        # 4. Aplicar mejoras basadas en memoria
        result = self._apply_memory_improvements(result, memory_context)
        
        # 5. Guardar en memoria
        self._save_to_memory(user_input, result, True)
        
        return result
```

## 📊 Funcionalidades Detalladas

### 1. Aprendizaje de Preferencias

#### Preferencias Musicales
```python
# Usuario dice: "pon música de bad bunny"
# Sistema aprende:
{
    'music_artist:bad bunny': UserPreference(
        category='music',
        preference_type='artist', 
        value='bad bunny',
        frequency=1,
        confidence=0.5
    )
}

# Después de varios usos:
# Usuario dice solo: "pon música"
# Sistema mejora a: "pon música de bad bunny"
```

#### Preferencias de Aplicaciones
```python
# Usuario frecuentemente: "abre spotify"
# Sistema aprende que Spotify es la app favorita
# Próxima vez: "abre mi app de música" → "abre spotify"
```

### 2. Contexto Conversacional

#### Continuación de Conversación
```python
# Conversación:
# Usuario: "pon música de bad bunny"
# Usuario: "pon otra" (dentro de 5 minutos)
# Sistema: Detecta continuación y mantiene contexto de "bad bunny"
```

#### Detección de Patrones Temporales
```python
# Sistema aprende que a las 9:00 AM usuario suele pedir música
# A las 9:00 AM: "pon algo" → Sugiere música automáticamente
```

### 3. Manejo de Fallos

#### Prevención de Comandos Fallidos
```python
# Si "abre steam" ha fallado 3 veces:
# Usuario: "abre steam"
# Sistema: ⚠️ Advertencia: comando similar falló 3 veces
# Reduce confianza y sugiere alternativas
```

## 🎯 Casos de Uso

### Ejemplo 1: Primera Sesión
```
Usuario: "pon música de bad bunny"
Sistema: Buscando música de Bad Bunny
[Aprende: music_artist:bad bunny]

Usuario: "abre spotify"  
Sistema: Abriendo Spotify
[Aprende: app:spotify]
```

### Ejemplo 2: Sesión Posterior
```
Usuario: "pon música"
Sistema: [Consulta memoria] → "pon música de bad bunny"
Respuesta: "Buscando música de Bad Bunny (tu favorito)"

Usuario: "abre mi app de música"
Sistema: [Consulta memoria] → "abre spotify" 
Respuesta: "Abriendo Spotify"
```

### Ejemplo 3: Contexto Conversacional
```
Usuario: "pon música de bad bunny"
Sistema: Reproduciendo Bad Bunny

Usuario: "pon otra"
Sistema: [Detecta continuación] → "pon otra de bad bunny"
Respuesta: "Más música de Bad Bunny"
```

## 📈 Análisis y Estadísticas

### Obtener Estadísticas
```python
detector = UnifiedCommandDetector()
stats = detector.get_memory_stats()

print(f"Conversaciones: {stats['conversation_entries']}")
print(f"Preferencias: {stats['user_preferences']}")
print(f"Comandos fallidos: {stats['failed_commands']}")
```

### Preferencias por Categoría
```python
# Preferencias musicales
music_prefs = detector.get_user_preferences('music')
for key, pref in music_prefs.items():
    print(f"{pref['value']}: {pref['frequency']} usos")

# Aplicaciones favoritas  
app_prefs = detector.get_user_preferences('app')
```

### Contexto Reciente
```python
context = detector.get_conversation_context(5)  # Últimas 5 conversaciones
for entry in context:
    print(f"{entry['user_input']} → {entry['action']}")
```

## 🔧 Configuración y Personalización

### Archivo de Memoria
- **Ubicación**: `conversation_memory.json`
- **Formato**: JSON con todas las estructuras de memoria
- **Persistencia**: Automática después de cada interacción

### Parámetros Configurables
```python
memory = ConversationMemory(
    memory_file="custom_memory.json",  # Archivo personalizado
    max_history=1000                   # Máximo de entradas
)
```

### Limpieza de Datos Antiguos
```python
# Limpiar datos de más de 30 días
memory.clear_old_data(days=30)
```

## 🚀 Uso en Producción

### Inicialización
```python
from unified_command_detector import UnifiedCommandDetector

# Crear detector con memoria
detector = UnifiedCommandDetector()

# Verificar que la memoria esté disponible
if detector.conversation_memory:
    print("✅ Memoria conversacional activa")
else:
    print("❌ Memoria no disponible")
```

### Flujo Típico
```python
# 1. Analizar comando con memoria
user_input = "pon música"
result = detector.analyze_command(user_input)

# 2. Ejecutar comando (actualiza memoria automáticamente)
success = detector.execute_command(result)

# 3. La memoria se actualiza automáticamente con el resultado
```

## 🧪 Pruebas y Demostración

### Demo Completo
```bash
python demo_conversation_memory.py
```

Este script demuestra:
- ✅ Aprendizaje de preferencias
- ✅ Mejora de comandos genéricos  
- ✅ Contexto conversacional
- ✅ Estadísticas de memoria
- ✅ Persistencia entre sesiones

### Casos de Prueba
```python
# Probar aprendizaje
detector.analyze_command("pon música de bad bunny")  # Aprende preferencia
detector.analyze_command("pon música")               # Usa preferencia

# Probar contexto
detector.analyze_command("abre spotify")             # Comando base
detector.analyze_command("abre otra app")            # Continuación
```

## 📝 Logs y Debugging

### Mensajes de Sistema
```
🧠 Sistema de memoria conversacional activado
🔍 Analizando: 'pon música'
🧠 Contexto de memoria obtenido: 4 elementos  
✨ Input mejorado: 'pon música' → 'pon música de bad bunny'
🎯 Target mejorado con preferencia: bad bunny
💾 Guardando en memoria conversacional
```

### Estadísticas en Tiempo Real
```
📊 Estadísticas de memoria:
📚 Entradas de conversación: 25
❤️ Preferencias aprendidas: 8
🔄 Acciones recientes: 15
❌ Comandos fallidos: 2
```

## 🔮 Futuras Mejoras

### Características Planificadas
- 🎯 **Predicción de comandos**: Sugerir comandos antes de que el usuario los pida
- 📊 **Análisis de sentimientos**: Adaptar respuestas al estado de ánimo
- 🌍 **Contexto geográfico**: Considerar ubicación y hora local
- 🤝 **Memoria compartida**: Sincronización entre dispositivos
- 🧠 **IA más avanzada**: Usar modelos de lenguaje para análisis más profundo

### Optimizaciones Técnicas
- ⚡ **Indexación**: Búsqueda más rápida en historiales grandes
- 💾 **Compresión**: Reducir tamaño del archivo de memoria
- 🔄 **Sincronización**: Actualizaciones en tiempo real
- 📈 **Analytics**: Métricas avanzadas de uso

## 🆘 Solución de Problemas

### Memoria No Se Carga
```python
# Verificar archivo
import os
if not os.path.exists("conversation_memory.json"):
    print("Archivo de memoria no existe - se creará automáticamente")

# Verificar permisos
try:
    with open("conversation_memory.json", 'w') as f:
        f.write('{}')
    print("✅ Permisos de escritura OK")
except:
    print("❌ Error de permisos")
```

### Preferencias No Se Aprenden
```python
# Verificar que los comandos se ejecuten exitosamente
result = detector.analyze_command("pon música de bad bunny")
success = detector.execute_command(result)
print(f"Comando ejecutado: {success}")

# Solo los comandos exitosos generan preferencias
```

### Memoria Muy Grande
```python
# Limpiar datos antiguos
detector.conversation_memory.clear_old_data(days=7)

# Reducir tamaño máximo del historial
detector.conversation_memory.max_history = 500
```

---

## 📚 Referencias

- **Archivo principal**: `conversation_memory.py`
- **Integración**: `unified_command_detector.py`
- **Demo**: `demo_conversation_memory.py`
- **Documentación**: Este archivo

---

*🧠 Sistema de Memoria Conversacional - Haciendo a Roxy más inteligente con cada interacción*
