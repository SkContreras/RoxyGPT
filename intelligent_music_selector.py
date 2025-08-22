"""
Intelligent Music Selector - Roxy Assistant
==========================================
Sistema inteligente que usa datos de Spotify del usuario para elegir música personalizada.
Analiza preferencias, historial y contexto para hacer selecciones inteligentes.
"""

import json
import random
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from spotify_user_data_extractor import SpotifyUserDataExtractor
from spotify_controller_unified import SpotifyControllerUnified
from music_history_manager import MusicHistoryManager
from music_context_analyzer import MusicContextAnalyzer, MusicContext

class IntelligentMusicSelector:
    def __init__(self):
        """Inicializar selector inteligente de música"""
        self.data_extractor = SpotifyUserDataExtractor()
        self.spotify_controller = SpotifyControllerUnified()
        self.history_manager = MusicHistoryManager()
        self.context_analyzer = MusicContextAnalyzer()
        self.user_preferences = {}
        self.user_data = {}
        
        # Cargar datos del usuario
        self._load_user_data()
        
        print("🧠 Intelligent Music Selector inicializado con historial y análisis de contexto")
    
    def _load_user_data(self):
        """Cargar datos y preferencias del usuario"""
        try:
            self.user_preferences = self.data_extractor.get_user_preferences()
            self.user_data = self.data_extractor._load_cache()
            
            if self.user_preferences:
                print("✅ Datos de usuario cargados exitosamente")
            else:
                print("⚠️ No hay datos de usuario - se usará selección genérica")
                
        except Exception as e:
            print(f"❌ Error cargando datos de usuario: {e}")
    
    def select_music_intelligently(self, user_input: str = "", context: str = "general", 
                                  conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Seleccionar música inteligentemente basado en:
        - Input del usuario
        - Preferencias históricas
        - Análisis completo de contexto (mood, actividad, tiempo, social)
        """
        
        print(f"🧠 Selección inteligente para: '{user_input}' (contexto: {context})")
        
        # 🧠 ANÁLISIS AVANZADO DE CONTEXTO
        music_context = self.context_analyzer.analyze_music_context(user_input, conversation_history)
        context_summary = self.context_analyzer.get_context_summary_for_display(music_context)
        
        print(f"🎭 Contexto detectado: {context_summary['summary']}")
        print(f"🎯 Confianza del análisis: {context_summary['overall_confidence']}")
        
        # Estrategias de selección por prioridad (mejoradas con contexto inteligente)
        strategies = [
            lambda ui, ctx: self._select_by_intelligent_context(ui, ctx, music_context),  # 1. Contexto inteligente
            self._select_by_user_input,      # 2. Basado en input específico
            self._select_by_context,         # 3. Basado en contexto/mood básico
            self._select_by_preferences,     # 4. Basado en preferencias
            self._select_by_recent_history,  # 5. Basado en historial reciente
            self._select_fallback           # 6. Selección de respaldo
        ]
        
        for strategy in strategies:
            try:
                result = strategy(user_input, context)
                if result and result.get('tracks'):
                    # Filtrar canciones basado en historial para evitar repeticiones
                    original_count = len(result['tracks'])
                    result['tracks'] = self.history_manager.filter_tracks_by_history(result['tracks'])
                    
                    if result['tracks']:
                        filtered_count = len(result['tracks'])
                        if filtered_count < original_count:
                            print(f"🎵 Filtrado por historial: {original_count} → {filtered_count} canciones")
                        
                        print(f"✅ Música seleccionada via: {result.get('method', 'unknown')}")
                        
                        # Enriquecer resultado con información de contexto
                        result['context_analysis'] = {
                            'mood': music_context.mood.primary_mood,
                            'activity': music_context.activity.primary_activity,
                            'social': music_context.social.social_situation,
                            'time': music_context.temporal.time_of_day,
                            'confidence': music_context.overall_confidence,
                            'summary': music_context.context_summary
                        }
                        
                        return result
                    else:
                        print(f"⚠️ Todas las canciones fueron filtradas por historial en {strategy.__name__}")
                        continue
            except Exception as e:
                print(f"⚠️ Error en estrategia {strategy.__name__}: {e}")
                continue
        
        # Si todo falla, usar selección básica
        return self._select_basic_fallback()
    
    def _select_by_intelligent_context(self, user_input: str, context: str, music_context: MusicContext) -> Optional[Dict[str, Any]]:
        """Selección basada en análisis inteligente completo de contexto"""
        
        if music_context.overall_confidence < 0.4:
            return None  # Confianza muy baja, usar otros métodos
        
        print(f"🎯 Usando contexto inteligente con confianza: {music_context.overall_confidence:.2f}")
        
        # Obtener recomendaciones del contexto
        recommendations = music_context.music_recommendations
        
        # Estrategia 1: Buscar por géneros recomendados
        if recommendations.get('genres'):
            for genre in recommendations['genres'][:3]:  # Probar top 3 géneros
                result = self._get_tracks_from_genre(genre, f"intelligent_context_genre_{genre}")
                if result and result.get('tracks'):
                    # Filtrar por características de audio recomendadas
                    filtered_tracks = self._filter_by_audio_features(result['tracks'], recommendations)
                    if filtered_tracks:
                        result['tracks'] = filtered_tracks
                        result['context_reasoning'] = f"Género {genre} basado en contexto: {music_context.context_summary}"
                        return result
        
        # Estrategia 2: Buscar por términos de búsqueda contextuales
        if recommendations.get('search_terms'):
            for search_term in recommendations['search_terms'][:2]:  # Probar top 2 términos
                result = self._search_tracks_by_term(search_term, f"intelligent_context_search_{search_term}")
                if result and result.get('tracks'):
                    filtered_tracks = self._filter_by_audio_features(result['tracks'], recommendations)
                    if filtered_tracks:
                        result['tracks'] = filtered_tracks
                        result['context_reasoning'] = f"Búsqueda '{search_term}' basada en contexto: {music_context.context_summary}"
                        return result
        
        # Estrategia 3: Combinar con preferencias del usuario
        if music_context.mood.confidence > 0.6:
            mood_result = self._select_by_mood_advanced(music_context.mood, recommendations)
            if mood_result:
                return mood_result
        
        return None
    
    def _filter_by_audio_features(self, tracks: List[Dict], recommendations: Dict[str, Any]) -> List[Dict]:
        """Filtrar tracks basándose en características de audio recomendadas"""
        
        # Por ahora retornar todos los tracks - en implementación completa
        # se consultarían las características de audio de Spotify API
        # y se filtrarían basándose en energy_range, valence_range, etc.
        
        # Placeholder: retornar primeros 5 tracks
        return tracks[:5]
    
    def _select_by_mood_advanced(self, mood_analysis, recommendations: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Selección avanzada basada en análisis de mood completo"""
        
        # Combinar mood con preferencias del usuario
        favorite_artists = self.user_preferences.get('favorite_artists', [])
        
        # Si hay artistas favoritos, buscar música de ellos que coincida con el mood
        if favorite_artists and mood_analysis.confidence > 0.7:
            for artist in favorite_artists[:3]:
                result = self._get_tracks_from_artist(artist, f"mood_advanced_{mood_analysis.primary_mood}")
                if result and result.get('tracks'):
                    result['context_reasoning'] = f"Artista favorito {artist} para mood {mood_analysis.primary_mood}"
                    return result
        
        # Buscar por características específicas del mood
        mood_search_terms = {
            'happy': ['upbeat', 'cheerful', 'positive'],
            'sad': ['melancholy', 'emotional', 'heartbreak'],
            'energetic': ['high energy', 'pump up', 'motivation'],
            'calm': ['peaceful', 'serene', 'tranquil'],
            'focused': ['concentration', 'study', 'ambient'],
            'romantic': ['love songs', 'romantic', 'intimate']
        }
        
        search_terms = mood_search_terms.get(mood_analysis.primary_mood, [])
        for term in search_terms:
            result = self._search_tracks_by_term(term, f"mood_advanced_search_{term}")
            if result and result.get('tracks'):
                result['context_reasoning'] = f"Búsqueda avanzada para mood {mood_analysis.primary_mood}: {term}"
                return result
        
        return None
    
    def _select_by_user_input(self, user_input: str, context: str) -> Optional[Dict[str, Any]]:
        """Seleccionar basado en input específico del usuario"""
        if not user_input or len(user_input.strip()) < 3:
            return None
        
        user_lower = user_input.lower()
        
        # Detectar artistas favoritos mencionados
        favorite_artists = self.user_preferences.get('favorite_artists', [])
        for artist in favorite_artists:
            if artist.lower() in user_lower:
                return self._get_tracks_from_artist(artist, f"input_match_{artist}")
        
        # Detectar géneros favoritos mencionados
        favorite_genres = self.user_preferences.get('favorite_genres', [])
        for genre in favorite_genres:
            if genre.lower() in user_lower:
                return self._get_tracks_from_genre(genre, f"input_genre_{genre}")
        
        # Detectar mood keywords
        mood_keywords = {
            'party': ['fiesta', 'party', 'bailar', 'celebrar'],
            'chill': ['relajar', 'chill', 'tranquilo', 'suave'],
            'workout': ['ejercicio', 'gym', 'entrenar', 'correr'],
            'sad': ['triste', 'sad', 'llorar', 'melanc'],
            'happy': ['feliz', 'happy', 'alegre', 'contento'],
            'focus': ['concentrar', 'estudiar', 'trabajo', 'focus']
        }
        
        for mood, keywords in mood_keywords.items():
            if any(keyword in user_lower for keyword in keywords):
                return self._select_by_mood(mood, f"input_mood_{mood}")
        
        return None
    
    def _select_by_context(self, user_input: str, context: str) -> Optional[Dict[str, Any]]:
        """Seleccionar basado en contexto/mood actual"""
        
        # Mapear contextos a estrategias
        context_strategies = {
            'party': lambda: self._select_by_mood('party', 'context_party'),
            'chill': lambda: self._select_by_mood('chill', 'context_chill'),
            'workout': lambda: self._select_by_mood('workout', 'context_workout'),
            'focus': lambda: self._select_by_mood('focus', 'context_focus'),
            'morning': lambda: self._select_by_time('morning', 'context_morning'),
            'evening': lambda: self._select_by_time('evening', 'context_evening'),
            'night': lambda: self._select_by_time('night', 'context_night')
        }
        
        if context in context_strategies:
            return context_strategies[context]()
        
        # Auto-detectar contexto por hora
        current_hour = datetime.now().hour
        
        if 6 <= current_hour < 12:  # Mañana
            return self._select_by_time('morning', 'auto_morning')
        elif 12 <= current_hour < 18:  # Tarde
            return self._select_by_time('afternoon', 'auto_afternoon')
        elif 18 <= current_hour < 22:  # Noche
            return self._select_by_time('evening', 'auto_evening')
        else:  # Madrugada
            return self._select_by_time('night', 'auto_night')
    
    def _select_by_preferences(self, user_input: str, context: str) -> Optional[Dict[str, Any]]:
        """Seleccionar basado en preferencias generales del usuario"""
        
        if not self.user_preferences:
            return None
        
        # Estrategia: mezclar artistas favoritos y géneros
        favorite_artists = self.user_preferences.get('favorite_artists', [])[:10]
        favorite_genres = self.user_preferences.get('favorite_genres', [])[:5]
        
        if favorite_artists:
            # 70% probabilidad de elegir artista favorito
            if random.random() < 0.7:
                artist = random.choice(favorite_artists)
                return self._get_tracks_from_artist(artist, 'preferences_artist')
        
        if favorite_genres:
            # 30% probabilidad de elegir por género favorito
            genre = random.choice(favorite_genres)
            return self._get_tracks_from_genre(genre, 'preferences_genre')
        
        return None
    
    def _select_by_recent_history(self, user_input: str, context: str) -> Optional[Dict[str, Any]]:
        """Seleccionar basado en historial reciente (similar pero no igual)"""
        
        recent_tracks = self.user_data.get('recently_played', [])
        if not recent_tracks:
            return None
        
        # Obtener artistas del historial reciente
        recent_artists = list(set([track['artist'] for track in recent_tracks[-20:]]))
        
        if recent_artists:
            # Elegir un artista del historial reciente
            artist = random.choice(recent_artists)
            return self._get_tracks_from_artist(artist, 'recent_history')
        
        return None
    
    def _select_by_mood(self, mood: str, method: str) -> Optional[Dict[str, Any]]:
        """Seleccionar música basada en mood específico"""
        
        # Mapear moods a características de audio y géneros
        mood_mapping = {
            'party': {
                'energy_min': 0.7,
                'danceability_min': 0.6,
                'valence_min': 0.5,
                'genres': ['reggaeton', 'latin', 'pop', 'dance', 'electronic'],
                'search_terms': ['party', 'dance', 'reggaeton hits', 'latin party']
            },
            'chill': {
                'energy_max': 0.5,
                'valence_min': 0.3,
                'acousticness_min': 0.3,
                'genres': ['chill', 'indie', 'acoustic', 'ambient'],
                'search_terms': ['chill music', 'relaxing', 'indie chill', 'acoustic']
            },
            'workout': {
                'energy_min': 0.8,
                'tempo_min': 120,
                'genres': ['hip hop', 'electronic', 'rock', 'pop'],
                'search_terms': ['workout music', 'gym music', 'high energy', 'motivation']
            },
            'sad': {
                'valence_max': 0.4,
                'energy_max': 0.5,
                'genres': ['indie', 'alternative', 'acoustic', 'sad'],
                'search_terms': ['sad songs', 'melancholic', 'heartbreak', 'emotional']
            },
            'happy': {
                'valence_min': 0.7,
                'energy_min': 0.6,
                'genres': ['pop', 'indie pop', 'funk', 'soul'],
                'search_terms': ['happy music', 'feel good', 'upbeat', 'positive vibes']
            },
            'focus': {
                'instrumentalness_min': 0.5,
                'energy_max': 0.6,
                'genres': ['instrumental', 'ambient', 'classical', 'lo-fi'],
                'search_terms': ['focus music', 'study music', 'instrumental', 'ambient']
            }
        }
        
        if mood not in mood_mapping:
            return None
        
        mood_config = mood_mapping[mood]
        
        # Priorizar artistas favoritos que coincidan con el mood
        if self._match_artists_to_mood(mood_config):
            result = self._match_artists_to_mood(mood_config)
            if result:
                result['method'] = f"{method}_matched_artist"
                return result
        
        # Buscar por términos de búsqueda del mood
        search_term = random.choice(mood_config['search_terms'])
        return self._search_tracks_by_term(search_term, f"{method}_search")
    
    def _select_by_time(self, time_period: str, method: str) -> Optional[Dict[str, Any]]:
        """Seleccionar música basada en período del día"""
        
        time_mapping = {
            'morning': ['morning music', 'wake up', 'energizing', 'coffee music'],
            'afternoon': ['afternoon vibes', 'work music', 'productive'],
            'evening': ['evening music', 'dinner music', 'relaxing'],
            'night': ['night music', 'late night', 'chill night', 'ambient']
        }
        
        if time_period not in time_mapping:
            return None
        
        search_terms = time_mapping[time_period]
        search_term = random.choice(search_terms)
        
        return self._search_tracks_by_term(search_term, method)
    
    def _match_artists_to_mood(self, mood_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Encontrar artistas favoritos que coincidan con el mood"""
        
        favorite_artists = self.user_preferences.get('favorite_artists', [])
        favorite_genres = self.user_preferences.get('favorite_genres', [])
        
        # Buscar coincidencias de género
        mood_genres = mood_config.get('genres', [])
        matching_genres = [genre for genre in favorite_genres if any(mg in genre.lower() for mg in mood_genres)]
        
        if matching_genres:
            genre = random.choice(matching_genres)
            return self._get_tracks_from_genre(genre, 'mood_matched_genre')
        
        # Si no hay coincidencias exactas, usar artista favorito genérico
        if favorite_artists:
            artist = random.choice(favorite_artists[:5])  # Top 5
            return self._get_tracks_from_artist(artist, 'mood_fallback_artist')
        
        return None
    
    def _get_tracks_from_artist(self, artist: str, method: str) -> Dict[str, Any]:
        """Obtener tracks de un artista específico"""
        try:
            tracks = self.spotify_controller.search_track(f"artist:{artist}", limit=10)
            
            if tracks:
                return {
                    'tracks': tracks,
                    'method': method,
                    'selection_reason': f"Artista: {artist}",
                    'confidence': 0.9
                }
            else:
                # Fallback: buscar por nombre del artista sin filtro
                tracks = self.spotify_controller.search_track(artist, limit=5)
                return {
                    'tracks': tracks,
                    'method': f"{method}_fallback",
                    'selection_reason': f"Artista (fallback): {artist}",
                    'confidence': 0.7
                } if tracks else {}
                
        except Exception as e:
            print(f"❌ Error buscando artista {artist}: {e}")
            return {}
    
    def _get_tracks_from_genre(self, genre: str, method: str) -> Dict[str, Any]:
        """Obtener tracks de un género específico"""
        try:
            # Buscar por género
            search_terms = [f"genre:{genre}", genre, f"{genre} music"]
            
            for search_term in search_terms:
                tracks = self.spotify_controller.search_track(search_term, limit=10)
                if tracks:
                    return {
                        'tracks': tracks,
                        'method': method,
                        'selection_reason': f"Género: {genre}",
                        'confidence': 0.8
                    }
            
            return {}
                
        except Exception as e:
            print(f"❌ Error buscando género {genre}: {e}")
            return {}
    
    def _search_tracks_by_term(self, search_term: str, method: str) -> Dict[str, Any]:
        """Buscar tracks por término de búsqueda"""
        try:
            tracks = self.spotify_controller.search_track(search_term, limit=10)
            
            if tracks:
                return {
                    'tracks': tracks,
                    'method': method,
                    'selection_reason': f"Búsqueda: {search_term}",
                    'confidence': 0.6
                }
            
            return {}
                
        except Exception as e:
            print(f"❌ Error buscando término {search_term}: {e}")
            return {}
    
    def _select_fallback(self, user_input: str, context: str) -> Optional[Dict[str, Any]]:
        """Selección de respaldo usando datos del usuario"""
        
        # Usar top tracks si están disponibles
        top_tracks = self.user_data.get('top_tracks', [])
        if top_tracks:
            # Mezclar top tracks con algo de aleatoriedad
            selected_tracks = random.sample(top_tracks, min(5, len(top_tracks)))
            
            return {
                'tracks': selected_tracks,
                'method': 'fallback_top_tracks',
                'selection_reason': 'Tus canciones favoritas',
                'confidence': 0.8
            }
        
        # Usar saved tracks si están disponibles
        saved_tracks = self.user_data.get('saved_tracks', [])
        if saved_tracks:
            selected_tracks = random.sample(saved_tracks, min(5, len(saved_tracks)))
            
            return {
                'tracks': selected_tracks,
                'method': 'fallback_saved_tracks',
                'selection_reason': 'Tu biblioteca guardada',
                'confidence': 0.7
            }
        
        return None
    
    def _select_basic_fallback(self) -> Dict[str, Any]:
        """Selección básica de respaldo cuando todo falla"""
        
        # Términos genéricos populares
        fallback_terms = [
            'top hits', 'popular music', 'trending', 
            'latin hits', 'pop music', 'rock hits'
        ]
        
        for term in fallback_terms:
            try:
                tracks = self.spotify_controller.search_track(term, limit=5)
                if tracks:
                    return {
                        'tracks': tracks,
                        'method': 'basic_fallback',
                        'selection_reason': f'Música popular: {term}',
                        'confidence': 0.3
                    }
            except:
                continue
        
        # Último recurso
        return {
            'tracks': [],
            'method': 'empty_fallback',
            'selection_reason': 'No se pudo encontrar música',
            'confidence': 0.0
        }
    
    def get_recommended_track(self, user_input: str = "", context: str = "general", 
                             conversation_history: List[Dict] = None) -> Optional[Dict[str, Any]]:
        """Obtener una sola canción recomendada (la mejor opción)"""
        
        selection_result = self.select_music_intelligently(user_input, context, conversation_history)
        
        if selection_result and selection_result.get('tracks'):
            # Elegir la mejor canción de la selección
            tracks = selection_result['tracks']
            best_track = tracks[0]  # Primera canción (generalmente la más relevante)
            
            return {
                'track': best_track,
                'reason': selection_result.get('selection_reason', 'Selección inteligente'),
                'method': selection_result.get('method', 'unknown'),
                'confidence': selection_result.get('confidence', 0.5)
            }
        
        return None
    
    def refresh_user_data(self, force: bool = False):
        """Actualizar datos del usuario"""
        print("🔄 Actualizando datos del usuario...")
        self.user_data = self.data_extractor.extract_all_user_data(force_refresh=force)
        self.user_preferences = self.data_extractor.generate_user_preferences(self.user_data)
        print("✅ Datos actualizados")
    
    def get_selection_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del selector"""
        return {
            'has_preferences': bool(self.user_preferences),
            'has_user_data': bool(self.user_data),
            'favorite_artists_count': len(self.user_preferences.get('favorite_artists', [])),
            'favorite_genres_count': len(self.user_preferences.get('favorite_genres', [])),
            'recent_tracks_count': len(self.user_data.get('recently_played', [])),
            'top_tracks_count': len(self.user_data.get('top_tracks', [])),
            'saved_tracks_count': len(self.user_data.get('saved_tracks', []))
        }

def test_intelligent_selector():
    """Función de prueba para el selector inteligente"""
    print("🧪 TESTING: Intelligent Music Selector")
    print("=" * 50)
    
    selector = IntelligentMusicSelector()
    
    # Mostrar estadísticas
    stats = selector.get_selection_stats()
    print(f"📊 ESTADÍSTICAS DEL SELECTOR:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Pruebas de selección
    test_cases = [
        ("", "general"),
        ("pon música", "general"),
        ("algo para la fiesta", "party"),
        ("música relajante", "chill"),
        ("para entrenar", "workout"),
        ("bad bunny", "general"),
        ("reggaeton", "general")
    ]
    
    print(f"\n🎵 PRUEBAS DE SELECCIÓN:")
    for user_input, context in test_cases:
        print(f"\n🧪 Input: '{user_input}' (contexto: {context})")
        
        try:
            # Simular historial de conversación para pruebas
            mock_history = [
                {"user": "Hola Roxy", "roxy": "¡Hola! ¿En qué puedo ayudarte?"},
                {"user": user_input, "roxy": ""}
            ]
            
            recommendation = selector.get_recommended_track(user_input, context, mock_history)
            
            if recommendation:
                track = recommendation['track']
                print(f"   ✅ Recomendación: {track.get('artist', 'N/A')} - {track.get('name', 'N/A')}")
                print(f"   📝 Razón: {recommendation.get('reason', 'N/A')}")
                print(f"   🔧 Método: {recommendation.get('method', 'N/A')}")
                print(f"   🎯 Confianza: {recommendation.get('confidence', 0):.2f}")
            else:
                print("   ❌ No se pudo generar recomendación")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_intelligent_selector()
