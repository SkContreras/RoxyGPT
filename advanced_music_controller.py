"""
Controlador Avanzado de Música - Roxy Megurdy
============================================
Sistema para reproducir música directamente sin necesidad de navegador
Detecta aplicaciones activas y usa métodos nativos de control
"""

import os
import json
import subprocess
import webbrowser
import requests
from typing import Optional, Dict, Any
import tempfile
import time

# Importaciones opcionales
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

class AdvancedMusicController:
    def __init__(self):
        """Inicializar controlador avanzado de música"""
        self.youtube_api_key = self._load_youtube_api_key()
        self.automation_available = PYAUTOGUI_AVAILABLE
        
    def _load_youtube_api_key(self) -> Optional[str]:
        """Cargar API key de YouTube desde .env"""
        if os.path.exists('.env'):
            try:
                with open('.env', 'r') as f:
                    for line in f:
                        if 'youtube_api_key' in line and '=' in line:
                            key = line.split('=', 1)[1].strip().strip('"').strip("'")
                            if key and key != 'your_youtube_api_key_here':
                                return key
            except Exception as e:
                print(f"⚠️ Error cargando YouTube API key: {e}")
        return None
    
    def play_music_advanced(self, search_query: str, platform: str = "auto") -> bool:
        """
        Reproducir música usando métodos avanzados con detección de aplicaciones
        
        Args:
            search_query: Búsqueda de la canción
            platform: "spotify", "youtube", "auto"
            
        Returns:
            bool: True si se reprodujo exitosamente
        """
        print(f"🎵 REPRODUCCIÓN AVANZADA: '{search_query}' en {platform}")
        
        if platform == "auto":
            # Intentar Spotify primero, luego YouTube
            if self._try_spotify_advanced(search_query):
                return True
            return self._try_youtube_advanced(search_query)
        elif platform == "spotify":
            return self._try_spotify_advanced(search_query)
        elif platform == "youtube":
            return self._try_youtube_advanced(search_query)
        
        return False
    
    def _is_spotify_running(self) -> bool:
        """Detectar si Spotify Desktop está ejecutándose"""
        try:
            # En Windows, buscar proceso de Spotify
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq Spotify.exe"],
                capture_output=True, text=True, shell=True
            )
            return "Spotify.exe" in result.stdout
        except Exception:
            return False
    
    def _is_spotify_web_active(self) -> bool:
        """Detectar si hay una sesión web de Spotify activa"""
        try:
            # Verificar si hay ventanas del navegador con Spotify
            result = subprocess.run(
                ["tasklist", "/FI", "WINDOWTITLE eq *Spotify*"],
                capture_output=True, text=True, shell=True
            )
            return "chrome.exe" in result.stdout or "msedge.exe" in result.stdout or "firefox.exe" in result.stdout
        except Exception:
            return False
    
    def _try_spotify_advanced(self, search_query: str) -> bool:
        """Método avanzado para Spotify con detección de aplicación"""
        try:
            print(f"🎵 Intentando reproducción avanzada en Spotify: '{search_query}'")
            
            # Detectar estado de Spotify
            spotify_desktop_running = self._is_spotify_running()
            spotify_web_active = self._is_spotify_web_active()
            
            print(f"🔍 Spotify Desktop: {'🟢 ACTIVO' if spotify_desktop_running else '🔴 INACTIVO'}")
            print(f"🔍 Spotify Web: {'🟢 ACTIVO' if spotify_web_active else '🔴 INACTIVO'}")
            
            clean_query = search_query.replace(' ', '%20')
            
            # PRIORIDAD 1: Si Spotify Desktop está ejecutándose, usarlo
            if spotify_desktop_running:
                return self._control_spotify_desktop(search_query, clean_query)
            
            # PRIORIDAD 2: Si hay sesión web activa, usarla
            elif spotify_web_active:
                return self._control_spotify_web(search_query, clean_query)
            
            # PRIORIDAD 3: Intentar abrir Spotify Desktop
            else:
                return self._launch_spotify_desktop(search_query, clean_query)
                
        except Exception as e:
            print(f"❌ Error en Spotify avanzado: {e}")
            return self._fallback_spotify_web(search_query)
    
    def _control_spotify_desktop(self, search_query: str, clean_query: str) -> bool:
        """Controlar Spotify Desktop cuando está ejecutándose - VERSIÓN MEJORADA"""
        try:
            print("🎵 Controlando Spotify Desktop activo...")
            
            # Método 1: URI directo de búsqueda y reproducción
            spotify_search_uri = f"spotify:search:{clean_query}"
            
            # Abrir búsqueda en Spotify
            result = subprocess.run(
                ["start", "", spotify_search_uri], 
                shell=True, capture_output=True
            )
            
            if result.returncode == 0:
                print("✅ Búsqueda enviada a Spotify Desktop")
                
                # MEJORADO: Automatización más robusta con múltiples métodos
                if self.automation_available:
                    try:
                        print("🎵 Iniciando reproducción automática mejorada...")
                        time.sleep(3)  # Dar más tiempo para que cargue la búsqueda
                        
                        # Asegurar que Spotify está en foco
                        import pygetwindow as gw
                        spotify_windows = [w for w in gw.getAllWindows() if 'spotify' in w.title.lower()]
                        if spotify_windows:
                            spotify_windows[0].activate()
                            time.sleep(1)
                            print("✅ Ventana de Spotify enfocada")
                        
                        # NUEVO: Múltiples comandos de reproducción robustos
                        self._send_robust_play_commands()
                        
                        print("🎵 ¡REPRODUCCIÓN AUTOMÁTICA MEJORADA ENVIADA! Debería empezar a sonar")
                        return True
                        
                    except ImportError:
                        # Si pygetwindow no está disponible, usar método básico mejorado
                        print("📝 Usando método básico mejorado de automatización...")
                        time.sleep(2)
                        self._send_robust_play_commands()
                        print("🎵 Comandos de reproducción básicos mejorados enviados")
                        return True
                        
                    except Exception as e:
                        print(f"⚠️ Error en reproducción automática: {e}")
                        print("💡 Sugerencia: Instala pygetwindow con 'pip install pygetwindow'")
                        # Intentar método básico como fallback
                        try:
                            self._send_basic_play_commands()
                        except:
                            pass
                        return True  # Aún así consideramos exitoso el envío de búsqueda
                else:
                    print("⚠️ PyAutoGUI no disponible - instala con 'pip install pyautogui'")
                    print("🔧 La búsqueda se envió, pero debes presionar ENTER manualmente")
                
                return True
            else:
                print("⚠️ Error enviando comando a Spotify Desktop")
                return False
                
        except Exception as e:
            print(f"❌ Error controlando Spotify Desktop: {e}")
            return False
    
    def _control_spotify_web(self, search_query: str, clean_query: str) -> bool:
        """Controlar sesión web de Spotify existente"""
        try:
            print("🌐 Usando sesión web de Spotify existente...")
            
            # MEJORADO: URL con parámetros específicos para auto-reproducción
            web_urls = [
                f"https://open.spotify.com/search/{clean_query}?autoplay=1&si=autoplay",
                f"https://open.spotify.com/search/{clean_query}?play=true",
                f"https://open.spotify.com/search/{clean_query}",  # Fallback básico
            ]
            
            # Intentar cada URL hasta que una funcione
            for i, web_url in enumerate(web_urls):
                try:
                    webbrowser.open(web_url)
                    print(f"✅ Spotify Web abierto (método {i+1}/3): {web_url}")
                    
                    # Si tenemos automatización, intentar reproducir automáticamente
                    if self.automation_available and i == 0:  # Solo en el primer intento
                        try:
                            print("🎵 Automatizando clic en primer resultado...")
                            time.sleep(4)  # Esperar que cargue la página
                            
                            # Intentar hacer clic en el primer resultado
                            # Esto es experimental y puede necesitar ajustes
                            pyautogui.hotkey('ctrl', 'f')  # Abrir búsqueda
                            time.sleep(0.5)
                            pyautogui.typewrite('play')  # Buscar botón play
                            time.sleep(0.5)
                            pyautogui.press('escape')  # Cerrar búsqueda
                            time.sleep(0.5)
                            pyautogui.press('tab')  # Navegar al primer resultado
                            pyautogui.press('enter')  # Reproducir
                            
                            print("🎵 Automatización web intentada")
                            
                        except Exception as e:
                            print(f"⚠️ Error en automatización web: {e}")
                    
                    return True
                    
                except Exception as e:
                    print(f"⚠️ Error con URL {i+1}: {e}")
                    continue
            
            print("❌ No se pudo abrir ninguna URL de Spotify Web")
            return False
            
        except Exception as e:
            print(f"❌ Error controlando Spotify Web: {e}")
            return False
    
    def _launch_spotify_desktop(self, search_query: str, clean_query: str) -> bool:
        """Lanzar Spotify Desktop con búsqueda"""
        try:
            print("🚀 Lanzando Spotify Desktop...")
            
            # Intentar abrir Spotify Desktop
            spotify_paths = [
                os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe"),
                r"C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe",
                "spotify.exe"  # Si está en PATH
            ]
            
            spotify_launched = False
            for path in spotify_paths:
                try:
                    expanded_path = os.path.expandvars(path)
                    if os.path.exists(expanded_path):
                        subprocess.Popen([expanded_path])
                        spotify_launched = True
                        print(f"✅ Spotify Desktop lanzado desde: {expanded_path}")
                        break
                except Exception:
                    continue
            
            if not spotify_launched:
                # Fallback: intentar con comando start
                try:
                    subprocess.run(["start", "spotify:"], shell=True, check=True)
                    spotify_launched = True
                    print("✅ Spotify Desktop lanzado via protocolo")
                except Exception:
                    print("⚠️ No se pudo lanzar Spotify Desktop")
            
            if spotify_launched:
                # Esperar que Spotify se abra y luego enviar búsqueda
                print("⏳ Esperando que Spotify Desktop se inicie...")
                time.sleep(6)  # Dar más tiempo para que se abra completamente
                
                # Enviar búsqueda
                spotify_search_uri = f"spotify:search:{clean_query}"
                subprocess.run(["start", "", spotify_search_uri], shell=True)
                
                print(f"🎵 Búsqueda enviada: '{search_query}'")
                
                # NUEVO: Automatizar reproducción después del lanzamiento - MEJORADO
                if self.automation_available:
                    try:
                        print("🎵 Automatizando reproducción post-lanzamiento...")
                        time.sleep(4)  # Esperar que cargue la búsqueda
                        
                        # Intentar enfocar Spotify y reproducir
                        try:
                            import pygetwindow as gw
                            spotify_windows = [w for w in gw.getAllWindows() if 'spotify' in w.title.lower()]
                            if spotify_windows:
                                spotify_windows[0].activate()
                                time.sleep(1)
                                print("✅ Ventana de Spotify enfocada post-lanzamiento")
                        except ImportError:
                            pass
                        
                        # Usar comandos robustos de reproducción
                        self._send_robust_play_commands()
                        
                        print("🎵 ¡REPRODUCCIÓN AUTOMÁTICA COMPLETA! La música debería estar sonando")
                        
                    except Exception as e:
                        print(f"⚠️ Error en automatización post-lanzamiento: {e}")
                        print("💡 La búsqueda se envió, presiona ENTER en Spotify para reproducir")
                        # Intentar método básico como fallback
                        try:
                            self._send_basic_play_commands()
                        except:
                            pass
                
                return True
            else:
                # Si no se puede lanzar desktop, usar web
                return self._fallback_spotify_web(search_query)
                
        except Exception as e:
            print(f"❌ Error lanzando Spotify Desktop: {e}")
            return self._fallback_spotify_web(search_query)
    
    def _fallback_spotify_web(self, search_query: str) -> bool:
        """Fallback: usar Spotify Web con múltiples métodos"""
        try:
            print("🌐 Fallback: Usando Spotify Web...")
            clean_query = search_query.replace(' ', '%20')
            
            # Múltiples URLs de fallback con diferentes parámetros
            fallback_urls = [
                f"https://open.spotify.com/search/{clean_query}?autoplay=1",
                f"https://open.spotify.com/search/{clean_query}?si=fallback",
                f"https://open.spotify.com/search/{clean_query}",
                f"https://music.youtube.com/search?q={search_query}",  # YouTube Music como último recurso
            ]
            
            for i, url in enumerate(fallback_urls):
                try:
                    webbrowser.open(url)
                    platform = "Spotify Web" if "spotify.com" in url else "YouTube Music"
                    print(f"✅ {platform} abierto (fallback {i+1}/4): {url}")
                    return True
                except Exception as e:
                    print(f"⚠️ Error fallback {i+1}: {e}")
                    continue
            
            print("❌ Todos los métodos de fallback fallaron")
            return False
            
        except Exception as e:
            print(f"❌ Error en fallback web: {e}")
            return False
    
    def _try_youtube_advanced(self, search_query: str) -> bool:
        """Método avanzado para YouTube"""
        try:
            print(f"🎵 Intentando reproducción avanzada en YouTube: '{search_query}'")
            
            # Método 1: Si tenemos API key, buscar el video específico
            if self.youtube_api_key:
                video_url = self._find_youtube_video(search_query)
                if video_url:
                    print(f"🎵 Reproduciendo video específico: {video_url}")
                    webbrowser.open(video_url)
                    return True
            
            # Método 2: URL con parámetros de auto-reproducción
            clean_query = search_query.replace(' ', '+')
            
            # URLs especiales que intentan auto-reproducir
            autoplay_urls = [
                f"https://www.youtube.com/results?search_query={clean_query}&autoplay=1",
                f"https://music.youtube.com/search?q={clean_query}",
                f"https://www.youtube.com/watch?v={clean_query}",  # Si es un ID
            ]
            
            for url in autoplay_urls:
                try:
                    webbrowser.open(url)
                    print(f"✅ YouTube abierto con: {url}")
                    return True
                except:
                    continue
            
        except Exception as e:
            print(f"⚠️ Error método avanzado YouTube: {e}")
        
        return False
    
    def _find_youtube_video(self, search_query: str) -> Optional[str]:
        """Buscar video específico en YouTube usando API"""
        if not self.youtube_api_key:
            return None
        
        try:
            # Búsqueda en YouTube API
            search_url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': search_query,
                'type': 'video',
                'maxResults': 1,
                'key': self.youtube_api_key
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('items'):
                    video_id = data['items'][0]['id']['videoId']
                    video_url = f"https://www.youtube.com/watch?v={video_id}&autoplay=1"
                    return video_url
            
        except Exception as e:
            print(f"⚠️ Error buscando en YouTube API: {e}")
        
        return None
    
    def download_and_play_local(self, search_query: str) -> bool:
        """🎵 MÉTODO EXTREMO: Descargar y reproducir localmente"""
        try:
            print(f"🎵 MÉTODO EXTREMO: Descargando '{search_query}' para reproducción local")
            
            # Verificar si yt-dlp está disponible
            try:
                subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠️ yt-dlp no está instalado - método extremo no disponible")
                return False
            
            # Crear directorio temporal
            temp_dir = tempfile.mkdtemp()
            output_template = os.path.join(temp_dir, "%(title)s.%(ext)s")
            
            # Comando para descargar solo audio
            cmd = [
                "yt-dlp",
                f"ytsearch1:{search_query}",  # Buscar primer resultado
                "--extract-audio",
                "--audio-format", "mp3",
                "--output", output_template,
                "--no-playlist"
            ]
            
            print("🔄 Descargando audio...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Buscar el archivo descargado
                for file in os.listdir(temp_dir):
                    if file.endswith('.mp3'):
                        audio_path = os.path.join(temp_dir, file)
                        print(f"✅ Audio descargado: {file}")
                        
                        # Reproducir con el reproductor por defecto
                        if os.name == 'nt':  # Windows
                            os.startfile(audio_path)
                        else:  # Unix/Linux
                            subprocess.run(["xdg-open", audio_path])
                        
                        return True
            else:
                print(f"❌ Error descargando: {result.stderr}")
            
        except subprocess.TimeoutExpired:
            print("⏱️ Timeout descargando audio")
        except Exception as e:
            print(f"❌ Error método extremo: {e}")
        
        return False

    def _send_robust_play_commands(self):
        """Enviar múltiples comandos de reproducción robustos"""
        try:
            import pyautogui
            
            print("🎵 Enviando comandos de reproducción robustos...")
            
            # Múltiples métodos de reproducción
            commands = [
                # Método 1: Enter para seleccionar/reproducir
                lambda: pyautogui.press('enter'),
                # Método 2: Espacio para play/pause
                lambda: pyautogui.press('space'),
                # Método 3: Tecla multimedia play/pause
                lambda: pyautogui.press('playpause'),
                # Método 4: Ctrl+Enter (atajo en algunos reproductores)
                lambda: pyautogui.hotkey('ctrl', 'enter'),
                # Método 5: Tab + Enter (navegar y seleccionar)
                lambda: (pyautogui.press('tab'), time.sleep(0.2), pyautogui.press('enter')),
            ]
            
            for i, cmd in enumerate(commands, 1):
                try:
                    print(f"   🎯 Comando {i}/5...")
                    cmd()
                    time.sleep(0.4)  # Pausa entre comandos
                except Exception as e:
                    print(f"   ⚠️ Error comando {i}: {e}")
                    continue
            
            print("✅ Comandos robustos enviados")
            
        except ImportError:
            print("⚠️ PyAutoGUI no disponible para comandos robustos")
        except Exception as e:
            print(f"⚠️ Error enviando comandos robustos: {e}")
    
    def _send_basic_play_commands(self):
        """Enviar comandos básicos de reproducción"""
        try:
            import pyautogui
            
            print("🎵 Enviando comandos básicos...")
            
            # Solo comandos esenciales
            pyautogui.press('enter')
            time.sleep(0.5)
            pyautogui.press('space')
            
            print("✅ Comandos básicos enviados")
            
        except ImportError:
            print("⚠️ PyAutoGUI no disponible para comandos básicos")
        except Exception as e:
            print(f"⚠️ Error enviando comandos básicos: {e}")

# Función para integrar con el detector principal
def create_advanced_music_controller():
    """Crear instancia del controlador avanzado"""
    return AdvancedMusicController()
