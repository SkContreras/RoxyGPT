"""
DJ Narrator Mode - Estilo DJ Levi
================================
Convierte a Roxy en un DJ narrador profesional con personalidad carismática
"""

import random
import time
from typing import Dict, List, Optional
from datetime import datetime

class DJNarratorMode:
    """Modo DJ Narrador para Roxy - Estilo DJ Levi"""
    
    def __init__(self):
        """Inicializar modo DJ narrador"""
        self.dj_name = "DJ Roxy"
        self.session_active = False
        self.current_mood = "energetic"  # energetic, chill, party, romantic, workout
        self.track_count = 0
        self.session_start_time = None
        
        # Personalidad DJ - FRASES CORTAS (máximo 8 palabras)
        self.dj_phrases = {
            "intro": [
                "DJ Roxy en cabina",
                "Música en vivo con Roxy",
                "Aquí DJ Roxy",
                "Roxy al aire"
            ],
            "transitions": [
                "Ahora viene fuego",
                "Siguiente tema",
                "Y ahora...",
                "Continuamos"
            ],
            "track_intro": [
                "{artist} - {song}",
                "Suena {artist}",
                "{artist} con {song}",
                "Ahora {artist}"
            ],
            "energy_boost": [
                "¡Puro fuego!",
                "¡Está brutal!",
                "¡Qué rola!",
                "¡Increíble!",
                "¡Así me gusta!"
            ],
            "time_checks": [
                "{time} en punto",
                "Son las {time}",
                "{time} horas"
            ],
            "mood_comments": {
                "energetic": [
                    "¡Pura energía!",
                    "¡Con actitud!",
                    "¡Arriba el ánimo!"
                ],
                "chill": [
                    "Música relajante",
                    "Sonidos suaves",
                    "Para descansar"
                ],
                "party": [
                    "¡A bailar!",
                    "¡Fiesta total!",
                    "¡Party time!"
                ],
                "romantic": [
                    "Música romántica",
                    "Para el corazón",
                    "Sonidos especiales"
                ],
                "workout": [
                    "¡A entrenar!",
                    "¡Con energía!",
                    "¡Dale duro!"
                ]
            },
            "requests": [
                "¡Buena elección!",
                "¡Excelente!",
                "¡Me gusta!",
                "¡Perfecto!"
            ],
            "outros": [
                "Sesión terminada",
                "Hasta la próxima",
                "Nos vemos",
                "¡Gracias!"
            ]
        }
        
        # Comentarios por género - CORTOS
        self.genre_comments = {
            "reggaeton": [
                "¡Puro reggaeton!",
                "¡A perrear!",
                "¡Ritmo latino!"
            ],
            "pop": [
                "¡Pop hits!",
                "¡Música pop!",
                "¡Éxito total!"
            ],
            "rock": [
                "¡Rock and roll!",
                "¡Puro rock!",
                "¡Guitarra brutal!"
            ],
            "electronic": [
                "¡Electrónica!",
                "¡Beats perfectos!",
                "¡Sonidos futuristas!"
            ]
        }
    
    def start_session(self, mood: str = "energetic"):
        """Iniciar sesión de DJ narrador"""
        self.session_active = True
        self.current_mood = mood
        self.track_count = 0
        self.session_start_time = datetime.now()
        
        intro = random.choice(self.dj_phrases["intro"])
        mood_comment = random.choice(self.dj_phrases["mood_comments"][mood])
        
        return f"{intro} - {mood_comment}"
    
    def introduce_track(self, artist: str, song: str, genre: str = None) -> str:
        """Presentar una canción como DJ narrador - MÁXIMO 8 PALABRAS"""
        if not self.session_active:
            return ""
        
        self.track_count += 1
        
        # Solo intro de la canción (máximo 6 palabras)
        track_intro = random.choice(self.dj_phrases["track_intro"])
        intro_text = track_intro.format(artist=artist, song=song)
        
        # Ocasionalmente agregar comentario corto (30% probabilidad)
        if random.random() < 0.3:
            if genre and genre.lower() in self.genre_comments:
                genre_comment = random.choice(self.genre_comments[genre.lower()])
                return f"{intro_text} - {genre_comment}"
            else:
                energy_comment = random.choice(self.dj_phrases["energy_boost"])
                return f"{intro_text} - {energy_comment}"
        
        return intro_text
    
    def transition_comment(self) -> str:
        """Comentario de transición entre canciones - MÁXIMO 4 PALABRAS"""
        if not self.session_active:
            return ""
        
        # Solo transición simple
        return random.choice(self.dj_phrases["transitions"])
    
    def handle_user_request(self, user_input: str, artist: str, song: str) -> str:
        """Manejar petición del usuario como DJ - MÁXIMO 4 PALABRAS"""
        user_lower = user_input.lower()
        
        # Cambiar mood según contexto
        if "fiesta" in user_lower or "party" in user_lower:
            self.current_mood = "party"
        elif "relajar" in user_lower or "chill" in user_lower:
            self.current_mood = "chill"
        elif "ejercicio" in user_lower or "gym" in user_lower:
            self.current_mood = "workout"
        
        # Solo respuesta corta
        return random.choice(self.dj_phrases["requests"])
    
    def get_mood_intro(self, mood: str) -> str:
        """Obtener introducción específica por estado de ánimo - CORTA"""
        mood_intros = {
            "energetic": "¡Pura energía!",
            "chill": "Sonidos relajantes",
            "party": "¡A bailar!",
            "romantic": "Música romántica",
            "workout": "¡A entrenar!"
        }
        
        return mood_intros.get(mood, mood_intros["energetic"])
    
    def session_stats(self) -> str:
        """Estadísticas de la sesión como DJ - CORTA"""
        if not self.session_active or not self.session_start_time:
            return "Sin sesión activa"
        
        duration = datetime.now() - self.session_start_time
        minutes = int(duration.total_seconds() // 60)
        
        return f"{self.track_count} rolas - {minutes} minutos"
    
    def end_session(self) -> str:
        """Terminar sesión de DJ narrador"""
        if not self.session_active:
            return "No hay sesión activa"
        
        outro = random.choice(self.dj_phrases["outros"])
        stats = self.session_stats()
        
        self.session_active = False
        self.track_count = 0
        self.session_start_time = None
        
        return f"{stats} {outro}"
    
    def get_current_vibe(self) -> str:
        """Obtener comentario del ambiente actual"""
        vibe_comments = {
            "energetic": "¡El ambiente está súper energético!",
            "chill": "Ambiente perfecto para relajarse",
            "party": "¡La fiesta está en su mejor momento!",
            "romantic": "Ambiente romántico y especial",
            "workout": "¡Energía pura para entrenar!"
        }
        
        base_comment = vibe_comments.get(self.current_mood, "¡El ambiente está increíble!")
        
        if self.track_count > 0:
            return f"{base_comment} ¡Ya llevamos {self.track_count} rolas de pura calidad!"
        
        return base_comment
    
    def special_announcements(self) -> Optional[str]:
        """Anuncios especiales ocasionales"""
        if not self.session_active:
            return None
        
        # Solo hacer anuncios ocasionalmente
        if random.random() > 0.15:  # 15% probabilidad
            return None
        
        announcements = [
            "¡Recuerden seguir a DJ Roxy para más música increíble!",
            "¡Si les está gustando la música, compartan con sus amigos!",
            "¡Esta es su casa musical, siempre bienvenidos!",
            "¡Gracias por confiar en DJ Roxy para su música!",
            "¡La mejor música siempre aquí con ustedes!"
        ]
        
        return random.choice(announcements)

# Integración con el sistema principal
def integrate_dj_narrator_with_spotify(spotify_controller, dj_narrator):
    """Integrar DJ narrador con controlador Spotify"""
    
    def enhanced_play_music(search_query: str, mood: str = "energetic"):
        """Reproducir música con narración DJ"""
        
        # Iniciar sesión si no está activa
        if not dj_narrator.session_active:
            intro = dj_narrator.start_session(mood)
            print(f"🎤 DJ Roxy: {intro}")
        
        # Buscar y reproducir
        result = spotify_controller.play_music_advanced(search_query)
        
        if result['success'] and result.get('track_info'):
            track = result['track_info']
            
            # Narración del track
            narration = dj_narrator.introduce_track(
                artist=track['artist'],
                song=track['name'],
                genre="reggaeton" if "reggaeton" in search_query.lower() else None
            )
            
            print(f"🎤 DJ Roxy: {narration}")
            
            # Anuncio especial ocasional
            special = dj_narrator.special_announcements()
            if special:
                print(f"🎤 DJ Roxy: {special}")
        
        return result
    
    return enhanced_play_music

# Función para testing
def test_dj_narrator():
    """Test del modo DJ narrador"""
    print("🎤 TEST: DJ NARRATOR MODE")
    print("=" * 40)
    
    dj = DJNarratorMode()
    
    # Iniciar sesión
    print("🎤 " + dj.start_session("party"))
    print()
    
    # Simular varias canciones
    tracks = [
        ("Bad Bunny", "Tití Me Preguntó", "reggaeton"),
        ("Fuerza Regida", "Tu Boda", "regional"),
        ("Karol G", "Provenza", "reggaeton"),
        ("The Weeknd", "Blinding Lights", "pop")
    ]
    
    for artist, song, genre in tracks:
        time.sleep(1)
        print("🎤 " + dj.transition_comment())
        print("🎤 " + dj.introduce_track(artist, song, genre))
        print()
    
    # Stats y cierre
    print("🎤 " + dj.session_stats())
    print("🎤 " + dj.end_session())

if __name__ == "__main__":
    test_dj_narrator()
