"""
Auto DJ Mode - DJ Automático Inteligente
========================================
DJ que reproduce música automáticamente, evita repeticiones y se adapta al contexto
"""

import time
import random
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from music_history_manager import MusicHistoryManager
from intelligent_music_selector import IntelligentMusicSelector
from spotify_controller_unified import SpotifyControllerUnified
from dj_narrator_mode import DJNarratorMode

@dataclass
class DJSession:
    """Información de una sesión de DJ automático"""
    start_time: datetime
    mood: str
    tracks_played: int = 0
    total_duration: int = 0  # en segundos
    is_active: bool = True
    auto_mood_changes: bool = True
    user_interactions: int = 0

class AutoDJMode:
    """DJ Automático que reproduce música continuamente sin repetir"""
    
    def __init__(self, spotify_controller: SpotifyControllerUnified = None, 
                 intelligent_selector: IntelligentMusicSelector = None,
                 dj_narrator: DJNarratorMode = None):
        """Inicializar DJ automático"""
        
        # Componentes principales
        self.spotify_controller = spotify_controller or SpotifyControllerUnified()
        self.intelligent_selector = intelligent_selector or IntelligentMusicSelector()
        self.dj_narrator = dj_narrator or DJNarratorMode()
        self.history_manager = MusicHistoryManager()
        
        # Estado del DJ
        self.current_session: Optional[DJSession] = None
        self.is_running = False
        self.auto_play_thread: Optional[threading.Thread] = None
        
        # Configuración
        self.track_duration_estimate = 210  # 3.5 minutos promedio por canción
        self.pause_between_tracks = 5  # 5 segundos entre canciones
        self.mood_change_probability = 0.15  # 15% probabilidad de cambiar mood
        self.mood_change_interval = 6  # Cambiar mood cada 6 canciones
        
        # Moods disponibles y sus contextos
        self.available_moods = {
            "energetic": {
                "contexts": ["general", "morning", "workout"],
                "keywords": ["energetic", "upbeat", "motivational", "high energy"],
                "weight": 1.0
            },
            "chill": {
                "contexts": ["chill", "evening", "relax"],
                "keywords": ["chill", "relaxing", "ambient", "lo-fi", "calm"],
                "weight": 1.0
            },
            "party": {
                "contexts": ["party", "dance", "celebration"],
                "keywords": ["party", "dance", "reggaeton", "latin hits", "club music"],
                "weight": 0.8
            },
            "focus": {
                "contexts": ["focus", "work", "study"],
                "keywords": ["instrumental", "focus music", "study music", "ambient"],
                "weight": 0.6
            },
            "romantic": {
                "contexts": ["romantic", "dinner", "love"],
                "keywords": ["romantic", "love songs", "ballads", "soft music"],
                "weight": 0.5
            }
        }
        
        # Callbacks para eventos
        self.on_track_start: Optional[Callable] = None
        self.on_track_end: Optional[Callable] = None
        self.on_mood_change: Optional[Callable] = None
        self.on_session_end: Optional[Callable] = None
        
        print("🤖 Auto DJ Mode inicializado")
    
    def start_auto_session(self, initial_mood: str = "auto", duration_minutes: int = 0):
        """Iniciar sesión de DJ automático"""
        if self.is_running:
            print("⚠️ Ya hay una sesión activa")
            return False
        
        # Determinar mood inicial
        if initial_mood == "auto":
            initial_mood = self._determine_mood_by_time()
        
        # Crear nueva sesión
        self.current_session = DJSession(
            start_time=datetime.now(),
            mood=initial_mood,
            auto_mood_changes=True
        )
        
        # Iniciar narrador DJ
        dj_intro = self.dj_narrator.start_session(initial_mood)
        print(f"🎤 {dj_intro}")
        
        # Configurar duración si se especifica
        if duration_minutes > 0:
            self.session_end_time = datetime.now() + timedelta(minutes=duration_minutes)
        else:
            self.session_end_time = None
        
        # Iniciar thread de reproducción automática
        self.is_running = True
        self.auto_play_thread = threading.Thread(target=self._auto_play_loop, daemon=True)
        self.auto_play_thread.start()
        
        print(f"🚀 DJ Automático iniciado - Mood: {initial_mood}")
        if duration_minutes > 0:
            print(f"⏰ Duración programada: {duration_minutes} minutos")
        
        return True
    
    def stop_auto_session(self):
        """Detener sesión de DJ automático"""
        if not self.is_running:
            print("⚠️ No hay sesión activa")
            return
        
        self.is_running = False
        
        if self.current_session:
            # Finalizar narrador DJ
            dj_outro = self.dj_narrator.end_session()
            print(f"🎤 {dj_outro}")
            
            # Mostrar estadísticas de sesión
            duration = datetime.now() - self.current_session.start_time
            duration_minutes = int(duration.total_seconds() // 60)
            
            print(f"📊 SESIÓN TERMINADA:")
            print(f"   ⏱️ Duración: {duration_minutes} minutos")
            print(f"   🎵 Canciones: {self.current_session.tracks_played}")
            print(f"   👤 Interacciones: {self.current_session.user_interactions}")
            
            # Callback de fin de sesión
            if self.on_session_end:
                self.on_session_end(self.current_session)
        
        self.current_session = None
        print("⏹️ DJ Automático detenido")
    
    def _auto_play_loop(self):
        """Loop principal de reproducción automática"""
        consecutive_failures = 0
        max_failures = 3
        
        while self.is_running:
            try:
                # Verificar si debe terminar por tiempo
                if self.session_end_time and datetime.now() >= self.session_end_time:
                    print("⏰ Tiempo de sesión completado")
                    break
                
                # Obtener siguiente canción
                next_track = self._get_next_track()
                
                if next_track:
                    # Reproducir canción
                    success = self._play_track_auto(next_track)
                    
                    if success:
                        consecutive_failures = 0
                        
                        # Actualizar estadísticas de sesión
                        if self.current_session:
                            self.current_session.tracks_played += 1
                        
                        # Esperar duración estimada de la canción
                        time.sleep(self.track_duration_estimate)
                        
                        # Pausa entre canciones
                        if self.pause_between_tracks > 0:
                            time.sleep(self.pause_between_tracks)
                    else:
                        consecutive_failures += 1
                        print(f"⚠️ Fallo en reproducción ({consecutive_failures}/{max_failures})")
                        
                        if consecutive_failures >= max_failures:
                            print("❌ Demasiados fallos consecutivos, deteniendo DJ automático")
                            break
                        
                        # Esperar antes de reintentar
                        time.sleep(10)
                else:
                    print("⚠️ No se pudo obtener siguiente canción")
                    time.sleep(30)  # Esperar antes de reintentar
                
                # Considerar cambio de mood
                self._consider_mood_change()
                
            except Exception as e:
                print(f"❌ Error en loop automático: {e}")
                time.sleep(10)
        
        # Detener sesión
        self.is_running = False
    
    def _get_next_track(self) -> Optional[Dict[str, Any]]:
        """Obtener la siguiente canción a reproducir"""
        if not self.current_session:
            return None
        
        try:
            # Obtener recomendación inteligente basada en el mood actual
            mood_context = self.current_session.mood
            search_query = self._get_mood_search_query(mood_context)
            
            print(f"🧠 Buscando música para mood '{mood_context}': {search_query}")
            
            # Usar selector inteligente
            recommendation = self.intelligent_selector.get_recommended_track(search_query, mood_context)
            
            if recommendation and recommendation.get('track'):
                track = recommendation['track']
                
                # Verificar si la canción ya fue reproducida recientemente
                if self.history_manager.is_track_recently_played(track.get('uri', '')):
                    print(f"⏭️ Canción reciente, buscando alternativa...")
                    
                    # Intentar obtener múltiples opciones y filtrar
                    selection_result = self.intelligent_selector.select_music_intelligently(search_query, mood_context)
                    
                    if selection_result and selection_result.get('tracks'):
                        filtered_tracks = self.history_manager.filter_tracks_by_history(selection_result['tracks'])
                        
                        if filtered_tracks:
                            # Elegir aleatoriamente de las opciones filtradas
                            track = random.choice(filtered_tracks)
                            recommendation['track'] = track
                            recommendation['reason'] = f"Alternativa filtrada: {selection_result.get('selection_reason', '')}"
                
                return recommendation
            else:
                print("⚠️ No se pudo obtener recomendación inteligente")
                return None
                
        except Exception as e:
            print(f"❌ Error obteniendo siguiente canción: {e}")
            return None
    
    def _play_track_auto(self, recommendation: Dict[str, Any]) -> bool:
        """Reproducir canción automáticamente"""
        try:
            track = recommendation.get('track', {})
            track_uri = track.get('uri', '')
            
            if not track_uri:
                print("❌ No se encontró URI de la canción")
                return False
            
            # Narración del DJ
            if self.dj_narrator.session_active:
                narration = self.dj_narrator.introduce_track(
                    artist=track.get('artist', 'Artista Desconocido'),
                    song=track.get('name', 'Canción Sin Nombre'),
                    genre=track.get('genre')
                )
                
                if narration:
                    print(f"🎤 DJ Roxy: {narration}")
            
            # Callback de inicio de canción
            if self.on_track_start:
                self.on_track_start(track, recommendation.get('reason', ''))
            
            # Reproducir usando controlador unificado
            result = self.spotify_controller.play_track_by_uri(track_uri, track)
            
            if result and result.get('success'):
                print(f"🔧 Roxy: 🎵 ¡Reproduciendo! {track.get('artist', 'N/A')} - {track.get('name', 'N/A')}")
                
                # Agregar al historial
                self.history_manager.add_played_track(
                    track_info=track,
                    mood_context=self.current_session.mood if self.current_session else None,
                    user_requested=False
                )
                
                # Callback de fin de canción
                if self.on_track_end:
                    self.on_track_end(track)
                
                return True
            else:
                print(f"❌ Error reproduciendo: {result.get('error', 'Error desconocido')}")
                return False
                
        except Exception as e:
            print(f"❌ Error en reproducción automática: {e}")
            return False
    
    def _get_mood_search_query(self, mood: str) -> str:
        """Obtener query de búsqueda basado en el mood"""
        if mood not in self.available_moods:
            mood = "energetic"
        
        mood_config = self.available_moods[mood]
        keywords = mood_config.get('keywords', [])
        
        if keywords:
            return random.choice(keywords)
        else:
            return mood
    
    def _determine_mood_by_time(self) -> str:
        """Determinar mood automáticamente basado en la hora"""
        current_hour = datetime.now().hour
        
        if 6 <= current_hour < 10:  # Mañana
            return random.choice(["energetic", "chill"])
        elif 10 <= current_hour < 14:  # Media mañana
            return "energetic"
        elif 14 <= current_hour < 18:  # Tarde
            return random.choice(["energetic", "chill", "focus"])
        elif 18 <= current_hour < 22:  # Noche
            return random.choice(["chill", "party", "romantic"])
        else:  # Madrugada
            return random.choice(["chill", "focus"])
    
    def _consider_mood_change(self):
        """Considerar cambiar el mood actual"""
        if not self.current_session or not self.current_session.auto_mood_changes:
            return
        
        # Cambiar mood cada cierto número de canciones
        if (self.current_session.tracks_played % self.mood_change_interval == 0 and 
            self.current_session.tracks_played > 0):
            
            if random.random() < self.mood_change_probability:
                self._change_mood()
    
    def _change_mood(self):
        """Cambiar el mood actual"""
        if not self.current_session:
            return
        
        current_mood = self.current_session.mood
        
        # Elegir nuevo mood diferente al actual
        available_moods = [mood for mood in self.available_moods.keys() if mood != current_mood]
        
        # Ponderar moods por hora del día
        weighted_moods = []
        current_hour = datetime.now().hour
        
        for mood in available_moods:
            weight = self.available_moods[mood]['weight']
            
            # Ajustar peso según hora
            if 22 <= current_hour or current_hour < 6:  # Madrugada
                if mood in ["chill", "focus"]:
                    weight *= 2
                elif mood == "party":
                    weight *= 0.3
            elif 18 <= current_hour < 22:  # Noche
                if mood in ["party", "romantic"]:
                    weight *= 1.5
            
            # Agregar mood según su peso
            for _ in range(int(weight * 10)):
                weighted_moods.append(mood)
        
        if weighted_moods:
            new_mood = random.choice(weighted_moods)
            old_mood = self.current_session.mood
            self.current_session.mood = new_mood
            
            # Narración del cambio
            mood_intro = self.dj_narrator.get_mood_intro(new_mood)
            print(f"🎤 DJ Roxy: {mood_intro}")
            
            print(f"🎭 Mood cambiado: {old_mood} → {new_mood}")
            
            # Callback de cambio de mood
            if self.on_mood_change:
                self.on_mood_change(old_mood, new_mood)
    
    def handle_user_request(self, user_input: str, track_info: Dict[str, Any] = None):
        """Manejar petición del usuario durante sesión automática"""
        if not self.current_session:
            return
        
        self.current_session.user_interactions += 1
        
        # Narración del DJ para petición del usuario
        if track_info:
            dj_response = self.dj_narrator.handle_user_request(
                user_input, 
                track_info.get('artist', ''), 
                track_info.get('name', '')
            )
            
            if dj_response:
                print(f"🎤 DJ Roxy: {dj_response}")
        
        # Detectar cambio de mood en la petición
        user_lower = user_input.lower()
        mood_keywords = {
            "party": ["fiesta", "party", "bailar", "reggaeton"],
            "chill": ["relajar", "chill", "tranquilo", "suave"],
            "energetic": ["energía", "activo", "motivar", "alegre"],
            "romantic": ["romántico", "amor", "love", "romantic"],
            "focus": ["concentrar", "estudiar", "trabajo", "instrumental"]
        }
        
        for mood, keywords in mood_keywords.items():
            if any(keyword in user_lower for keyword in keywords):
                if mood != self.current_session.mood:
                    old_mood = self.current_session.mood
                    self.current_session.mood = mood
                    print(f"🎭 Mood cambiado por petición del usuario: {old_mood} → {mood}")
                break
    
    def get_session_status(self) -> Dict[str, Any]:
        """Obtener estado actual de la sesión"""
        if not self.current_session:
            return {"active": False}
        
        duration = datetime.now() - self.current_session.start_time
        duration_minutes = int(duration.total_seconds() // 60)
        
        return {
            "active": self.is_running,
            "mood": self.current_session.mood,
            "tracks_played": self.current_session.tracks_played,
            "duration_minutes": duration_minutes,
            "user_interactions": self.current_session.user_interactions,
            "auto_mood_changes": self.current_session.auto_mood_changes,
            "session_start": self.current_session.start_time.isoformat()
        }
    
    def set_mood(self, new_mood: str):
        """Cambiar mood manualmente"""
        if not self.current_session:
            print("⚠️ No hay sesión activa")
            return False
        
        if new_mood not in self.available_moods:
            print(f"⚠️ Mood '{new_mood}' no disponible. Opciones: {list(self.available_moods.keys())}")
            return False
        
        old_mood = self.current_session.mood
        self.current_session.mood = new_mood
        
        # Narración del cambio
        mood_intro = self.dj_narrator.get_mood_intro(new_mood)
        print(f"🎤 DJ Roxy: {mood_intro}")
        
        print(f"🎭 Mood cambiado manualmente: {old_mood} → {new_mood}")
        return True
    
    def toggle_auto_mood_changes(self):
        """Activar/desactivar cambios automáticos de mood"""
        if not self.current_session:
            return False
        
        self.current_session.auto_mood_changes = not self.current_session.auto_mood_changes
        status = "activados" if self.current_session.auto_mood_changes else "desactivados"
        print(f"🎭 Cambios automáticos de mood {status}")
        return self.current_session.auto_mood_changes

def test_auto_dj():
    """Test del DJ automático"""
    print("🤖 TEST: Auto DJ Mode")
    print("=" * 40)
    
    # Crear instancia (sin controladores reales para test)
    auto_dj = AutoDJMode()
    
    # Mostrar moods disponibles
    print("🎭 Moods disponibles:")
    for mood, config in auto_dj.available_moods.items():
        print(f"   {mood}: {config['keywords'][:2]}...")
    
    # Test de determinación de mood por tiempo
    current_mood = auto_dj._determine_mood_by_time()
    print(f"\n🕐 Mood sugerido por hora actual: {current_mood}")
    
    # Test de queries de búsqueda
    print(f"\n🔍 Queries de búsqueda por mood:")
    for mood in auto_dj.available_moods.keys():
        query = auto_dj._get_mood_search_query(mood)
        print(f"   {mood}: '{query}'")
    
    print(f"\n✅ Auto DJ Mode listo para usar")

if __name__ == "__main__":
    test_auto_dj()
