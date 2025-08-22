"""
Music History Manager - Sistema de Historial Musical
===================================================
Gestiona el historial de canciones reproducidas para evitar repeticiones
y mejorar la experiencia del DJ automático
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict

@dataclass
class PlayedTrack:
    """Información de una canción reproducida"""
    uri: str
    name: str
    artist: str
    album: Optional[str] = None
    genre: Optional[str] = None
    played_at: float = None  # timestamp
    mood_context: Optional[str] = None
    user_requested: bool = False  # True si fue pedida por el usuario
    
    def __post_init__(self):
        if self.played_at is None:
            self.played_at = time.time()

class MusicHistoryManager:
    """Gestor del historial musical para evitar repeticiones"""
    
    def __init__(self, history_file: str = "music_history.json"):
        """Inicializar gestor de historial"""
        self.history_file = history_file
        self.played_tracks: List[PlayedTrack] = []
        self.max_history_size = 1000  # Máximo 1000 canciones en historial
        self.avoid_repeat_hours = 4   # No repetir canciones en las últimas 4 horas
        self.avoid_artist_minutes = 30  # No repetir artista en los últimos 30 minutos
        
        # Cargar historial existente
        self._load_history()
        
        print(f"🎵 Music History Manager inicializado - {len(self.played_tracks)} canciones en historial")
    
    def _load_history(self):
        """Cargar historial desde archivo"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Convertir diccionarios a PlayedTrack objects
                for track_data in data:
                    track = PlayedTrack(**track_data)
                    self.played_tracks.append(track)
                
                # Limpiar historial viejo (más de 7 días)
                self._cleanup_old_history()
                
                print(f"✅ Historial musical cargado: {len(self.played_tracks)} canciones")
            else:
                print("📝 Creando nuevo historial musical")
                
        except Exception as e:
            print(f"⚠️ Error cargando historial: {e}")
            self.played_tracks = []
    
    def _save_history(self):
        """Guardar historial a archivo"""
        try:
            # Convertir PlayedTrack objects a diccionarios
            data = [asdict(track) for track in self.played_tracks]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Error guardando historial: {e}")
    
    def _cleanup_old_history(self):
        """Limpiar canciones muy viejas del historial"""
        cutoff_time = time.time() - (7 * 24 * 3600)  # 7 días atrás
        
        original_count = len(self.played_tracks)
        self.played_tracks = [
            track for track in self.played_tracks 
            if track.played_at > cutoff_time
        ]
        
        # Limitar tamaño máximo
        if len(self.played_tracks) > self.max_history_size:
            self.played_tracks = self.played_tracks[-self.max_history_size:]
        
        cleaned_count = original_count - len(self.played_tracks)
        if cleaned_count > 0:
            print(f"🧹 Limpiadas {cleaned_count} canciones viejas del historial")
    
    def add_played_track(self, track_info: Dict[str, Any], mood_context: str = None, user_requested: bool = False):
        """Agregar canción al historial"""
        try:
            played_track = PlayedTrack(
                uri=track_info.get('uri', ''),
                name=track_info.get('name', ''),
                artist=track_info.get('artist', ''),
                album=track_info.get('album'),
                genre=track_info.get('genre'),
                mood_context=mood_context,
                user_requested=user_requested
            )
            
            self.played_tracks.append(played_track)
            self._save_history()
            
            print(f"📝 Agregado al historial: {played_track.artist} - {played_track.name}")
            
        except Exception as e:
            print(f"❌ Error agregando al historial: {e}")
    
    def is_track_recently_played(self, track_uri: str) -> bool:
        """Verificar si una canción fue reproducida recientemente"""
        cutoff_time = time.time() - (self.avoid_repeat_hours * 3600)
        
        for track in self.played_tracks:
            if track.uri == track_uri and track.played_at > cutoff_time:
                return True
        
        return False
    
    def is_artist_recently_played(self, artist_name: str) -> bool:
        """Verificar si un artista fue reproducido recientemente"""
        cutoff_time = time.time() - (self.avoid_artist_minutes * 60)
        
        for track in self.played_tracks:
            if track.artist.lower() == artist_name.lower() and track.played_at > cutoff_time:
                return True
        
        return False
    
    def get_recently_played_uris(self, hours: int = 4) -> Set[str]:
        """Obtener URIs de canciones reproducidas en las últimas X horas"""
        cutoff_time = time.time() - (hours * 3600)
        
        recent_uris = set()
        for track in self.played_tracks:
            if track.played_at > cutoff_time:
                recent_uris.add(track.uri)
        
        return recent_uris
    
    def get_recently_played_artists(self, minutes: int = 30) -> Set[str]:
        """Obtener artistas reproducidos en los últimos X minutos"""
        cutoff_time = time.time() - (minutes * 60)
        
        recent_artists = set()
        for track in self.played_tracks:
            if track.played_at > cutoff_time:
                recent_artists.add(track.artist.lower())
        
        return recent_artists
    
    def filter_tracks_by_history(self, tracks: List[Dict[str, Any]], strict_mode: bool = False) -> List[Dict[str, Any]]:
        """Filtrar canciones basado en el historial para evitar repeticiones"""
        if not tracks:
            return tracks
        
        # Obtener canciones y artistas recientes
        recent_uris = self.get_recently_played_uris(self.avoid_repeat_hours)
        recent_artists = self.get_recently_played_artists(self.avoid_artist_minutes if not strict_mode else 60)
        
        filtered_tracks = []
        
        for track in tracks:
            track_uri = track.get('uri', '')
            track_artist = track.get('artist', '').lower()
            
            # Verificar si la canción específica fue reproducida recientemente
            if track_uri in recent_uris:
                continue
            
            # Verificar si el artista fue reproducido recientemente
            if track_artist in recent_artists:
                continue
            
            filtered_tracks.append(track)
        
        print(f"🎵 Filtrado por historial: {len(tracks)} → {len(filtered_tracks)} canciones")
        
        # Si quedaron muy pocas canciones, relajar las restricciones
        if len(filtered_tracks) < 3 and len(tracks) > 10:
            print("🔄 Muy pocas canciones después del filtro, relajando restricciones...")
            recent_uris = self.get_recently_played_uris(1)  # Solo última hora
            recent_artists = self.get_recently_played_artists(10)  # Solo últimos 10 minutos
            
            filtered_tracks = []
            for track in tracks:
                track_uri = track.get('uri', '')
                track_artist = track.get('artist', '').lower()
                
                if track_uri not in recent_uris and track_artist not in recent_artists:
                    filtered_tracks.append(track)
        
        return filtered_tracks if filtered_tracks else tracks[:5]  # Mínimo 5 canciones
    
    def get_history_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del historial"""
        if not self.played_tracks:
            return {"total_tracks": 0}
        
        # Contar por artistas
        artist_counts = {}
        genre_counts = {}
        mood_counts = {}
        
        recent_cutoff = time.time() - (24 * 3600)  # Últimas 24 horas
        recent_tracks = 0
        user_requested_count = 0
        
        for track in self.played_tracks:
            # Artistas
            artist_counts[track.artist] = artist_counts.get(track.artist, 0) + 1
            
            # Géneros
            if track.genre:
                genre_counts[track.genre] = genre_counts.get(track.genre, 0) + 1
            
            # Moods
            if track.mood_context:
                mood_counts[track.mood_context] = mood_counts.get(track.mood_context, 0) + 1
            
            # Recientes
            if track.played_at > recent_cutoff:
                recent_tracks += 1
            
            # Pedidas por usuario
            if track.user_requested:
                user_requested_count += 1
        
        # Top artistas
        top_artists = sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        top_moods = sorted(mood_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "total_tracks": len(self.played_tracks),
            "recent_tracks_24h": recent_tracks,
            "user_requested": user_requested_count,
            "auto_selected": len(self.played_tracks) - user_requested_count,
            "top_artists": top_artists,
            "top_genres": top_genres,
            "top_moods": top_moods,
            "avoid_repeat_hours": self.avoid_repeat_hours,
            "avoid_artist_minutes": self.avoid_artist_minutes
        }
    
    def get_last_played_tracks(self, count: int = 10) -> List[PlayedTrack]:
        """Obtener las últimas canciones reproducidas"""
        return self.played_tracks[-count:] if self.played_tracks else []
    
    def clear_history(self):
        """Limpiar todo el historial"""
        self.played_tracks = []
        self._save_history()
        print("🗑️ Historial musical limpiado completamente")
    
    def export_history(self, filename: str = None) -> str:
        """Exportar historial a archivo JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"music_history_export_{timestamp}.json"
        
        try:
            data = {
                "export_date": datetime.now().isoformat(),
                "total_tracks": len(self.played_tracks),
                "history": [asdict(track) for track in self.played_tracks]
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"📤 Historial exportado a: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Error exportando historial: {e}")
            return ""

def test_music_history():
    """Test del gestor de historial musical"""
    print("🧪 TEST: Music History Manager")
    print("=" * 40)
    
    # Crear instancia
    history_manager = MusicHistoryManager("test_music_history.json")
    
    # Simular canciones reproducidas
    test_tracks = [
        {"uri": "spotify:track:1", "name": "Canción 1", "artist": "Artista A", "genre": "pop"},
        {"uri": "spotify:track:2", "name": "Canción 2", "artist": "Artista B", "genre": "rock"},
        {"uri": "spotify:track:3", "name": "Canción 3", "artist": "Artista A", "genre": "pop"},
        {"uri": "spotify:track:4", "name": "Canción 4", "artist": "Artista C", "genre": "reggaeton"},
    ]
    
    # Agregar canciones al historial
    for i, track in enumerate(test_tracks):
        print(f"\n📝 Agregando canción {i+1}...")
        history_manager.add_played_track(track, mood_context="test", user_requested=(i % 2 == 0))
        time.sleep(0.1)  # Simular tiempo entre canciones
    
    # Mostrar estadísticas
    print("\n📊 ESTADÍSTICAS:")
    stats = history_manager.get_history_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Test de filtrado
    print(f"\n🎵 TEST DE FILTRADO:")
    all_tracks = test_tracks + [
        {"uri": "spotify:track:5", "name": "Canción 5", "artist": "Artista D", "genre": "jazz"},
        {"uri": "spotify:track:6", "name": "Canción 6", "artist": "Artista E", "genre": "classical"},
    ]
    
    filtered = history_manager.filter_tracks_by_history(all_tracks)
    print(f"   Canciones originales: {len(all_tracks)}")
    print(f"   Canciones filtradas: {len(filtered)}")
    
    # Limpiar archivo de prueba
    try:
        os.remove("test_music_history.json")
        print("🧹 Archivo de prueba eliminado")
    except:
        pass

if __name__ == "__main__":
    test_music_history()
