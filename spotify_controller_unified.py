"""
Controlador Unificado de Spotify - Roxy Megurdy
==============================================
Controlador consolidado que combina API oficial y métodos de integración
Elimina la duplicación entre spotify_api_controller.py y spotify_integration.py
"""

import os
import json
import base64
import requests
import webbrowser
import time
import subprocess
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode

class SpotifyControllerUnified:
    """Controlador unificado de Spotify que combina API oficial y métodos de integración"""
    
    def __init__(self):
        """Inicializar controlador unificado de Spotify"""
        # Configuración básica
        self.client_id = None
        self.client_secret = None
        self.access_token = None
        self.refresh_token = None
        self.redirect_uri = "http://127.0.0.1:8888/callback"
        self.scope = "user-modify-playback-state user-read-playback-state user-read-currently-playing streaming"
        
        # Archivos de configuración
        self.token_file = "spotify_tokens.json"
        self.cache_file = ".spotify_cache"
        
        # Estado del controlador
        self.spotify_premium = None
        self.device_id = None
        
        # Cargar configuración
        self._load_credentials()
        self._load_saved_tokens()
        self._setup_spotipy_integration()
        
        print("🎵 Controlador Spotify Unificado inicializado")
    
    def _load_credentials(self):
        """Cargar credenciales de Spotify desde .env"""
        if os.path.exists('.env'):
            try:
                with open('.env', 'r') as f:
                    for line in f:
                        if 'spotify_client_id' in line and '=' in line:
                            self.client_id = line.split('=', 1)[1].strip().strip('"').strip("'")
                        elif 'spotify_client_secret' in line and '=' in line:
                            self.client_secret = line.split('=', 1)[1].strip().strip('"').strip("'")
                
                if self.client_id and self.client_secret:
                    print("✅ Credenciales Spotify cargadas")
                else:
                    print("⚠️ Credenciales Spotify incompletas en .env")
                    
            except Exception as e:
                print(f"⚠️ Error cargando credenciales: {e}")
    
    def _load_saved_tokens(self):
        """Cargar tokens guardados"""
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'r') as f:
                    tokens = json.load(f)
                    self.access_token = tokens.get('access_token')
                    self.refresh_token = tokens.get('refresh_token')
                    print("✅ Tokens de Spotify cargados")
        except Exception as e:
            print(f"⚠️ Error cargando tokens: {e}")
    
    def _save_tokens(self, access_token: str, refresh_token: Optional[str] = None):
        """Guardar tokens"""
        try:
            tokens = {
                'access_token': access_token,
                'refresh_token': refresh_token or self.refresh_token
            }
            
            with open(self.token_file, 'w') as f:
                json.dump(tokens, f)
            
            self.access_token = access_token
            if refresh_token:
                self.refresh_token = refresh_token
                
            print("✅ Tokens guardados")
        except Exception as e:
            print(f"❌ Error guardando tokens: {e}")
    
    def _setup_spotipy_integration(self):
        """Configurar integración con spotipy para funciones Premium"""
        try:
            import spotipy
            from spotipy.oauth2 import SpotifyOAuth
            
            if self.client_id and self.client_secret:
                self.spotify_premium = spotipy.Spotify(auth_manager=SpotifyOAuth(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    redirect_uri=self.redirect_uri,
                    scope=self.scope,
                    cache_path=self.cache_file
                ))
                print("🎵 Integración Premium (spotipy) configurada")
                return True
            else:
                print("⚠️ Credenciales faltantes para Premium")
                return False
                
        except ImportError:
            print("⚠️ spotipy no instalado - funcionalidad Premium limitada")
            print("💡 Para funciones avanzadas: pip install spotipy")
            self.spotify_premium = None
            return False
        except Exception as e:
            print(f"⚠️ Error configurando spotipy: {e}")
            self.spotify_premium = None
            return False
    
    # ==================== MÉTODOS DE AUTENTICACIÓN ====================
    
    def is_available(self) -> bool:
        """Verificar si Spotify está disponible"""
        return bool(self.client_id and self.client_secret)
    
    def has_premium_features(self) -> bool:
        """Verificar si tiene funcionalidades Premium"""
        return self.spotify_premium is not None
    
    def authenticate(self) -> bool:
        """Autenticar con Spotify (método unificado)"""
        if not self.is_available():
            print("❌ Credenciales de Spotify no configuradas")
            print("💡 Agrega spotify_client_id y spotify_client_secret en .env")
            return False
        
        # Intentar con token existente
        if self.access_token:
            if self._test_token():
                print("✅ Token existente válido")
                return True
            else:
                print("⚠️ Token expirado, refrescando...")
                if self._refresh_access_token():
                    return True
        
        # Si no hay token o falló el refresh, obtener uno nuevo
        return self._get_new_access_token()
    
    def _test_token(self) -> bool:
        """Probar si el token actual funciona"""
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get('https://api.spotify.com/v1/me', headers=headers, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _refresh_access_token(self) -> bool:
        """Refrescar token de acceso"""
        if not self.refresh_token:
            return False
        
        try:
            credentials = f"{self.client_id}:{self.client_secret}"
            b64_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {b64_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }
            
            response = requests.post('https://accounts.spotify.com/api/token', 
                                   headers=headers, data=data, timeout=10)
            
            if response.status_code == 200:
                tokens = response.json()
                new_access_token = tokens['access_token']
                new_refresh_token = tokens.get('refresh_token', self.refresh_token)
                
                self._save_tokens(new_access_token, new_refresh_token)
                print("✅ Token refrescado exitosamente")
                return True
            else:
                print(f"❌ Error refrescando token: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error en refresh: {e}")
            return False
    
    def _get_new_access_token(self) -> bool:
        """Obtener nuevo token de acceso"""
        # Método 1: Intentar con Client Credentials (búsqueda básica)
        if self._get_client_credentials_token():
            return True
        
        # Método 2: Flujo de autorización completo (funciones Premium)
        return self._start_oauth_flow()
    
    def _get_client_credentials_token(self) -> bool:
        """Obtener token usando Client Credentials (solo búsqueda)"""
        try:
            credentials = f"{self.client_id}:{self.client_secret}"
            b64_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {b64_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {'grant_type': 'client_credentials'}
            
            response = requests.post('https://accounts.spotify.com/api/token', 
                                   headers=headers, data=data, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                print("✅ Token Client Credentials obtenido (búsqueda básica)")
                return True
            else:
                print(f"❌ Error obteniendo Client Credentials: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error en Client Credentials: {e}")
            return False
    
    def _start_oauth_flow(self) -> bool:
        """Iniciar flujo OAuth para funciones Premium"""
        print("🔐 Iniciando autenticación OAuth para funciones Premium...")
        
        auth_params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': self.scope,
            'show_dialog': 'true'
        }
        
        auth_url = f"https://accounts.spotify.com/authorize?{urlencode(auth_params)}"
        
        print(f"🌐 Abriendo URL de autorización...")
        webbrowser.open(auth_url)
        
        print("\n📋 INSTRUCCIONES:")
        print("1. Autoriza la aplicación en el navegador")
        print("2. Serás redirigido a 127.0.0.1:8888 (error normal)")
        print("3. Copia el código de la URL (después de 'code=')")
        
        code = input("\n🔑 Pega el código aquí: ").strip()
        
        if not code:
            print("❌ No se proporcionó código")
            return False
        
        return self._exchange_code_for_tokens(code)
    
    def _exchange_code_for_tokens(self, code: str) -> bool:
        """Intercambiar código por tokens"""
        try:
            credentials = f"{self.client_id}:{self.client_secret}"
            b64_credentials = base64.b64encode(credentials.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {b64_credentials}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': self.redirect_uri
            }
            
            response = requests.post('https://accounts.spotify.com/api/token', 
                                   headers=headers, data=data, timeout=10)
            
            if response.status_code == 200:
                tokens = response.json()
                access_token = tokens['access_token']
                refresh_token = tokens['refresh_token']
                
                self._save_tokens(access_token, refresh_token)
                print("✅ Autenticación OAuth exitosa!")
                return True
            else:
                print(f"❌ Error obteniendo tokens: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error en intercambio de tokens: {e}")
            return False
    
    # ==================== MÉTODOS DE BÚSQUEDA ====================
    
    def search_track(self, query: str, limit: int = 5) -> List[Dict]:
        """Buscar tracks en Spotify (método unificado)"""
        if not self.access_token:
            if not self.authenticate():
                return []
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            params = {
                'q': query,
                'type': 'track',
                'limit': limit
            }
            
            response = requests.get('https://api.spotify.com/v1/search', 
                                  headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                tracks = []
                
                for track in data['tracks']['items']:
                    tracks.append({
                        'name': track['name'],
                        'artist': ', '.join([artist['name'] for artist in track['artists']]),
                        'uri': track['uri'],
                        'id': track['id'],
                        'external_url': track['external_urls']['spotify'],
                        'preview_url': track.get('preview_url')
                    })
                
                print(f"✅ Encontrados {len(tracks)} tracks para '{query}'")
                return tracks
            else:
                print(f"❌ Error buscando: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")
            return []
    
    # ==================== MÉTODOS DE REPRODUCCIÓN ====================
    
    def play_track_by_uri(self, track_uri: str, track_info: Optional[Dict] = None) -> Dict[str, Any]:
        """Reproducir directamente por URI (método optimizado para selección inteligente)"""
        result = {
            'success': False,
            'method': 'play_by_uri',
            'track_uri': track_uri,
            'error': None,
            'track_info': track_info
        }
        
        print(f"🎵 REPRODUCCIÓN DIRECTA POR URI: {track_uri}")
        
        # 1. Autenticar
        if not self.authenticate():
            result['error'] = "Autenticación fallida"
            return result
        
        # 2. Intentar reproducción Premium directa
        if self.has_premium_features():
            if self._play_track_premium(track_uri):
                result['success'] = True
                result['method'] = 'premium_direct_uri'
                print("🎉 ¡Reproduciendo directamente via API Premium!")
                return result
        
        # 3. Fallback: Métodos de integración con URI
        if track_info:
            if self._play_track_integration(track_info):
                result['success'] = True
                result['method'] = 'integration_uri'
                print("✅ Reproduciendo via métodos de integración (URI)")
                return result
        
        # 4. Último fallback: URI directo
        try:
            subprocess.run(["start", track_uri], shell=True, check=True)
            result['success'] = True
            result['method'] = 'direct_uri_fallback'
            print("✅ Reproduciendo con URI directo")
            return result
        except Exception as e:
            result['error'] = f"Error con URI directo: {e}"
        
        result['error'] = "Todos los métodos de reproducción por URI fallaron"
        return result
    
    def play_music_advanced(self, search_query: str) -> Dict[str, Any]:
        """Método principal de reproducción (unifica todas las funcionalidades)"""
        result = {
            'success': False,
            'method': 'unified_controller',
            'query': search_query,
            'error': None,
            'track_info': None
        }
        
        print(f"🎵 REPRODUCCIÓN UNIFICADA: '{search_query}'")
        
        # 1. Autenticar
        if not self.authenticate():
            result['error'] = "Autenticación fallida"
            return result
        
        # 2. Buscar track
        tracks = self.search_track(search_query, limit=1)
        if not tracks:
            result['error'] = "No se encontraron pistas"
            return result
        
        track = tracks[0]
        result['track_info'] = track
        print(f"🎵 Pista encontrada: {track['artist']} - {track['name']}")
        
        # 3. Intentar reproducción Premium
        if self.has_premium_features():
            if self._play_track_premium(track['uri']):
                result['success'] = True
                result['method'] = 'premium_api'
                print("🎉 ¡Reproduciendo via API Premium!")
                return result
        
        # 4. Fallback: Métodos de integración
        if self._play_track_integration(track):
            result['success'] = True
            result['method'] = 'integration_fallback'
            print("✅ Reproduciendo via métodos de integración")
            return result
        
        # 5. Último fallback: Web
        if self._play_track_web(track):
            result['success'] = True
            result['method'] = 'web_fallback'
            print("🌐 Reproduciendo via Spotify Web")
            return result
        
        result['error'] = "Todos los métodos de reproducción fallaron"
        return result
    
    def _play_track_premium(self, track_uri: str) -> bool:
        """Reproducir usando API Premium (spotipy)"""
        if not self.spotify_premium:
            return False
        
        try:
            # Verificar dispositivos
            devices_response = self.spotify_premium.devices()
            
            if not devices_response or not devices_response.get('devices'):
                print("⚠️ No hay dispositivos activos. Intentando activar...")
                self._activate_spotify_device()
                time.sleep(3)
                devices_response = self.spotify_premium.devices()
            
            if devices_response and devices_response.get('devices'):
                devices = devices_response['devices']
                
                # Buscar dispositivo activo
                active_device = None
                for device in devices:
                    if device.get('is_active'):
                        active_device = device
                        break
                
                if not active_device and devices:
                    active_device = devices[0]
                
                if active_device:
                    self.spotify_premium.start_playback(
                        device_id=active_device['id'],
                        uris=[track_uri]
                    )
                    print(f"✅ Reproduciendo en: {active_device.get('name', 'Dispositivo')}")
                    return True
            
            print("⚠️ No se encontraron dispositivos disponibles")
            return False
            
        except Exception as e:
            print(f"❌ Error reproducción Premium: {e}")
            return False
    
    def _play_track_integration(self, track: Dict) -> bool:
        """Reproducir usando métodos de integración"""
        try:
            # Método 1: URI directo
            try:
                subprocess.run(["start", track['uri']], shell=True, check=True)
                print("✅ Abriendo con URI directo")
                self._try_autoplay_keyboard()
                return True
            except:
                pass
            
            # Método 2: Protocolo spotify:
            try:
                subprocess.run(["start", f"spotify:track:{track['id']}"], shell=True, check=True)
                print("✅ Abriendo con protocolo spotify:")
                self._try_autoplay_keyboard()
                return True
            except:
                pass
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error métodos integración: {e}")
            return False
    
    def _play_track_web(self, track: Dict) -> bool:
        """Reproducir usando Spotify Web"""
        try:
            # URLs con diferentes parámetros de autoplay
            urls = [
                f"{track['external_url']}?autoplay=1",
                f"{track['external_url']}?play=true",
                track['external_url']
            ]
            
            for url in urls:
                try:
                    webbrowser.open(url)
                    print(f"✅ Abriendo en Spotify Web")
                    return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            print(f"❌ Error Spotify Web: {e}")
            return False
    
    def _activate_spotify_device(self):
        """Intentar activar un dispositivo Spotify"""
        try:
            # Intentar abrir Spotify Desktop
            subprocess.run(["start", "spotify:"], shell=True)
            print("🎵 Activando Spotify Desktop...")
        except:
            pass
    
    def _try_autoplay_keyboard(self):
        """Intentar auto-reproducción con teclado"""
        try:
            import pyautogui
            time.sleep(2)
            pyautogui.press('space')
            print("🎵 Comando de reproducción enviado")
        except ImportError:
            print("💡 Para auto-reproducción: pip install pyautogui")
        except Exception as e:
            print(f"⚠️ Error auto-reproducción: {e}")
    
    # ==================== MÉTODOS DE CONTROL ====================
    
    def pause_music(self) -> bool:
        """Pausar música"""
        if self.spotify_premium:
            try:
                self.spotify_premium.pause_playback()
                return True
            except:
                pass
        return False
    
    def resume_music(self) -> bool:
        """Reanudar música"""
        if self.spotify_premium:
            try:
                self.spotify_premium.start_playback()
                return True
            except:
                pass
        return False
    
    def next_track(self) -> bool:
        """Siguiente canción"""
        if self.spotify_premium:
            try:
                self.spotify_premium.next_track()
                return True
            except:
                pass
        return False
    
    def previous_track(self) -> bool:
        """Canción anterior"""
        if self.spotify_premium:
            try:
                self.spotify_premium.previous_track()
                return True
            except:
                pass
        return False
    
    def set_volume(self, volume: int) -> bool:
        """Establecer volumen (0-100)"""
        if self.spotify_premium:
            try:
                self.spotify_premium.volume(max(0, min(100, volume)))
                return True
            except:
                pass
        return False
    
    def get_current_track(self) -> Optional[Dict]:
        """Obtener información de la pista actual"""
        if self.spotify_premium:
            try:
                current = self.spotify_premium.current_playback()
                if current and current.get('item'):
                    track = current['item']
                    return {
                        'name': track['name'],
                        'artist': ', '.join([a['name'] for a in track['artists']]),
                        'album': track['album']['name'],
                        'is_playing': current.get('is_playing', False),
                        'progress_ms': current.get('progress_ms', 0),
                        'duration_ms': track.get('duration_ms', 0)
                    }
            except:
                pass
        return None
    
    def get_devices(self) -> List[Dict]:
        """Obtener dispositivos disponibles"""
        if self.spotify_premium:
            try:
                devices_response = self.spotify_premium.devices()
                if devices_response and devices_response.get('devices'):
                    return devices_response['devices']
            except:
                pass
        return []
    
    # ==================== MÉTODOS DE UTILIDAD ====================
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado del controlador"""
        return {
            'available': self.is_available(),
            'authenticated': bool(self.access_token),
            'premium_features': self.has_premium_features(),
            'devices_count': len(self.get_devices()),
            'current_track': self.get_current_track()
        }

# ==================== FUNCIONES DE CONFIGURACIÓN ====================

def setup_spotify_credentials():
    """Configurar credenciales de Spotify en .env"""
    print("🔧 CONFIGURACIÓN DE SPOTIFY")
    print("=" * 40)
    
    print("📋 Para usar Spotify necesitas:")
    print("1. Ir a https://developer.spotify.com/dashboard")
    print("2. Crear una aplicación")
    print("3. Obtener Client ID y Client Secret")
    print("4. Agregar 'http://127.0.0.1:8888/callback' como Redirect URI")
    
    client_id = input("\n🔑 Client ID: ").strip()
    client_secret = input("🔐 Client Secret: ").strip()
    
    if client_id and client_secret:
        env_content = f"""
# Spotify API Credentials
spotify_client_id={client_id}
spotify_client_secret={client_secret}
"""
        
        with open('.env', 'a') as f:
            f.write(env_content)
        
        print("✅ Credenciales guardadas en .env")
        return True
    else:
        print("❌ Credenciales incompletas")
        return False

def test_spotify_unified():
    """Test del controlador unificado"""
    print("🎵 TEST: Controlador Spotify Unificado")
    print("=" * 50)
    
    controller = SpotifyControllerUnified()
    
    # Mostrar estado
    status = controller.get_status()
    print(f"📊 Estado:")
    print(f"   Disponible: {'✅' if status['available'] else '❌'}")
    print(f"   Autenticado: {'✅' if status['authenticated'] else '❌'}")
    print(f"   Premium: {'✅' if status['premium_features'] else '❌'}")
    print(f"   Dispositivos: {status['devices_count']}")
    
    if not status['available']:
        print("💡 Ejecuta setup_spotify_credentials() primero")
        return False
    
    # Test de búsqueda
    print(f"\n🔍 Test de búsqueda...")
    tracks = controller.search_track("bad bunny", limit=3)
    for i, track in enumerate(tracks, 1):
        print(f"   {i}. {track['artist']} - {track['name']}")
    
    # Test de reproducción
    if tracks:
        print(f"\n🎵 Test de reproducción...")
        result = controller.play_music_advanced("bad bunny")
        print(f"📊 Resultado: {'ÉXITO' if result['success'] else 'FALLÓ'}")
        print(f"📊 Método: {result['method']}")
        if result['error']:
            print(f"❌ Error: {result['error']}")
    
    return True

if __name__ == "__main__":
    print("🚀 CONTROLADOR SPOTIFY UNIFICADO")
    print("=" * 40)
    
    # Verificar credenciales
    controller = SpotifyControllerUnified()
    
    if not controller.is_available():
        print("⚠️ No hay credenciales configuradas")
        if input("¿Configurar ahora? (y/n): ").lower() == 'y':
            setup_spotify_credentials()
    
    # Ejecutar test
    test_spotify_unified()
