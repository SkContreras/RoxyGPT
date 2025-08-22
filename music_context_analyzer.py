"""
Sistema de Análisis de Contexto Musical Inteligente - Roxy Assistant
================================================================
Analiza múltiples dimensiones del contexto del usuario para selección musical óptima:
- Detección de estado de ánimo avanzada
- Inferencia de actividad actual
- Contexto temporal y climático
- Situación social
- Análisis del entorno del usuario
"""

import os
import json
import time
import psutil
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import re

# Importaciones opcionales
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    from personality_config import PersonalityConfig
    PERSONALITY_AVAILABLE = True
except ImportError:
    PERSONALITY_AVAILABLE = False

@dataclass
class MoodAnalysis:
    """Análisis de estado de ánimo del usuario"""
    primary_mood: str  # happy, sad, energetic, calm, focused, etc.
    secondary_moods: List[str]
    confidence: float  # 0.0 - 1.0
    indicators: List[str]  # Qué llevó a esta conclusión
    energy_level: float  # 0.0 - 1.0
    valence: float  # 0.0 - 1.0 (negative to positive)

@dataclass
class ActivityContext:
    """Contexto de actividad actual del usuario"""
    primary_activity: str  # working, exercising, relaxing, socializing, etc.
    confidence: float
    indicators: List[str]
    activity_intensity: float  # 0.0 - 1.0
    duration_estimate: Optional[int]  # minutos estimados
    location_context: str  # home, office, gym, car, etc.

@dataclass
class TemporalContext:
    """Contexto temporal y ambiental"""
    time_of_day: str  # morning, afternoon, evening, night
    day_of_week: str
    is_weekend: bool
    season: str  # spring, summer, fall, winter
    weather_mood: Optional[str]  # sunny, rainy, cloudy, etc.
    special_occasion: Optional[str]  # holiday, birthday, etc.

@dataclass
class SocialContext:
    """Contexto social del usuario"""
    social_situation: str  # alone, with_friends, family, party, etc.
    group_size_estimate: int
    formality_level: str  # casual, formal, intimate
    confidence: float

@dataclass
class SystemContext:
    """Contexto del sistema y entorno técnico"""
    cpu_usage: float
    memory_usage: float
    active_applications: List[str]
    user_idle_time: float
    audio_output_device: Optional[str]
    volume_level: Optional[float]

@dataclass
class MusicContext:
    """Contexto musical completo"""
    mood: MoodAnalysis
    activity: ActivityContext
    temporal: TemporalContext
    social: SocialContext
    system: SystemContext
    overall_confidence: float
    context_summary: str
    music_recommendations: Dict[str, Any]

class MusicContextAnalyzer:
    """Analizador inteligente de contexto musical"""
    
    def __init__(self, personality_config=None):
        """Inicializar analizador de contexto musical"""
        self.personality = personality_config
        self.ollama_available = OLLAMA_AVAILABLE
        self.model = "llama3:latest"
        
        # Configuración de análisis
        self.mood_keywords = self._load_mood_keywords()
        self.activity_patterns = self._load_activity_patterns()
        self.weather_api_key = os.getenv('WEATHER_API_KEY')  # OpenWeatherMap API
        
        # Cache para evitar análisis repetitivos
        self.context_cache = {}
        self.cache_duration = 300  # 5 minutos
        
        print("🧠 Music Context Analyzer inicializado")
    
    def analyze_music_context(self, user_input: str, conversation_history: List[Dict] = None) -> MusicContext:
        """
        Análisis completo del contexto musical
        
        Args:
            user_input: Input actual del usuario
            conversation_history: Historial de conversación reciente
            
        Returns:
            MusicContext: Análisis completo del contexto
        """
        
        print(f"🔍 Analizando contexto musical para: '{user_input}'")
        
        # Verificar cache
        cache_key = self._generate_cache_key(user_input)
        if cache_key in self.context_cache:
            cached_data = self.context_cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_duration:
                print("📦 Usando contexto en cache")
                return cached_data['context']
        
        # Análisis de diferentes dimensiones
        mood_analysis = self._detect_mood(user_input, conversation_history)
        activity_context = self._infer_activity(user_input, conversation_history)
        temporal_context = self._get_time_context()
        social_context = self._detect_social_situation(user_input, conversation_history)
        system_context = self._get_system_context()
        
        # Calcular confianza general
        overall_confidence = self._calculate_overall_confidence([
            mood_analysis.confidence,
            activity_context.confidence,
            social_context.confidence
        ])
        
        # Generar resumen contextual
        context_summary = self._generate_context_summary(
            mood_analysis, activity_context, temporal_context, social_context
        )
        
        # Generar recomendaciones musicales
        music_recommendations = self._generate_music_recommendations(
            mood_analysis, activity_context, temporal_context, social_context
        )
        
        # Crear contexto completo
        music_context = MusicContext(
            mood=mood_analysis,
            activity=activity_context,
            temporal=temporal_context,
            social=social_context,
            system=system_context,
            overall_confidence=overall_confidence,
            context_summary=context_summary,
            music_recommendations=music_recommendations
        )
        
        # Guardar en cache
        self.context_cache[cache_key] = {
            'timestamp': time.time(),
            'context': music_context
        }
        
        print(f"✅ Contexto analizado - Confianza: {overall_confidence:.2f}")
        return music_context
    
    def _detect_mood(self, user_input: str, conversation_history: List[Dict] = None) -> MoodAnalysis:
        """Detectar estado de ánimo del usuario usando múltiples indicadores"""
        
        indicators = []
        primary_mood = "neutral"
        secondary_moods = []
        confidence = 0.5
        energy_level = 0.5
        valence = 0.5
        
        user_lower = user_input.lower()
        
        # Análisis por keywords directo
        mood_scores = {}
        for mood, keywords in self.mood_keywords.items():
            score = sum(1 for keyword in keywords if keyword in user_lower)
            if score > 0:
                mood_scores[mood] = score
                indicators.append(f"Keywords de '{mood}': {score}")
        
        # Análisis avanzado con LLM si está disponible
        if self.ollama_available and conversation_history:
            llm_mood = self._analyze_mood_with_llm(user_input, conversation_history)
            if llm_mood:
                llm_moods = llm_mood.get('moods', {})
                # Asegurar que los valores del LLM sean numéricos
                for mood, score in llm_moods.items():
                    if isinstance(score, (int, float)):
                        mood_scores[mood] = mood_scores.get(mood, 0) + score
                indicators.extend(llm_mood.get('indicators', []))
                confidence = max(confidence, llm_mood.get('confidence', 0.5))
        
        # Determinar mood principal - asegurar que todos los valores sean numéricos
        if mood_scores:
            # Filtrar solo valores numéricos
            numeric_scores = {mood: score for mood, score in mood_scores.items() 
                            if isinstance(score, (int, float))}
            
            if numeric_scores:
                primary_mood = max(numeric_scores.items(), key=lambda x: x[1])[0]
                secondary_moods = [mood for mood, score in sorted(numeric_scores.items(), 
                                 key=lambda x: x[1], reverse=True)[1:3]]
                confidence = min(0.9, confidence + 0.2 * len(indicators))
        
        # Calcular energy y valence basado en mood
        energy_level, valence = self._mood_to_audio_features(primary_mood)
        
        return MoodAnalysis(
            primary_mood=primary_mood,
            secondary_moods=secondary_moods,
            confidence=confidence,
            indicators=indicators,
            energy_level=energy_level,
            valence=valence
        )
    
    def _infer_activity(self, user_input: str, conversation_history: List[Dict] = None) -> ActivityContext:
        """Inferir actividad actual del usuario"""
        
        indicators = []
        primary_activity = "general"
        confidence = 0.3
        activity_intensity = 0.5
        duration_estimate = None
        location_context = "unknown"
        
        user_lower = user_input.lower()
        
        # Patrones de actividad en el input
        for activity, patterns in self.activity_patterns.items():
            matches = sum(1 for pattern in patterns if re.search(pattern, user_lower))
            if matches > 0:
                primary_activity = activity
                confidence = min(0.8, 0.4 + matches * 0.2)
                indicators.append(f"Patrones de '{activity}': {matches}")
                break
        
        # Análisis del sistema para inferir actividad
        system_activity = self._infer_activity_from_system()
        if system_activity:
            if primary_activity == "general":
                primary_activity = system_activity['activity']
                confidence = system_activity['confidence']
            indicators.extend(system_activity['indicators'])
        
        # Inferir intensidad y duración basado en actividad
        activity_intensity, duration_estimate = self._get_activity_characteristics(primary_activity)
        
        # Inferir ubicación
        location_context = self._infer_location_context(primary_activity, user_input)
        
        return ActivityContext(
            primary_activity=primary_activity,
            confidence=confidence,
            indicators=indicators,
            activity_intensity=activity_intensity,
            duration_estimate=duration_estimate,
            location_context=location_context
        )
    
    def _get_time_context(self) -> TemporalContext:
        """Obtener contexto temporal y ambiental"""
        
        now = datetime.now()
        hour = now.hour
        
        # Determinar período del día
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 21:
            time_of_day = "evening"
        else:
            time_of_day = "night"
        
        # Día de la semana
        day_of_week = now.strftime("%A").lower()
        is_weekend = now.weekday() >= 5
        
        # Estación del año (hemisferio norte)
        month = now.month
        if month in [12, 1, 2]:
            season = "winter"
        elif month in [3, 4, 5]:
            season = "spring"
        elif month in [6, 7, 8]:
            season = "summer"
        else:
            season = "fall"
        
        # Clima (si hay API key)
        weather_mood = self._get_weather_mood()
        
        # Ocasiones especiales
        special_occasion = self._detect_special_occasion(now)
        
        return TemporalContext(
            time_of_day=time_of_day,
            day_of_week=day_of_week,
            is_weekend=is_weekend,
            season=season,
            weather_mood=weather_mood,
            special_occasion=special_occasion
        )
    
    def _detect_social_situation(self, user_input: str, conversation_history: List[Dict] = None) -> SocialContext:
        """Detectar situación social del usuario"""
        
        social_situation = "alone"
        group_size_estimate = 1
        formality_level = "casual"
        confidence = 0.4
        
        user_lower = user_input.lower()
        
        # Indicadores de situación social en el input
        social_indicators = {
            'with_friends': ['amigos', 'friends', 'con mis amigos', 'estamos', 'nosotros'],
            'family': ['familia', 'family', 'con la familia', 'en casa con'],
            'party': ['fiesta', 'party', 'celebrando', 'reunión'],
            'work': ['trabajo', 'oficina', 'reunión', 'meeting', 'presentación'],
            'romantic': ['cita', 'date', 'romántico', 'con mi pareja']
        }
        
        for situation, keywords in social_indicators.items():
            if any(keyword in user_lower for keyword in keywords):
                social_situation = situation
                confidence = 0.7
                
                # Estimar tamaño del grupo
                if situation in ['with_friends', 'party']:
                    group_size_estimate = 5
                elif situation == 'family':
                    group_size_estimate = 3
                elif situation == 'work':
                    group_size_estimate = 8
                    formality_level = "formal"
                elif situation == 'romantic':
                    group_size_estimate = 2
                    formality_level = "intimate"
                break
        
        return SocialContext(
            social_situation=social_situation,
            group_size_estimate=group_size_estimate,
            formality_level=formality_level,
            confidence=confidence
        )
    
    def _get_system_context(self) -> SystemContext:
        """Obtener contexto del sistema"""
        
        # Información del sistema
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        
        # Procesos activos (aplicaciones principales)
        active_applications = []
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name']
                if name and not name.startswith('System') and len(name) > 3:
                    active_applications.append(name)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        active_applications = list(set(active_applications))[:10]  # Top 10
        
        # Tiempo de inactividad (aproximado)
        user_idle_time = 0.0  # Placeholder - requiere implementación específica del OS
        
        return SystemContext(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            active_applications=active_applications,
            user_idle_time=user_idle_time,
            audio_output_device=None,  # Placeholder
            volume_level=None  # Placeholder
        )
    
    def _generate_music_recommendations(self, mood: MoodAnalysis, activity: ActivityContext, 
                                      temporal: TemporalContext, social: SocialContext) -> Dict[str, Any]:
        """Generar recomendaciones musicales basadas en el contexto completo"""
        
        recommendations = {
            'genres': [],
            'energy_range': [0.3, 0.7],
            'valence_range': [0.3, 0.7],
            'tempo_range': [80, 140],
            'danceability_range': [0.3, 0.7],
            'acousticness_range': [0.0, 1.0],
            'instrumentalness_range': [0.0, 1.0],
            'search_terms': [],
            'avoid_explicit': False,
            'context_reasoning': []
        }
        
        # Ajustes basados en mood
        mood_adjustments = self._get_mood_music_adjustments(mood)
        self._apply_adjustments(recommendations, mood_adjustments, "mood")
        
        # Ajustes basados en actividad
        activity_adjustments = self._get_activity_music_adjustments(activity)
        self._apply_adjustments(recommendations, activity_adjustments, "activity")
        
        # Ajustes basados en contexto temporal
        temporal_adjustments = self._get_temporal_music_adjustments(temporal)
        self._apply_adjustments(recommendations, temporal_adjustments, "temporal")
        
        # Ajustes basados en contexto social
        social_adjustments = self._get_social_music_adjustments(social)
        self._apply_adjustments(recommendations, social_adjustments, "social")
        
        return recommendations
    
    # Métodos auxiliares y configuración
    def _load_mood_keywords(self) -> Dict[str, List[str]]:
        """Cargar keywords para detección de mood"""
        return {
            'happy': ['feliz', 'alegre', 'contento', 'bien', 'genial', 'perfecto', 'excelente', 'happy', 'joy'],
            'sad': ['triste', 'mal', 'deprimido', 'melancólico', 'sad', 'down', 'blue'],
            'energetic': ['energético', 'activo', 'motivado', 'pump up', 'energetic', 'hyped'],
            'calm': ['tranquilo', 'relajado', 'peaceful', 'calm', 'chill', 'zen'],
            'focused': ['concentrado', 'estudiando', 'trabajando', 'focus', 'study'],
            'romantic': ['romántico', 'amor', 'cita', 'romantic', 'love'],
            'party': ['fiesta', 'celebrando', 'party', 'dance', 'bailar'],
            'nostalgic': ['nostálgico', 'recuerdos', 'nostalgic', 'memories', 'throwback'],
            'angry': ['enojado', 'molesto', 'frustrado', 'angry', 'mad', 'pissed'],
            'anxious': ['ansioso', 'nervioso', 'estresado', 'anxious', 'stressed', 'worried']
        }
    
    def _load_activity_patterns(self) -> Dict[str, List[str]]:
        """Cargar patrones para detección de actividad"""
        return {
            'working': [r'\b(trabajo|trabajando|oficina|meeting|reunión)\b'],
            'exercising': [r'\b(ejercicio|gym|correr|entrenar|workout)\b'],
            'studying': [r'\b(estudiando|study|concentrar|focus|tarea)\b'],
            'cooking': [r'\b(cocinando|cocinar|kitchen|preparando)\b'],
            'driving': [r'\b(manejando|conduciendo|driving|car|auto)\b'],
            'cleaning': [r'\b(limpiando|clean|ordenando)\b'],
            'socializing': [r'\b(con amigos|friends|reunión|social)\b'],
            'relaxing': [r'\b(relajando|relax|descansar|chill)\b'],
            'gaming': [r'\b(jugando|gaming|game|videojuego)\b'],
            'reading': [r'\b(leyendo|reading|libro|book)\b']
        }
    
    def _analyze_mood_with_llm(self, user_input: str, conversation_history: List[Dict]) -> Optional[Dict]:
        """Usar LLM para análisis avanzado de mood"""
        if not self.ollama_available:
            return None
        
        try:
            # Construir contexto de conversación
            context = ""
            if conversation_history:
                recent_messages = conversation_history[-5:]  # Últimos 5 mensajes
                context = "\n".join([f"Usuario: {msg.get('user', '')}\nRoxy: {msg.get('roxy', '')}" 
                                   for msg in recent_messages if msg.get('user')])
            
            prompt = f"""
Analiza el estado de ánimo del usuario basándote en su mensaje actual y el contexto de la conversación.

CONTEXTO RECIENTE:
{context}

MENSAJE ACTUAL: "{user_input}"

Determina:
1. Estado de ánimo principal y secundarios
2. Nivel de energía (0.0-1.0)
3. Valencia emocional (0.0=negativo, 1.0=positivo)
4. Confianza en el análisis (0.0-1.0)
5. Indicadores que llevaron a esta conclusión

RESPONDE EN JSON:
{{
  "moods": {{"primary": "mood_name", "secondary": ["mood1", "mood2"]}},
  "energy_level": 0.7,
  "valence": 0.8,
  "confidence": 0.9,
  "indicators": ["indicador1", "indicador2"]
}}
"""
            
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.3}
            )
            
            content = response['message']['content'].strip()
            
            # Extraer JSON
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
                
        except Exception as e:
            print(f"❌ Error en análisis LLM de mood: {e}")
        
        return None
    
    def _mood_to_audio_features(self, mood: str) -> Tuple[float, float]:
        """Convertir mood a características de audio (energy, valence)"""
        mood_features = {
            'happy': (0.7, 0.8),
            'sad': (0.3, 0.2),
            'energetic': (0.9, 0.7),
            'calm': (0.3, 0.6),
            'focused': (0.4, 0.5),
            'romantic': (0.5, 0.8),
            'party': (0.9, 0.9),
            'nostalgic': (0.4, 0.4),
            'angry': (0.8, 0.3),
            'anxious': (0.6, 0.3)
        }
        return mood_features.get(mood, (0.5, 0.5))
    
    def _infer_activity_from_system(self) -> Optional[Dict[str, Any]]:
        """Inferir actividad basándose en aplicaciones activas del sistema"""
        try:
            active_apps = []
            for proc in psutil.process_iter(['name']):
                try:
                    name = proc.info['name'].lower()
                    active_apps.append(name)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Patrones de aplicaciones
            app_patterns = {
                'working': ['word', 'excel', 'powerpoint', 'outlook', 'slack', 'teams', 'zoom'],
                'gaming': ['steam', 'game', 'epic', 'battle', 'origin'],
                'studying': ['notion', 'obsidian', 'anki', 'pdf', 'reader'],
                'media_consuming': ['netflix', 'youtube', 'vlc', 'media', 'browser'],
                'developing': ['code', 'visual studio', 'pycharm', 'git', 'terminal']
            }
            
            for activity, patterns in app_patterns.items():
                matches = sum(1 for app in active_apps if any(pattern in app for pattern in patterns))
                if matches > 0:
                    return {
                        'activity': activity,
                        'confidence': min(0.8, 0.3 + matches * 0.2),
                        'indicators': [f"Apps activas: {matches} relacionadas con {activity}"]
                    }
            
        except Exception as e:
            print(f"⚠️ Error inferiendo actividad del sistema: {e}")
        
        return None
    
    def _get_activity_characteristics(self, activity: str) -> Tuple[float, Optional[int]]:
        """Obtener características de intensidad y duración de actividad"""
        activity_chars = {
            'working': (0.4, 60),
            'exercising': (0.9, 45),
            'studying': (0.3, 90),
            'cooking': (0.5, 30),
            'driving': (0.6, None),
            'cleaning': (0.7, 45),
            'socializing': (0.6, None),
            'relaxing': (0.2, None),
            'gaming': (0.7, 120),
            'reading': (0.2, 60)
        }
        return activity_chars.get(activity, (0.5, None))
    
    def _infer_location_context(self, activity: str, user_input: str) -> str:
        """Inferir contexto de ubicación"""
        location_keywords = {
            'home': ['casa', 'home', 'en casa'],
            'office': ['oficina', 'office', 'trabajo'],
            'gym': ['gym', 'gimnasio'],
            'car': ['auto', 'car', 'manejando'],
            'outdoors': ['parque', 'outside', 'afuera']
        }
        
        user_lower = user_input.lower()
        for location, keywords in location_keywords.items():
            if any(keyword in user_lower for keyword in keywords):
                return location
        
        # Inferir por actividad
        activity_locations = {
            'exercising': 'gym',
            'working': 'office',
            'driving': 'car',
            'cooking': 'home',
            'relaxing': 'home'
        }
        
        return activity_locations.get(activity, 'unknown')
    
    def _get_weather_mood(self) -> Optional[str]:
        """Obtener mood del clima actual (requiere API key)"""
        if not self.weather_api_key:
            return None
        
        try:
            # Placeholder para integración con API del clima
            # Aquí iría la implementación real con OpenWeatherMap u otra API
            return None
        except Exception as e:
            print(f"⚠️ Error obteniendo clima: {e}")
            return None
    
    def _detect_special_occasion(self, now: datetime) -> Optional[str]:
        """Detectar ocasiones especiales"""
        month = now.month
        day = now.day
        
        special_dates = {
            (12, 25): "christmas",
            (1, 1): "new_year",
            (2, 14): "valentine",
            (10, 31): "halloween",
            (12, 31): "new_year_eve"
        }
        
        return special_dates.get((month, day))
    
    def _get_mood_music_adjustments(self, mood: MoodAnalysis) -> Dict[str, Any]:
        """Obtener ajustes musicales basados en mood"""
        mood_configs = {
            'happy': {
                'genres': ['pop', 'funk', 'disco'],
                'energy_range': [0.6, 0.9],
                'valence_range': [0.7, 1.0],
                'search_terms': ['happy music', 'feel good', 'upbeat']
            },
            'sad': {
                'genres': ['indie', 'alternative', 'acoustic'],
                'energy_range': [0.1, 0.5],
                'valence_range': [0.0, 0.4],
                'search_terms': ['sad songs', 'melancholic', 'emotional']
            },
            'energetic': {
                'genres': ['electronic', 'rock', 'hip hop'],
                'energy_range': [0.7, 1.0],
                'tempo_range': [120, 180],
                'search_terms': ['high energy', 'pump up', 'motivation']
            },
            'calm': {
                'genres': ['ambient', 'classical', 'chill'],
                'energy_range': [0.1, 0.4],
                'acousticness_range': [0.3, 1.0],
                'search_terms': ['calm music', 'relaxing', 'peaceful']
            }
        }
        
        return mood_configs.get(mood.primary_mood, {})
    
    def _get_activity_music_adjustments(self, activity: ActivityContext) -> Dict[str, Any]:
        """Obtener ajustes musicales basados en actividad"""
        activity_configs = {
            'working': {
                'genres': ['lo-fi', 'ambient', 'instrumental'],
                'instrumentalness_range': [0.3, 1.0],
                'energy_range': [0.3, 0.6],
                'search_terms': ['focus music', 'work music', 'productivity']
            },
            'exercising': {
                'genres': ['electronic', 'hip hop', 'rock'],
                'energy_range': [0.7, 1.0],
                'tempo_range': [120, 160],
                'search_terms': ['workout music', 'gym music', 'motivation']
            },
            'studying': {
                'genres': ['classical', 'instrumental', 'ambient'],
                'instrumentalness_range': [0.5, 1.0],
                'energy_range': [0.2, 0.5],
                'search_terms': ['study music', 'concentration', 'focus']
            },
            'relaxing': {
                'genres': ['chill', 'ambient', 'acoustic'],
                'energy_range': [0.1, 0.4],
                'valence_range': [0.4, 0.8],
                'search_terms': ['chill music', 'relaxing', 'peaceful']
            }
        }
        
        return activity_configs.get(activity.primary_activity, {})
    
    def _get_temporal_music_adjustments(self, temporal: TemporalContext) -> Dict[str, Any]:
        """Obtener ajustes musicales basados en contexto temporal"""
        time_configs = {
            'morning': {
                'genres': ['indie pop', 'folk', 'acoustic'],
                'energy_range': [0.4, 0.7],
                'search_terms': ['morning music', 'wake up', 'coffee music']
            },
            'afternoon': {
                'genres': ['pop', 'indie', 'alternative'],
                'energy_range': [0.5, 0.8],
                'search_terms': ['afternoon vibes', 'productive music']
            },
            'evening': {
                'genres': ['jazz', 'soul', 'r&b'],
                'energy_range': [0.3, 0.6],
                'search_terms': ['evening music', 'dinner music', 'sophisticated']
            },
            'night': {
                'genres': ['ambient', 'electronic', 'chill'],
                'energy_range': [0.2, 0.5],
                'search_terms': ['night music', 'late night', 'atmospheric']
            }
        }
        
        config = time_configs.get(temporal.time_of_day, {})
        
        # Ajustes adicionales para fin de semana
        if temporal.is_weekend:
            config['energy_range'] = [x + 0.1 for x in config.get('energy_range', [0.5, 0.8])]
            config['search_terms'] = config.get('search_terms', []) + ['weekend vibes']
        
        return config
    
    def _get_social_music_adjustments(self, social: SocialContext) -> Dict[str, Any]:
        """Obtener ajustes musicales basados en contexto social"""
        social_configs = {
            'party': {
                'genres': ['reggaeton', 'pop', 'dance', 'electronic'],
                'energy_range': [0.7, 1.0],
                'danceability_range': [0.6, 1.0],
                'search_terms': ['party music', 'dance hits', 'crowd pleasers'],
                'avoid_explicit': False
            },
            'with_friends': {
                'genres': ['pop', 'rock', 'indie'],
                'energy_range': [0.5, 0.8],
                'search_terms': ['social music', 'group favorites', 'sing along']
            },
            'romantic': {
                'genres': ['r&b', 'soul', 'acoustic'],
                'valence_range': [0.6, 0.9],
                'energy_range': [0.3, 0.6],
                'search_terms': ['romantic music', 'love songs', 'intimate']
            },
            'work': {
                'genres': ['instrumental', 'ambient', 'classical'],
                'instrumentalness_range': [0.7, 1.0],
                'avoid_explicit': True,
                'search_terms': ['professional music', 'background music']
            }
        }
        
        return social_configs.get(social.social_situation, {})
    
    def _apply_adjustments(self, recommendations: Dict[str, Any], adjustments: Dict[str, Any], source: str):
        """Aplicar ajustes a las recomendaciones"""
        if not adjustments:
            return
        
        for key, value in adjustments.items():
            if key in recommendations:
                if isinstance(value, list):
                    if key.endswith('_range'):
                        # Combinar rangos tomando intersección
                        current_range = recommendations[key]
                        new_range = [max(current_range[0], value[0]), min(current_range[1], value[1])]
                        recommendations[key] = new_range
                    else:
                        # Agregar a listas
                        recommendations[key].extend(value)
                else:
                    recommendations[key] = value
        
        # Agregar razonamiento
        if 'context_reasoning' in recommendations:
            recommendations['context_reasoning'].append(f"Ajustes por {source}: {list(adjustments.keys())}")
    
    def _calculate_overall_confidence(self, confidences: List[float]) -> float:
        """Calcular confianza general del análisis"""
        if not confidences:
            return 0.0
        
        # Promedio ponderado con penalización por baja confianza
        avg_confidence = sum(confidences) / len(confidences)
        min_confidence = min(confidences)
        
        # Si alguna confianza es muy baja, penalizar el resultado general
        if min_confidence < 0.3:
            avg_confidence *= 0.7
        
        return min(0.95, avg_confidence)
    
    def _generate_context_summary(self, mood: MoodAnalysis, activity: ActivityContext, 
                                 temporal: TemporalContext, social: SocialContext) -> str:
        """Generar resumen textual del contexto"""
        
        summary_parts = []
        
        # Mood
        if mood.confidence > 0.5:
            summary_parts.append(f"Mood: {mood.primary_mood}")
            if mood.secondary_moods:
                summary_parts.append(f"({', '.join(mood.secondary_moods[:2])})")
        
        # Actividad
        if activity.confidence > 0.5:
            summary_parts.append(f"Actividad: {activity.primary_activity}")
        
        # Tiempo
        summary_parts.append(f"Momento: {temporal.time_of_day}")
        if temporal.is_weekend:
            summary_parts.append("(fin de semana)")
        
        # Social
        if social.confidence > 0.5 and social.social_situation != "alone":
            summary_parts.append(f"Social: {social.social_situation}")
        
        return " | ".join(summary_parts)
    
    def _generate_cache_key(self, user_input: str) -> str:
        """Generar clave de cache para el contexto"""
        # Incluir hora redondeada para que el cache sea válido por períodos
        hour_rounded = datetime.now().replace(minute=0, second=0, microsecond=0)
        return f"{user_input[:50]}_{hour_rounded.isoformat()}"
    
    def get_context_summary_for_display(self, context: MusicContext) -> Dict[str, str]:
        """Obtener resumen del contexto para mostrar al usuario"""
        return {
            'mood': f"{context.mood.primary_mood} ({context.mood.confidence:.2f})",
            'activity': f"{context.activity.primary_activity} ({context.activity.confidence:.2f})",
            'time': f"{context.temporal.time_of_day} - {context.temporal.day_of_week}",
            'social': f"{context.social.social_situation} ({context.social.confidence:.2f})",
            'overall_confidence': f"{context.overall_confidence:.2f}",
            'summary': context.context_summary
        }

# Función de prueba
def test_music_context_analyzer():
    """Función de prueba para el analizador de contexto"""
    print("🧪 TESTING: Music Context Analyzer")
    print("=" * 50)
    
    analyzer = MusicContextAnalyzer()
    
    # Casos de prueba
    test_cases = [
        "Pon música alegre para la fiesta",
        "Necesito algo tranquilo para estudiar",
        "Música para entrenar en el gym",
        "Algo romántico para la cena",
        "Estoy triste, pon algo que me anime",
        "Música para trabajar sin distracciones"
    ]
    
    for test_input in test_cases:
        print(f"\n🧪 Analizando: '{test_input}'")
        
        try:
            context = analyzer.analyze_music_context(test_input)
            summary = analyzer.get_context_summary_for_display(context)
            
            print(f"   📊 Resumen: {summary['summary']}")
            print(f"   🎭 Mood: {summary['mood']}")
            print(f"   🏃 Actividad: {summary['activity']}")
            print(f"   🕐 Tiempo: {summary['time']}")
            print(f"   👥 Social: {summary['social']}")
            print(f"   🎯 Confianza: {summary['overall_confidence']}")
            
            # Mostrar algunas recomendaciones
            recs = context.music_recommendations
            if recs.get('genres'):
                print(f"   🎵 Géneros recomendados: {', '.join(recs['genres'][:3])}")
            if recs.get('search_terms'):
                print(f"   🔍 Términos de búsqueda: {', '.join(recs['search_terms'][:2])}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_music_context_analyzer()
