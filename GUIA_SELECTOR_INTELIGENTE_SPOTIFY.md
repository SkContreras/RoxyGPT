# 🧠 Guía del Selector Inteligente de Música - Roxy Assistant

## 📋 **RESUMEN**

Roxy ahora incluye un **Sistema de Selección Inteligente de Música** que aprende de tu historial de Spotify para hacer recomendaciones personalizadas. Ya no reproduce música aleatoria cuando dices "pon música" - ahora elige basándose en tus gustos reales.

---

## 🎯 **CARACTERÍSTICAS PRINCIPALES**

### 🔍 **Extracción de Datos de Spotify:**
- ✅ **Historial de escucha** (últimas 50 canciones)
- ✅ **Top tracks** (tus canciones más escuchadas)
- ✅ **Top artists** (tus artistas favoritos)
- ✅ **Biblioteca guardada** (canciones que tienes guardadas)
- ✅ **Playlists** (tus listas de reproducción)
- ✅ **Artistas seguidos** (artistas que sigues)
- ✅ **Estado actual** (qué estás escuchando ahora)
- ✅ **Características de audio** (análisis de tus preferencias musicales)

### 🧠 **Selección Inteligente:**
- 🎯 **Personalizada** - Basada en TUS gustos reales
- 🎭 **Contextual** - Considera mood, hora del día, input del usuario
- 📊 **Múltiples estrategias** - 5 niveles de selección con fallbacks
- 🔄 **Auto-actualizable** - Se mantiene sincronizada con tu Spotify
- 💾 **Cache inteligente** - Almacena datos para respuesta rápida

---

## 🚀 **CÓMO FUNCIONA**

### 1. **Análisis de Preferencias**
```
🔍 Roxy analiza tu Spotify:
   📊 Géneros más escuchados
   🎤 Artistas favoritos  
   🎵 Patrones de escucha
   🎭 Preferencias de mood (energía, valencia, etc.)
   📈 Nivel de descubrimiento musical
```

### 2. **Estrategias de Selección** (Por prioridad)

**🎯 NIVEL 1: Input Específico**
```
Usuario: "pon música de bad bunny"
🧠 Detecta: Artista favorito mencionado
✨ Resultado: Reproduce Bad Bunny (tu artista favorito)
```

**🎭 NIVEL 2: Contexto/Mood**
```
Usuario: "música para la fiesta"
🧠 Detecta: Mood = party
✨ Resultado: Música energética de tus géneros favoritos
```

**❤️ NIVEL 3: Preferencias Generales**
```
Usuario: "pon música"
🧠 Usa: Tus artistas y géneros favoritos
✨ Resultado: Mezcla personalizada de tu música favorita
```

**📚 NIVEL 4: Historial Reciente**
```
🧠 Analiza: Lo que has escuchado últimamente
✨ Resultado: Música similar pero no repetida
```

**🔄 NIVEL 5: Fallback Inteligente**
```
🧠 Usa: Top tracks o biblioteca guardada
✨ Resultado: Tus canciones más escuchadas
```

---

## 💬 **COMANDOS DISPONIBLES**

### 🎵 **Comandos de Música (Ahora Inteligentes):**
```bash
"pon música"                    # Selección personalizada automática
"reproduce algo"                # Basado en tus gustos
"sorpréndeme"                  # Música inteligente
"música para la fiesta"        # Selección contextual
"algo relajante"               # Mood-based selection
"música para entrenar"         # Contexto workout
```

### 🔄 **Comandos de Gestión:**
```bash
"refresh music data"           # Actualizar datos de Spotify
"actualizar musica"           # Sincronizar con tu cuenta
"refresh spotify"             # Obtener datos frescos
"update music"                # Renovar preferencias
```

### 📊 **Ver Estadísticas:**
```bash
"stats"                       # Ver estado del selector inteligente
```

---

## 🎭 **DETECCIÓN DE MOOD/CONTEXTO**

### 🎉 **Party/Fiesta:**
- **Keywords:** fiesta, party, bailar, celebrar
- **Resultado:** Música energética, reggaeton, dance, pop
- **Características:** Alta energía, alta bailabilidad

### 😌 **Chill/Relajante:**
- **Keywords:** relajar, chill, tranquilo, suave
- **Resultado:** Música relajante, indie, acoustic, ambient
- **Características:** Baja energía, alta acústica

### 💪 **Workout/Ejercicio:**
- **Keywords:** ejercicio, gym, entrenar, correr
- **Resultado:** Música motivacional, hip hop, electronic, rock
- **Características:** Alta energía, tempo rápido

### 😢 **Sad/Triste:**
- **Keywords:** triste, sad, llorar, melancólico
- **Resultado:** Música melancólica, indie, alternative
- **Características:** Baja valencia, baja energía

### 😊 **Happy/Feliz:**
- **Keywords:** feliz, happy, alegre, contento
- **Resultado:** Música positiva, pop, funk, soul
- **Características:** Alta valencia, alta energía

### 🎯 **Focus/Concentración:**
- **Keywords:** concentrar, estudiar, trabajo, focus
- **Resultado:** Música instrumental, ambient, lo-fi
- **Características:** Alta instrumentalidad, baja energía

---

## ⏰ **SELECCIÓN POR HORA DEL DÍA**

### 🌅 **Mañana (6:00 - 12:00):**
- Música energizante para empezar el día
- Términos: "morning music", "wake up", "energizing"

### ☀️ **Tarde (12:00 - 18:00):**
- Música productiva para trabajar
- Términos: "afternoon vibes", "work music"

### 🌆 **Noche (18:00 - 22:00):**
- Música relajante para la cena
- Términos: "evening music", "dinner music"

### 🌙 **Madrugada (22:00 - 6:00):**
- Música chill para la noche
- Términos: "night music", "late night", "ambient"

---

## 📊 **EJEMPLOS DE FUNCIONAMIENTO**

### 🎵 **Ejemplo 1: Comando Genérico**
```
Usuario: "pon música"

🧠 Proceso:
1. Detecta: Sin artista específico
2. Usa: Selector inteligente
3. Analiza: Tus artistas favoritos (ej: Bad Bunny, Fuerza Regida)
4. Selecciona: Canción de tu artista favorito
5. Reproduce: "Bad Bunny - Tití Me Preguntó"
6. Razón: "Artista favorito basado en tu historial"

🎤 DJ Roxy: "DJ Roxy en cabina - ¡Pura energía!"
🎵 ¡Reproduciendo! Bad Bunny - Tití Me Preguntó
🎤 DJ Roxy: "Bad Bunny - Tití Me Preguntó"
```

### 🎉 **Ejemplo 2: Contexto Party**
```
Usuario: "música para la fiesta"

🧠 Proceso:
1. Detecta: Mood = party
2. Busca: Géneros energéticos en tus favoritos
3. Encuentra: Reggaeton (tu género favorito)
4. Selecciona: Música reggaeton energética
5. Reproduce: Canción de reggaeton popular

🎤 DJ Roxy: "¡Buena elección!"
🎵 ¡Reproduciendo! Karol G - Provenza
🎤 DJ Roxy: "Karol G - Provenza - ¡A perrear!"
```

### 🎯 **Ejemplo 3: Artista Específico**
```
Usuario: "pon algo de fuerza regida"

🧠 Proceso:
1. Detecta: Artista específico mencionado
2. Verifica: Fuerza Regida está en tus favoritos
3. Busca: Canciones de Fuerza Regida
4. Selecciona: Su canción más popular
5. Reproduce: Con alta confianza

🎵 ¡Reproduciendo! Fuerza Regida - Chinita
🎤 DJ Roxy: "Fuerza Regida - Chinita"
```

---

## 📁 **ARCHIVOS DEL SISTEMA**

### 🔧 **Archivos Principales:**
- `spotify_user_data_extractor.py` - Extrae datos de Spotify API
- `intelligent_music_selector.py` - Lógica de selección inteligente
- `unified_command_detector.py` - Integración con detector de comandos
- `bot_roxy_unified.py` - Interfaz principal con comandos

### 💾 **Archivos de Cache:**
- `cache/spotify_user_data.json` - Datos del usuario (1 hora de validez)
- `cache/spotify_preferences.json` - Preferencias procesadas (24 horas)

---

## 🔧 **CONFIGURACIÓN Y REQUISITOS**

### ✅ **Requisitos:**
- Cuenta de Spotify (Free o Premium)
- Spotify API configurada (Client ID/Secret en .env)
- Token de acceso válido
- Conexión a internet

### 🔄 **Actualización Automática:**
- **Cache de datos:** 1 hora
- **Preferencias:** 24 horas
- **Comando manual:** `refresh music data`

---

## 📈 **ESTADÍSTICAS DISPONIBLES**

### 📊 **Al usar comando `stats`:**
```
🧠 Selector Inteligente: ✅ DISPONIBLE
   🎤 Artistas favoritos: 25
   🎼 Géneros favoritos: 12
   🎵 Datos recientes: 50 canciones
   ⭐ Top tracks: 50 canciones
   💾 Biblioteca: 245 canciones
```

### 🔄 **Al usar `refresh music data`:**
```
✅ Datos musicales actualizados!
   🎤 Artistas favoritos: 28
   🎼 Géneros favoritos: 15
   🎵 Historial reciente: 50 canciones
   ⭐ Top tracks: 50 canciones
   💾 Biblioteca: 267 canciones
```

---

## 🎯 **VENTAJAS DEL SISTEMA**

### ✅ **Antes (Sistema Básico):**
```
Usuario: "pon música"
Sistema: Busca "música" en Spotify
Resultado: Cualquier canción con "música" en el título
Personalización: ❌ Ninguna
```

### 🌟 **Ahora (Sistema Inteligente):**
```
Usuario: "pon música"
Sistema: Analiza TUS gustos musicales
Resultado: Tu artista favorito o género preferido
Personalización: ✅ 100% basada en tu historial real
Contexto: ✅ Considera mood y hora del día
Aprendizaje: ✅ Mejora con el tiempo
```

---

## 🔧 **RESOLUCIÓN DE PROBLEMAS**

### ❌ **"Selector inteligente no disponible"**
- Verificar autenticación de Spotify
- Ejecutar `refresh music data`
- Revisar conexión a internet

### ❌ **"No se pudieron extraer datos"**
- Verificar tokens de Spotify
- Comprobar permisos de API
- Intentar reautenticar

### ❌ **Recomendaciones no personalizadas**
- Usar `refresh music data` para actualizar
- Verificar que tienes historial en Spotify
- Escuchar más música para mejorar recomendaciones

---

## 🎵 **CONCLUSIÓN**

El **Selector Inteligente de Música** transforma a Roxy de un reproductor genérico a un **DJ personal que conoce tus gustos**. Ahora cuando dices "pon música", Roxy:

- 🎯 **Elige basándose en TUS gustos reales**
- 🎭 **Considera el contexto y mood**
- 🧠 **Aprende de tu comportamiento**
- 🔄 **Se mantiene actualizada automáticamente**
- 🎤 **Combina con narración DJ para experiencia completa**

**¡Disfruta de tu música personalizada con Roxy!** 🎧✨
