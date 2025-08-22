"""
Spotify User Data Extractor - Roxy Assistant
============================================
Extrae datos del usuario de Spotify para personalización inteligente:
- Historial de escucha y preferencias
- Biblioteca (contenido guardado)
- Playlists
- Artistas y usuarios seguidos
- Estado de reproducción actual
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
from spotify_controller_unified import SpotifyControllerUnified

class SpotifyUserDataExtractor:
    def __init__(self):
        """Inicializar extractor de datos de usuario"""
        self.spotify_controller = SpotifyControllerUnified()
        self.cache_file = "cache/spotify_user_data.json"
        self.preferences_file = "cache/spotify_preferences.json"
        self.cache_duration = 3600  # 1 hora en segundos
        
        # Crear directorio cache si no existe
        os.makedirs("cache", exist_ok=True)
        
        print("🎵 Spotify User Data Extractor inicializado")
    
    def extract_all_user_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Extraer todos los datos del usuario de Spotify"""
        
        # Verificar cache
        if not force_refresh and self._is_cache_valid():
            print("📦 Usando datos en cache (válidos)")
            return self._load_cache()
        
        print("🔄 Extrayendo datos frescos de Spotify...")
        
        # Autenticar
        if not self.spotify_controller.authenticate():
            print("❌ Error de autenticación con Spotify")
            return {}
        
        user_data = {
            "timestamp": datetime.now().isoformat(),
            "user_profile": self._get_user_profile(),
            "recently_played": self._get_recently_played(),
            "top_tracks": self._get_top_tracks(),
            "top_artists": self._get_top_artists(),
            "saved_tracks": self._get_saved_tracks(),
            "playlists": self._get_user_playlists(),
            "followed_artists": self._get_followed_artists(),
            "current_playback": self._get_current_playback(),
            "audio_features": {}  # Se llenará después
        }
        
        # Obtener características de audio de tracks favoritos
        user_data["audio_features"] = self._analyze_audio_features(user_data)
        
        # Guardar en cache
        self._save_cache(user_data)
        
        print("✅ Datos de usuario extraídos y guardados")
        return user_data
    
    def _get_user_profile(self) -> Dict[str, Any]:
        """Obtener perfil del usuario"""
        try:
            headers = {'Authorization': f'Bearer {self.spotify_controller.access_token}'}
            response = requests.get('https://api.spotify.com/v1/me', headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                profile = {
                    "id": data.get("id"),
                    "display_name": data.get("display_name"),
                    "followers": data.get("followers", {}).get("total", 0),
                    "country": data.get("country"),
                    "product": data.get("product")  # free, premium
                }
                print(f"👤 Perfil: {profile['display_name']} ({profile['product']})")
                return profile
            else:
                print(f"❌ Error obteniendo perfil: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Error en perfil: {e}")
            return {}
    
    def _get_recently_played(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtener historial reciente de reproducción"""
        try:
            headers = {'Authorization': f'Bearer {self.spotify_controller.access_token}'}
            params = {'limit': limit}
            
            response = requests.get('https://api.spotify.com/v1/me/player/recently-played', 
                                  headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                recent_tracks = []
                
                for item in data.get('items', []):
                    track = item['track']
                    recent_tracks.append({
                        'name': track['name'],
                        'artist': ', '.join([artist['name'] for artist in track['artists']]),
                        'album': track['album']['name'],
                        'played_at': item['played_at'],
                        'uri': track['uri'],
                        'id': track['id'],
                        'popularity': track.get('popularity', 0)
                    })
                
                print(f"🎵 Historial reciente: {len(recent_tracks)} canciones")
                return recent_tracks
            else:
                print(f"❌ Error obteniendo historial: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error en historial: {e}")
            return []
    
    def _get_top_tracks(self, time_range: str = "medium_term", limit: int = 50) -> List[Dict[str, Any]]:
        """Obtener canciones más escuchadas"""
        try:
            headers = {'Authorization': f'Bearer {self.spotify_controller.access_token}'}
            params = {'time_range': time_range, 'limit': limit}
            
            response = requests.get('https://api.spotify.com/v1/me/top/tracks', 
                                  headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                top_tracks = []
                
                for track in data.get('items', []):
                    top_tracks.append({
                        'name': track['name'],
                        'artist': ', '.join([artist['name'] for artist in track['artists']]),
                        'album': track['album']['name'],
                        'uri': track['uri'],
                        'id': track['id'],
                        'popularity': track.get('popularity', 0)
                    })
                
                print(f"🌟 Top tracks ({time_range}): {len(top_tracks)} canciones")
                return top_tracks
            else:
                print(f"❌ Error obteniendo top tracks: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error en top tracks: {e}")
            return []
    
    def _get_top_artists(self, time_range: str = "medium_term", limit: int = 50) -> List[Dict[str, Any]]:
        """Obtener artistas más escuchados"""
        try:
            headers = {'Authorization': f'Bearer {self.spotify_controller.access_token}'}
            params = {'time_range': time_range, 'limit': limit}
            
            response = requests.get('https://api.spotify.com/v1/me/top/artists', 
                                  headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                top_artists = []
                
                for artist in data.get('items', []):
                    top_artists.append({
                        'name': artist['name'],
                        'genres': artist.get('genres', []),
                        'popularity': artist.get('popularity', 0),
                        'followers': artist.get('followers', {}).get('total', 0),
                        'uri': artist['uri'],
                        'id': artist['id']
                    })
                
                print(f"🎤 Top artists ({time_range}): {len(top_artists)} artistas")
                return top_artists
            else:
                print(f"❌ Error obteniendo top artists: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error en top artists: {e}")
            return []
    
    def _get_saved_tracks(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtener canciones guardadas en biblioteca"""
        try:
            headers = {'Authorization': f'Bearer {self.spotify_controller.access_token}'}
            saved_tracks = []
            offset = 0
            
            while len(saved_tracks) < limit:
                params = {'limit': min(50, limit - len(saved_tracks)), 'offset': offset}
                
                response = requests.get('https://api.spotify.com/v1/me/tracks', 
                                      headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items', [])
                    
                    if not items:
                        break
                    
                    for item in items:
                        track = item['track']
                        saved_tracks.append({
                            'name': track['name'],
                            'artist': ', '.join([artist['name'] for artist in track['artists']]),
                            'album': track['album']['name'],
                            'added_at': item['added_at'],
                            'uri': track['uri'],
                            'id': track['id'],
                            'popularity': track.get('popularity', 0)
                        })
                    
                    offset += len(items)
                else:
                    print(f"❌ Error obteniendo biblioteca: {response.status_code}")
                    break
            
            print(f"💾 Biblioteca: {len(saved_tracks)} canciones guardadas")
            return saved_tracks
                
        except Exception as e:
            print(f"❌ Error en biblioteca: {e}")
            return []
    
    def _get_user_playlists(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtener playlists del usuario"""
        try:
            headers = {'Authorization': f'Bearer {self.spotify_controller.access_token}'}
            params = {'limit': limit}
            
            response = requests.get('https://api.spotify.com/v1/me/playlists', 
                                  headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                playlists = []
                
                for playlist in data.get('items', []):
                    playlists.append({
                        'name': playlist['name'],
                        'description': playlist.get('description', ''),
                        'tracks_total': playlist['tracks']['total'],
                        'public': playlist['public'],
                        'collaborative': playlist['collaborative'],
                        'uri': playlist['uri'],
                        'id': playlist['id']
                    })
                
                print(f"📋 Playlists: {len(playlists)} listas")
                return playlists
            else:
                print(f"❌ Error obteniendo playlists: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error en playlists: {e}")
            return []
    
    def _get_followed_artists(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtener artistas seguidos"""
        try:
            headers = {'Authorization': f'Bearer {self.spotify_controller.access_token}'}
            params = {'type': 'artist', 'limit': limit}
            
            response = requests.get('https://api.spotify.com/v1/me/following', 
                                  headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                followed_artists = []
                
                for artist in data.get('artists', {}).get('items', []):
                    followed_artists.append({
                        'name': artist['name'],
                        'genres': artist.get('genres', []),
                        'popularity': artist.get('popularity', 0),
                        'followers': artist.get('followers', {}).get('total', 0),
                        'uri': artist['uri'],
                        'id': artist['id']
                    })
                
                print(f"👥 Artistas seguidos: {len(followed_artists)} artistas")
                return followed_artists
            else:
                print(f"❌ Error obteniendo seguidos: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error en seguidos: {e}")
            return []
    
    def _get_current_playback(self) -> Dict[str, Any]:
        """Obtener estado de reproducción actual"""
        try:
            headers = {'Authorization': f'Bearer {self.spotify_controller.access_token}'}
            
            response = requests.get('https://api.spotify.com/v1/me/player', 
                                  headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data:
                    track = data.get('item', {})
                    current_playback = {
                        'is_playing': data.get('is_playing', False),
                        'progress_ms': data.get('progress_ms', 0),
                        'shuffle_state': data.get('shuffle_state', False),
                        'repeat_state': data.get('repeat_state', 'off'),
                        'volume_percent': data.get('device', {}).get('volume_percent', 0),
                        'device_name': data.get('device', {}).get('name', ''),
                        'device_type': data.get('device', {}).get('type', ''),
                        'track': {
                            'name': track.get('name', ''),
                            'artist': ', '.join([artist['name'] for artist in track.get('artists', [])]),
                            'album': track.get('album', {}).get('name', ''),
                            'uri': track.get('uri', ''),
                            'id': track.get('id', '')
                        } if track else None
                    }
                    
                    print(f"🎧 Reproduciendo: {current_playback['track']['name'] if current_playback['track'] else 'Nada'}")
                    return current_playback
                else:
                    print("🔇 No hay reproducción activa")
                    return {}
            elif response.status_code == 204:
                print("🔇 No hay dispositivos activos")
                return {}
            else:
                print(f"❌ Error obteniendo playback: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Error en playback: {e}")
            return {}
    
    def _analyze_audio_features(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar características de audio de las canciones favoritas"""
        try:
            # Recopilar IDs de tracks favoritos
            track_ids = []
            
            # Top tracks
            for track in user_data.get('top_tracks', [])[:20]:  # Solo top 20
                if track.get('id'):
                    track_ids.append(track['id'])
            
            # Tracks guardados
            for track in user_data.get('saved_tracks', [])[:20]:  # Solo top 20
                if track.get('id'):
                    track_ids.append(track['id'])
            
            if not track_ids:
                return {}
            
            # Obtener características de audio
            headers = {'Authorization': f'Bearer {self.spotify_controller.access_token}'}
            params = {'ids': ','.join(track_ids[:100])}  # Máximo 100 por request
            
            response = requests.get('https://api.spotify.com/v1/audio-features', 
                                  headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                features = data.get('audio_features', [])
                
                # Calcular promedios
                if features:
                    valid_features = [f for f in features if f is not None]
                    
                    if valid_features:
                        avg_features = {
                            'danceability': sum(f.get('danceability', 0) for f in valid_features) / len(valid_features),
                            'energy': sum(f.get('energy', 0) for f in valid_features) / len(valid_features),
                            'valence': sum(f.get('valence', 0) for f in valid_features) / len(valid_features),
                            'acousticness': sum(f.get('acousticness', 0) for f in valid_features) / len(valid_features),
                            'instrumentalness': sum(f.get('instrumentalness', 0) for f in valid_features) / len(valid_features),
                            'tempo': sum(f.get('tempo', 0) for f in valid_features) / len(valid_features),
                            'loudness': sum(f.get('loudness', 0) for f in valid_features) / len(valid_features)
                        }
                        
                        print(f"🎼 Audio features analizadas: {len(valid_features)} canciones")
                        return avg_features
            
            return {}
                
        except Exception as e:
            print(f"❌ Error analizando audio features: {e}")
            return {}
    
    def _is_cache_valid(self) -> bool:
        """Verificar si el cache es válido"""
        try:
            if not os.path.exists(self.cache_file):
                return False
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            timestamp = datetime.fromisoformat(data.get('timestamp', ''))
            age = (datetime.now() - timestamp).total_seconds()
            
            return age < self.cache_duration
            
        except Exception:
            return False
    
    def _load_cache(self) -> Dict[str, Any]:
        """Cargar datos del cache"""
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_cache(self, data: Dict[str, Any]) -> None:
        """Guardar datos en cache"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error guardando cache: {e}")
    
    def generate_user_preferences(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generar perfil de preferencias basado en los datos"""
        preferences = {
            "timestamp": datetime.now().isoformat(),
            "favorite_genres": self._extract_favorite_genres(user_data),
            "favorite_artists": self._extract_favorite_artists(user_data),
            "music_characteristics": user_data.get('audio_features', {}),
            "listening_patterns": self._analyze_listening_patterns(user_data),
            "mood_preferences": self._infer_mood_preferences(user_data),
            "discovery_level": self._calculate_discovery_level(user_data)
        }
        
        # Guardar preferencias
        try:
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(preferences, f, indent=2, ensure_ascii=False)
            print("✅ Preferencias generadas y guardadas")
        except Exception as e:
            print(f"❌ Error guardando preferencias: {e}")
        
        return preferences
    
    def _extract_favorite_genres(self, user_data: Dict[str, Any]) -> List[str]:
        """Extraer géneros favoritos"""
        genre_count = {}
        
        # Contar géneros de top artists
        for artist in user_data.get('top_artists', []):
            for genre in artist.get('genres', []):
                genre_count[genre] = genre_count.get(genre, 0) + 1
        
        # Contar géneros de followed artists
        for artist in user_data.get('followed_artists', []):
            for genre in artist.get('genres', []):
                genre_count[genre] = genre_count.get(genre, 0) + 1
        
        # Ordenar por frecuencia
        sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)
        return [genre for genre, count in sorted_genres[:10]]  # Top 10
    
    def _extract_favorite_artists(self, user_data: Dict[str, Any]) -> List[str]:
        """Extraer artistas favoritos"""
        artists = []
        
        # Top artists (más peso)
        for artist in user_data.get('top_artists', [])[:20]:
            artists.append(artist['name'])
        
        # Followed artists
        for artist in user_data.get('followed_artists', [])[:10]:
            if artist['name'] not in artists:
                artists.append(artist['name'])
        
        return artists
    
    def _analyze_listening_patterns(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizar patrones de escucha"""
        recent = user_data.get('recently_played', [])
        
        if not recent:
            return {}
        
        # Analizar horarios (si está disponible)
        patterns = {
            "total_recent_tracks": len(recent),
            "unique_artists_recent": len(set(track['artist'] for track in recent)),
            "repeat_tendency": self._calculate_repeat_tendency(recent)
        }
        
        return patterns
    
    def _infer_mood_preferences(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """Inferir preferencias de mood basado en características de audio"""
        features = user_data.get('audio_features', {})
        
        if not features:
            return {}
        
        moods = {}
        
        # Mapear características a moods
        if features.get('energy', 0) > 0.7:
            moods['energy_level'] = 'high'
        elif features.get('energy', 0) < 0.3:
            moods['energy_level'] = 'low'
        else:
            moods['energy_level'] = 'medium'
        
        if features.get('valence', 0) > 0.6:
            moods['mood_tendency'] = 'positive'
        elif features.get('valence', 0) < 0.4:
            moods['mood_tendency'] = 'melancholic'
        else:
            moods['mood_tendency'] = 'neutral'
        
        if features.get('danceability', 0) > 0.7:
            moods['danceability'] = 'high'
        else:
            moods['danceability'] = 'low'
        
        return moods
    
    def _calculate_discovery_level(self, user_data: Dict[str, Any]) -> str:
        """Calcular nivel de descubrimiento musical"""
        top_artists = user_data.get('top_artists', [])
        followed = user_data.get('followed_artists', [])
        
        if not top_artists:
            return 'unknown'
        
        # Calcular popularidad promedio
        avg_popularity = sum(artist.get('popularity', 0) for artist in top_artists) / len(top_artists)
        
        if avg_popularity > 80:
            return 'mainstream'
        elif avg_popularity > 60:
            return 'mixed'
        else:
            return 'niche'
    
    def _calculate_repeat_tendency(self, recent_tracks: List[Dict[str, Any]]) -> float:
        """Calcular tendencia a repetir canciones"""
        if not recent_tracks:
            return 0.0
        
        track_counts = {}
        for track in recent_tracks:
            key = f"{track['name']} - {track['artist']}"
            track_counts[key] = track_counts.get(key, 0) + 1
        
        repeated_tracks = sum(1 for count in track_counts.values() if count > 1)
        return repeated_tracks / len(track_counts) if track_counts else 0.0
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """Obtener preferencias del usuario (desde cache o generar nuevas)"""
        try:
            if os.path.exists(self.preferences_file):
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    preferences = json.load(f)
                    
                # Verificar si son recientes (menos de 24 horas)
                timestamp = datetime.fromisoformat(preferences.get('timestamp', ''))
                age = (datetime.now() - timestamp).total_seconds()
                
                if age < 86400:  # 24 horas
                    print("📊 Usando preferencias en cache")
                    return preferences
            
            # Generar nuevas preferencias
            print("🔄 Generando nuevas preferencias...")
            user_data = self.extract_all_user_data()
            return self.generate_user_preferences(user_data)
            
        except Exception as e:
            print(f"❌ Error obteniendo preferencias: {e}")
            return {}

def test_data_extraction():
    """Función de prueba para la extracción de datos"""
    print("🧪 TESTING: Spotify User Data Extractor")
    print("=" * 50)
    
    extractor = SpotifyUserDataExtractor()
    
    # Extraer datos
    user_data = extractor.extract_all_user_data(force_refresh=True)
    
    if user_data:
        print("\n📊 RESUMEN DE DATOS EXTRAÍDOS:")
        print(f"   👤 Usuario: {user_data.get('user_profile', {}).get('display_name', 'N/A')}")
        print(f"   🎵 Historial reciente: {len(user_data.get('recently_played', []))} canciones")
        print(f"   🌟 Top tracks: {len(user_data.get('top_tracks', []))} canciones")
        print(f"   🎤 Top artists: {len(user_data.get('top_artists', []))} artistas")
        print(f"   💾 Biblioteca: {len(user_data.get('saved_tracks', []))} canciones")
        print(f"   📋 Playlists: {len(user_data.get('playlists', []))} listas")
        print(f"   👥 Seguidos: {len(user_data.get('followed_artists', []))} artistas")
        
        # Generar preferencias
        preferences = extractor.generate_user_preferences(user_data)
        
        print(f"\n🎯 PREFERENCIAS GENERADAS:")
        print(f"   🎼 Géneros favoritos: {preferences.get('favorite_genres', [])[:5]}")
        print(f"   🎤 Artistas favoritos: {preferences.get('favorite_artists', [])[:5]}")
        print(f"   🎭 Mood: {preferences.get('mood_preferences', {})}")
        print(f"   📈 Descubrimiento: {preferences.get('discovery_level', 'N/A')}")
        
    else:
        print("❌ No se pudieron extraer datos")

if __name__ == "__main__":
    test_data_extraction()
