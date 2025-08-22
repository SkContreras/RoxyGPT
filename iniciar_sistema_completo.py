"""
Iniciador Automático del Sistema Roxy Megurdy
============================================
Ejecuta todos los componentes necesarios automáticamente
"""

import os
import sys
import time
import subprocess
import signal
import threading
import requests
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class SystemLauncher:
    def __init__(self):
        self.processes = {}
        self.running = True
        
    def print_status(self, service, status, message=""):
        icons = {
            "STARTING": "🔄",
            "READY": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "INFO": "ℹ️"
        }
        colors = {
            "STARTING": Colors.YELLOW,
            "READY": Colors.GREEN,
            "ERROR": Colors.RED,
            "WARNING": Colors.YELLOW,
            "INFO": Colors.BLUE
        }
        icon = icons.get(status, "")
        color = colors.get(status, Colors.END)
        status_text = {
            "STARTING": "Iniciando...",
            "READY": "Listo",
            "ERROR": "Error",
            "WARNING": "Advertencia",
            "INFO": "Info"
        }.get(status, status)
        msg = f"{color}{icon} {service}: {status_text} {message}{Colors.END}"
        print(msg)

    def check_grok_api(self):
        """Verificar si la API de Grok está configurada"""
        try:
            if os.path.exists('.env'):
                with open('.env', 'r') as f:
                    for line in f:
                        if 'grok_api_key' in line and '=' in line:
                            key = line.split('=', 1)[1].strip().strip('"').strip("'")
                            if key and key != 'your_grok_api_key_here':
                                self.print_status("Grok API", "READY", "API key encontrada")
                                return True
            
            self.print_status("Grok API", "ERROR", "API key no encontrada en .env")
            return False
        except Exception as e:
            self.print_status("Grok API", "ERROR", f"Error verificando Grok: {e}")
            return False
    
    def check_ollama_running(self):
        """Verifica si Ollama ya está ejecutándose"""
        try:
            import ollama
            models = ollama.list()
            return True
        except:
            return False
    
    def warmup_ollama(self):
        """Precalienta Ollama enviando una consulta simple"""
        try:
            import ollama
            self.print_status("Ollama", "INFO", "Precalentando modelo llama3:latest...")
            
            # Enviar una consulta simple para precalentar
            response = ollama.chat(
                model='llama3:latest',
                messages=[{
                    'role': 'user',
                    'content': 'Hola, solo dime "ok" para confirmar que estás listo.'
                }],
                stream=False
            )
            
            if response and 'message' in response:
                self.print_status("Ollama", "READY", "Modelo llama3:latest precalentado y respondiendo correctamente")
                return True
            else:
                self.print_status("Ollama", "WARNING", "Respuesta inesperada del modelo")
                return False
                
        except Exception as e:
            self.print_status("Ollama", "ERROR", f"Error al precalentar: {str(e)}")
            return False
    
    def start_ollama(self):
        """Inicia Ollama si no está ejecutándose"""
        if self.check_ollama_running():
            self.print_status("Ollama", "READY", "Ya estaba ejecutándose")
            # Aunque esté ejecutándose, verificar que responde correctamente
            if self.warmup_ollama():
                return True
            else:
                self.print_status("Ollama", "WARNING", "Servicio iniciado pero modelo no responde bien")
                return False
        
        self.print_status("Ollama", "STARTING", "Iniciando servicio...")
        
        try:
            # Intentar iniciar ollama serve
            process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            self.processes['ollama'] = process
            
            # Esperar a que Ollama esté listo (puede tardar varios minutos la primera vez)
            self.print_status("Ollama", "INFO", "Primer arranque puede tardar 2-5 minutos...")
            for i in range(300):  # 5 minutos máximo para primer arranque
                time.sleep(1)
                if i % 10 == 0 and i > 0:  # Mostrar progreso cada 10 segundos
                    self.print_status("Ollama", "INFO", f"Esperando... {i//10}/30 (10s intervals)")
                if self.check_ollama_running():
                    self.print_status("Ollama", "READY", "Servicio iniciado, precalentando modelo...")
                    # Una vez que el servicio esté listo, precalentar el modelo
                    if self.warmup_ollama():
                        return True
                    else:
                        self.print_status("Ollama", "ERROR", "Servicio iniciado pero modelo no responde")
                        return False
                if process.poll() is not None:
                    # El proceso terminó
                    stdout, stderr = process.communicate()
                    if b"bind: Only one usage" in stderr:
                        # Ya estaba ejecutándose
                        self.print_status("Ollama", "READY", "Ya estaba ejecutándose")
                        # Verificar que el modelo responde
                        if self.warmup_ollama():
                            return True
                        else:
                            return False
                    else:
                        self.print_status("Ollama", "ERROR", f"Falló al iniciar: {stderr.decode()[:100]}")
                        return False
            
            self.print_status("Ollama", "ERROR", "Timeout esperando inicio")
            return False
            
        except Exception as e:
            self.print_status("Ollama", "ERROR", f"No se pudo iniciar: {str(e)}")
            return False
    
    def start_memory_server(self):
        """Inicia el servidor de memoria"""
        self.print_status("Servidor de Memoria", "STARTING")
        
        try:
            # Usar el python del entorno virtual si existe
            python_exe = ".venv\\Scripts\\python.exe" if os.path.exists(".venv\\Scripts\\python.exe") else "python"
            
            process = subprocess.Popen(
                [python_exe, "llama_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            self.processes['memory_server'] = process
            
            # Esperar a que el servidor esté listo
            for i in range(15):  # 15 segundos máximo
                time.sleep(1)
                try:
                    response = requests.get("http://127.0.0.1:5000/health", timeout=2)
                    if response.status_code == 200:
                        data = response.json()
                        ollama_status = "✅" if data.get('ollama_connected') else "⚠️"
                        self.print_status("Servidor de Memoria", "READY", f"Puerto 5000 {ollama_status}")
                        return True
                except:
                    pass
                    
                if process.poll() is not None:
                    stdout, stderr = process.communicate()
                    self.print_status("Servidor de Memoria", "ERROR", f"Proceso terminó: {stderr.decode()[:100]}")
                    return False
            
            self.print_status("Servidor de Memoria", "ERROR", "Timeout esperando respuesta")
            return False
            
        except Exception as e:
            self.print_status("Servidor de Memoria", "ERROR", f"Error al iniciar: {str(e)}")
            return False
    
    def start_roxy_bot(self):
        """Inicia el bot Roxy con sistema unificado"""
        self.print_status("Bot Roxy", "READY", "Sistema unificado listo para conversar")
        
        try:
            # Usar el python del entorno virtual si existe
            python_exe = ".venv\\Scripts\\python.exe" if os.path.exists(".venv\\Scripts\\python.exe") else "python"
            
            # Ejecutar directamente importando el módulo unificado
            import sys
            if '.' not in sys.path:
                sys.path.append('.')
            
            self.print_status("Bot Roxy", "READY", "Iniciando sistema unificado...")
            print(f"{Colors.GREEN}🎤 Roxy Unificada está lista para conversar!{Colors.END}")
            print(f"{Colors.CYAN}💬 Sistema inteligente: Un solo detector para todo{Colors.END}\n")
            
            # Importar y ejecutar el bot unificado
            import bot_roxy_unified
            bot_roxy_unified.main()
            
        except KeyboardInterrupt:
            self.print_status("Bot Roxy", "INFO", "Interrumpido por usuario")
        except Exception as e:
            self.print_status("Bot Roxy", "ERROR", f"Error al ejecutar: {str(e)}")
            # Fallback: ejecutar como subproceso
            try:
                self.print_status("Bot Roxy", "INFO", "Intentando método alternativo...")
                
                # Ejecutar con salida visible
                result = subprocess.run([python_exe, "bot_roxy_unified.py"], 
                                      stdout=None,  # Heredar stdout 
                                      stderr=None,  # Heredar stderr
                                      stdin=None,   # Heredar stdin
                                      text=True)
                
                if result.returncode != 0:
                    self.print_status("Bot Roxy", "ERROR", f"Bot terminó con código {result.returncode}")
                    
            except Exception as e2:
                self.print_status("Bot Roxy", "ERROR", f"Error en método alternativo: {str(e2)}")
                print(f"{Colors.RED}💡 Sugerencia: Ejecuta 'python bot_roxy_unified.py' directamente{Colors.END}")
    
    def cleanup(self):
        print(f"\n{Colors.YELLOW}🧹 Cerrando todos los servicios...{Colors.END}")
        
        for service_name, process in self.processes.items():
            if process and process.poll() is None:
                try:
                    if os.name == 'nt':
                        # Windows
                        process.send_signal(signal.CTRL_BREAK_EVENT)
                    else:
                        # Unix/Linux
                        process.terminate()
                    
                    try:
                        process.wait(timeout=5)
                        self.print_status(service_name, "INFO", "Cerrado correctamente")
                    except subprocess.TimeoutExpired:
                        process.kill()
                        self.print_status(service_name, "INFO", "Forzado a cerrar")
                        
                except Exception as e:
                    self.print_status(service_name, "ERROR", f"Error al cerrar: {str(e)}")
    
    def run(self):
        print(f"{Colors.PURPLE}{Colors.BOLD}🚀 INICIADOR AUTOMÁTICO - ROXY MEGURDY\n🎯 SISTEMA UNIFICADO INTELIGENTE\n========================================={Colors.END}")
        
        try:
            # 1. Verificar dependencias críticas para sistema unificado
            self.print_status("Sistema", "INFO", "Verificando sistema unificado...")
            
            critical_files = [
                "bot_roxy_unified.py",           # Bot principal unificado
                "unified_command_detector.py",   # Detector unificado
                "personality_config.py"          # Configuración de personalidad
            ]
            
            missing_files = []
            for file in critical_files:
                if not os.path.exists(file):
                    missing_files.append(file)
                else:
                    self.print_status("Archivos", "READY", f"✅ {file}")
            
            if missing_files:
                self.print_status("Sistema", "ERROR", f"Archivos críticos faltantes: {missing_files}")
                return
            
            # 2. Verificar APIs necesarias para el sistema híbrido
            self.print_status("IA", "INFO", "Verificando sistema híbrido Grok + Llama3...")
            
            # Verificar Grok API
            grok_ok = self.check_grok_api()
            
            # Verificar e iniciar Ollama/Llama3
            ollama_ok = self.start_ollama()
            
            if not grok_ok and not ollama_ok:
                self.print_status("Sistema", "ERROR", "Ni Grok ni Ollama están disponibles - el bot no funcionará correctamente")
                print(f"{Colors.YELLOW}💡 Configura grok_api_key en .env y/o instala Ollama{Colors.END}")
                return
            elif not grok_ok:
                self.print_status("Sistema", "WARNING", "Solo Ollama disponible - funcionalidad limitada")
            elif not ollama_ok:
                self.print_status("Sistema", "WARNING", "Solo Grok disponible - sin detección de comandos")
            else:
                self.print_status("Sistema", "READY", "Sistema híbrido completo: Grok + Llama3")
            
            time.sleep(2)  # Pausa para estabilización
            
            # 3. Iniciar servidor de memoria (opcional)
            self.start_memory_server()
            time.sleep(1)
            
            # 4. Mostrar estado del sistema unificado
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ¡SISTEMA UNIFICADO OPERATIVO!{Colors.END}")
            print(f"{Colors.CYAN}🧠 FLUJO UNIFICADO ACTIVADO: Entrada → Llama3 → Grok → TTS{Colors.END}")
            print(f"{Colors.BLUE}📊 Servicios activos: Detector Unificado, Llama3, Grok, PersonalityConfig, ElevenLabs TTS, Contexto{Colors.END}")
            print(f"{Colors.PURPLE}⚙️ Características: Un solo detector, comandos combinados, español/spanglish, alias, conversación musical, ejecución robusta, personalidad consistente{Colors.END}")
            print(f"{Colors.CYAN}🎯 Ejemplos: 'pon música de bad bunny', 'abre youtube', 'ver star wars', '¿cómo estás?'{Colors.END}")
            print(f"{Colors.YELLOW}💬 IMPORTANTE: Todas las respuestas aparecerán aquí abajo{Colors.END}")
            print(f"{Colors.BLUE}📢 Formato: 🎤 Roxy: [su respuesta]{Colors.END}")
            print("=" * 60)
            
            # 6. Iniciar bot Roxy con sistema unificado
            self.start_roxy_bot()
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⌨️  Interrupción detectada...{Colors.END}")
        
        finally:
            self.cleanup()
            print(f"\n{Colors.CYAN}👋 ¡Sistema unificado cerrado completamente!{Colors.END}")

def main():
    """Función principal"""
    # Cambiar al directorio correcto
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    launcher = SystemLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
