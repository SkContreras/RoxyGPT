"""
Bot Roxy Megurdy - Sistema Unificado
===================================
Asistente virtual con sistema de detección unificado e inteligente
Usa un solo detector para todos los comandos con Llama3 + Grok
"""

import os
import sys
import json
import time
import threading
import re
import requests
import tempfile
import random
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Imports para funcionalidades del bot
import speech_recognition as sr
import pygame

# Imports locales
from unified_command_detector import UnifiedCommandDetector, CommandResult
from auto_dj_mode import AutoDJMode
from music_history_manager import MusicHistoryManager
from personality_config import PersonalityConfig
from intelligent_memory_manager import MemoryManager
from dj_narrator_mode import DJNarratorMode, integrate_dj_narrator_with_spotify
from enhanced_voice_system import EnhancedVoiceSystem, AudioConfig, VoiceResult

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class RoxyBotUnified:
    def __init__(self):
        """Inicializar el bot Roxy con sistema unificado"""
        print(f"{Colors.PURPLE}{Colors.BOLD}")
        print("🚀 ROXY MEGURDY - SISTEMA UNIFICADO")
        print("===================================")
        print(f"{Colors.END}")
        
        # 📊 Estadísticas
        self.stats = {
            "mensajes_procesados": 0,
            "comandos_ejecutados": 0,
            "conversaciones": 0,
            "tiempo_inicio": time.time()
        }
        
        # 🧠 Detector unificado (NÚCLEO DEL SISTEMA)
        self.print_status("Detector", "STARTING", "Inicializando detector unificado...")
        # 🎯 DETECTOR UNIFICADO INTELIGENTE
        self.unified_detector = UnifiedCommandDetector(grok_callback=self.get_grok_info)
        self.print_status("Detector", "READY", "Detector unificado listo con Llama3 + Grok")
        
        # 🎤 Sistema de reconocimiento de voz mejorado
        self.print_status("Voz", "STARTING", "Inicializando sistema de voz mejorado...")
        try:
            # Configurar sistema de voz con parámetros optimizados
            audio_config = AudioConfig(
                energy_threshold=3000,  # Filtrar más ruido
                timeout=2.0,  # Respuesta más rápida
                phrase_time_limit=12.0,  # Permitir frases más largas
                pause_threshold=0.6,  # Detectar pausas más rápido
                min_audio_length=0.3,  # Filtrar audio muy corto
                require_confirmation=["eliminar", "borrar", "cerrar", "apagar", "desinstalar"]
            )
            self.voice_system = EnhancedVoiceSystem(audio_config)
            self.microphone_available = self.voice_system.is_available
            
            if self.microphone_available:
                self.print_status("Voz", "READY", "Sistema de voz mejorado activo con filtros inteligentes")
            else:
                self.print_status("Voz", "WARNING", "Sistema de voz no disponible")
                
        except Exception as e:
            self.print_status("Voz", "ERROR", f"Error inicializando sistema de voz: {e}")
            self.voice_system = None
            self.microphone_available = False
        
        # 🔊 Sistema de audio
        pygame.mixer.init()
        pygame.mixer.music.set_volume(0.3)
        
        # 👤 Personalidad y memoria
        try:
            self.personality = PersonalityConfig()
            self.memory_manager = MemoryManager()
            self.print_status("Personalidad", "READY", "Sistema de personalidad activo")
        except Exception as e:
            self.print_status("Personalidad", "ERROR", f"Error: {e}")
            self.personality = None
            self.memory_manager = None
        
        # 🌐 APIs y configuración
        self.load_api_keys()
        
        # 🔊 Estado del TTS
        self.tts_enabled = bool(self.elevenlabs_api_key)
        if self.tts_enabled:
            self.print_status("TTS", "READY", f"Síntesis de voz ACTIVA con voz {self.elevenlabs_voice_id[:8]}...")
        else:
            self.print_status("TTS", "WARNING", "Síntesis de voz DESACTIVADA - configura elevenlabs_api_key")
        
        # 📝 Historial de conversación
        self.conversation_history = []
        self.context = {}
        
        # 🎤 Modo DJ Narrador
        self.dj_narrator = DJNarratorMode()
        self.dj_mode_active = False
        self.print_status("DJ Mode", "READY", "Modo DJ Narrador disponible")
        
        # 🤖 Auto DJ Mode (NUEVO)
        self.auto_dj = None
        self.auto_dj_active = False
        self.music_history = MusicHistoryManager()
        self.print_status("Auto DJ", "READY", "DJ Automático disponible")
        
        self.running = True
        self.print_status("Sistema", "READY", "Roxy lista con sistema unificado")
    
    def print_status(self, service, status, message=""):
        """Imprimir estado con colores"""
        if status == "STARTING":
            print(f"{Colors.YELLOW}🔄 {service}: Iniciando... {message}{Colors.END}")
        elif status == "READY":
            print(f"{Colors.GREEN}✅ {service}: Listo {message}{Colors.END}")
        elif status == "ERROR":
            print(f"{Colors.RED}❌ {service}: Error {message}{Colors.END}")
        elif status == "WARNING":
            print(f"{Colors.YELLOW}⚠️  {service}: Advertencia {message}{Colors.END}")
        elif status == "INFO":
            print(f"{Colors.BLUE}ℹ️  {service}: {message}{Colors.END}")
        elif status == "USER":
            print(f"{Colors.CYAN}👤 {service}: {message}{Colors.END}")
        elif status == "COMMAND":
            print(f"{Colors.PURPLE}🎯 {service}: {message}{Colors.END}")
    
    def get_recent_conversation_history(self) -> List[Dict]:
        """Obtener historial reciente de conversación para análisis de contexto"""
        if not hasattr(self, 'conversation_history'):
            self.conversation_history = []
        
        # Retornar últimos 5 intercambios de conversación
        return self.conversation_history[-5:] if self.conversation_history else []
    
    def load_api_keys(self):
        """Cargar claves de API"""
        self.grok_api_key = None
        self.elevenlabs_api_key = None
        self.elevenlabs_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Default voice (Rachel)
        
        if os.path.exists('.env'):
            try:
                with open('.env', 'r') as f:
                    for line in f:
                        if 'grok_api_key' in line and '=' in line:
                            key = line.split('=', 1)[1].strip().strip('"').strip("'")
                            if key and key != 'your_grok_api_key_here':
                                self.grok_api_key = key
                                self.print_status("Grok", "READY", "API configurada")
                        elif 'elevenlabs_api_key' in line and '=' in line:
                            key = line.split('=', 1)[1].strip().strip('"').strip("'")
                            if key and key != 'your_elevenlabs_api_key_here':
                                self.elevenlabs_api_key = key
                                self.print_status("ElevenLabs", "READY", "TTS configurado")
                        elif 'elevenlabs_voice_id' in line and '=' in line:
                            voice_id = line.split('=', 1)[1].strip().strip('"').strip("'")
                            if voice_id:
                                self.elevenlabs_voice_id = voice_id
                                self.print_status("Voz", "READY", f"Voice ID: {voice_id[:8]}...")
            except Exception as e:
                self.print_status("APIs", "WARNING", f"Error cargando .env: {e}")
        
        if not self.grok_api_key:
            self.print_status("Grok", "WARNING", "API no configurada - funcionalidad limitada")
        
        if not self.elevenlabs_api_key:
            self.print_status("ElevenLabs", "WARNING", "API no configurada - sin síntesis de voz")
    
    def setup_microphone(self):
        """Configurar micrófono (método legacy - ahora usa EnhancedVoiceSystem)"""
        if self.voice_system:
            return self.voice_system.recalibrate()
        return False
    
    def recognize_speech(self):
        """🎤 Capturar voz del usuario con sistema mejorado"""
        if not self.microphone_available or not self.voice_system:
            self.print_status("Voz", "ERROR", "Sistema de voz no disponible")
            return None
            
        try:
            result = self.voice_system.recognize_speech_enhanced()
            
            if result.is_valid and result.text:
                # Mostrar información del reconocimiento
                confidence_indicator = "🟢" if result.confidence > 0.7 else "🟡" if result.confidence > 0.4 else "🔴"
                self.print_status("Usuario", "USER", f"'{result.text}' {confidence_indicator} ({result.confidence:.2f})")
                
                # Verificar si requiere confirmación
                if result.requires_confirmation:
                    if self.voice_system.confirm_command(result.text):
                        return result.text
                    else:
                        self.print_status("Voz", "INFO", "Comando cancelado por el usuario")
                        return None
                
                return result.text
            else:
                if result.error_message and "Timeout" not in result.error_message:
                    self.print_status("Voz", "INFO", f"Audio filtrado: {result.error_message}")
                return None
                
        except Exception as e:
            self.print_status("Voz", "ERROR", f"Error en reconocimiento: {e}")
            return None
    
    def process_user_input(self, user_input):
        """🧠 Procesar entrada del usuario - SISTEMA UNIFICADO"""
        if not user_input or user_input == "SALIR":
            return None
        low = user_input.lower().strip()
        if low.startswith("olvida ") and self.personality:
            term = low[7:].strip()
            if hasattr(self.personality, 'forget_value'):
                removed = self.personality.forget_value(term)
                if removed:
                    return f"(Olvidado: {', '.join(removed)})"
                else:
                    return f"(No encontré datos relacionados con '{term}')"
            else:
                return "(Función de olvido no disponible)"
        
        self.stats["mensajes_procesados"] += 1
        
        # 🎯 ANÁLISIS UNIFICADO CON CONTEXTO
        self.print_status("Analizando", "INFO", "Detector unificado procesando...")
        
        # Actualizar contexto con historial reciente
        recent_context = self.get_recent_conversation_history()
        
        # Pasar historial de conversación al detector unificado
        result = self.unified_detector.analyze_command(user_input, recent_context)
        
        # 🚀 EJECUTAR ACCIÓN BASADA EN RESULTADO
        if result.is_command:
            return self.handle_unified_command(result, user_input)
        else:
            return self.handle_conversation(user_input)
    
    def handle_unified_command(self, result: CommandResult, original_input: str):
        """🎯 Manejar comando detectado por sistema unificado"""
        command_type_emoji = {
            'app': '📱',
            'music': '🎵', 
            'content': '🎬',
            'conversation': '💬'
        }
        
        emoji = command_type_emoji.get(result.command_type, '🎯')
        self.print_status("Comando", "COMMAND", 
                         f"{emoji} {result.command_type.upper()} → {result.action} (confianza: {result.confidence:.2f})")
        
        # 🎤 MODO DJ NARRADOR PARA MÚSICA
        if result.command_type == 'music' and self.dj_mode_active:
            return self.handle_music_with_dj_narration(result, original_input)
        
        # 🎯 DECISIÓN BASADA EN CONFIANZA DINÁMICO
        confidence_calculator = self.unified_detector.confidence_calculator
        confidence_level = confidence_calculator.get_confidence_level(result.confidence)
        
        # Mostrar nivel de confianza al usuario
        confidence_msg = confidence_calculator.get_confidence_explanation(result, result.confidence)
        self.print_status("Confianza", "INFO", confidence_msg)
        
        # Decidir acción basada en nivel de confianza
        if confidence_calculator.should_execute_immediately(result.confidence):
            # Confianza muy alta - ejecutar inmediatamente
            success = self.unified_detector.execute_command(result)
            
        elif confidence_level == 'high':
            # Confianza alta - ejecutar inmediatamente (sin confirmación)
            success = self.unified_detector.execute_command(result)
            
        elif confidence_calculator.should_request_confirmation(result.confidence):
            # Confianza media - pedir confirmación
            confirmation_msg = f"🤔 Detecté: {result.action}"
            if result.target:
                confirmation_msg += f" → {result.target}"
            
            # Mostrar información adicional si está disponible
            execution_data = result.execution_data or {}
            if execution_data.get('artist'):
                confirmation_msg += f" (artista: {execution_data['artist']})"
            elif execution_data.get('genre'):
                confirmation_msg += f" (género: {execution_data['genre']})"
            elif execution_data.get('mood') and execution_data['mood'] != 'auto':
                confirmation_msg += f" (mood: {execution_data['mood']})"
                
            confirmation_msg += f"\n📊 Confianza: {result.confidence:.2f} (< 0.7 → requiere confirmación)"
            confirmation_msg += f"\n¿Proceder? (s/n): "
            
            print(confirmation_msg, end="")
            try:
                if self.voice_system and self.voice_system.is_available:
                    # Usar confirmación por voz si está disponible
                    print("\n🎤 Puedes responder por voz o escribir...")
                    response = input().lower().strip()
                    if not response:
                        # Si no escribió nada, intentar voz
                        voice_result = self.voice_system.recognize_speech_enhanced(show_status=False)
                        if voice_result.is_valid and voice_result.text:
                            response = voice_result.text.lower()
                else:
                    response = input().lower().strip()
                
                if any(word in response for word in ['s', 'si', 'sí', 'y', 'yes', 'confirmar', 'ok', 'vale']):
                    success = self.unified_detector.execute_command(result)
                else:
                    return "❌ Comando cancelado. ¿Puedes especificar mejor lo que quieres hacer?"
            except KeyboardInterrupt:
                return "❌ Comando cancelado."
                
        elif confidence_level == 'low':
            # Confianza baja - sugerir alternativas pero ejecutar si el usuario insiste
            alternatives_msg = f"Baja confianza en el comando ({result.confidence:.2f}). "
            alternatives_msg += f"¿Realmente quieres {result.action}"
            if result.target:
                alternatives_msg += f" → {result.target}"
            alternatives_msg += "? (s/n): "
            
            print(alternatives_msg, end="")
            try:
                user_response = input().lower().strip()
                if user_response in ['s', 'si', 'sí', 'y', 'yes']:
                    success = self.unified_detector.execute_command(result)
                else:
                    return "¿Puedes reformular tu solicitud de manera más específica?"
            except KeyboardInterrupt:
                return "Comando cancelado."
                
        else:
            # Confianza muy baja - rechazar y pedir clarificación
            return f"No estoy segura de entender tu solicitud (confianza: {result.confidence:.2f}). ¿Puedes ser más específico sobre lo que quieres hacer?"
        
        if success:
            self.stats["comandos_ejecutados"] += 1
            response = result.natural_response or f"¡Listo usuario! Comando {result.action} ejecutado"
        else:
            response = f"Ay perdón usuario, tuve problemas ejecutando {result.action}. ¿Intentas de nuevo?"
        
        # Guardar en historial
        self.add_to_history(original_input, response, result.command_type, {
            'action': result.action,
            'target': result.target,
            'confidence': result.confidence
        })
        
        return response
    
    def handle_conversation(self, user_input):
        """💬 Manejar conversación normal"""
        self.stats["conversaciones"] += 1
        self.print_status("Conversación", "INFO", "Procesando con Grok...")
        
        # Usar Grok para conversación si está disponible
        if self.grok_api_key:
            response = self.get_grok_response(user_input)
        else:
            response = self._get_fallback_response(user_input)
        
        self.add_to_history(user_input, response, "conversation")
        learn_msg = self._maybe_learn_fact(user_input)
        if learn_msg:
            response = response + "\n" + learn_msg
        return response

    def _maybe_learn_fact(self, user_input: str):
        if not self.personality:
            return None
        txt = user_input.lower()
        patterns = [
            (r"mi\s+(placa base|motherboard)\s+es\s+(.+)", ("hardware","motherboard")),
            (r"mi\s+gpu\s+es\s+(.+)", ("hardware","gpu")),
            (r"mi\s+cpu\s+es\s+(.+)", ("hardware","cpu")),
            (r"tengo\s+(\d+)\s*gb\s+de\s+ram", ("hardware","ram_gb")),
            (r"mi\s+anime\s+favorito\s+es\s+(.+)", ("intereses","anime_favorito")),
            (r"mi\s+juego\s+favorito\s+es\s+(.+)", ("intereses","juego_favorito")),
        ]
        for pat,(cat,key) in patterns:
            m = re.search(pat, txt)
            if m:
                raw = m.group(2) if m.lastindex and m.lastindex>=2 else m.group(1)
                val = raw.strip().strip('.')
                if not val or len(val)<2:
                    return None
                # Confirmación implícita: si usuario añade "no guardes" cancelamos
                if 'no guardes' in txt or 'no recuerdes' in txt:
                    return "(No guardaré ese dato)"
                # Crear categoría si no existe
                if cat not in self.personality.config:
                    self.personality.config[cat] = {}
                bucket = self.personality.config[cat]
                existing = bucket.get(key)
                if existing is None:
                    bucket[key] = val
                else:
                    if isinstance(existing, list):
                        if val not in existing:
                            existing.append(val)
                    else:
                        if existing != val:
                            bucket[key] = [existing, val]
                # Persistir si YAML disponible
                try:
                    import yaml
                    with open(self.personality.yaml_path,'w',encoding='utf-8') as f:
                        yaml.safe_dump(self.personality.config,f,allow_unicode=True,sort_keys=False)
                except Exception:
                    pass
                return f"(He aprendido {key}: {val})"
        return None
    
    def get_grok_info(self, query: str) -> str:
        """🔍 Obtener información específica de Grok para el detector de comandos"""
        if not self.grok_api_key:
            return f"Sin información disponible sobre: {query}"
        
        try:
            # Consulta específica de información, no conversación
            messages = [
                {"role": "system", "content": """Eres un asistente de información que proporciona datos específicos y concisos.
Responde de manera directa y factual, sin emojis ni formato especial.
Tu trabajo es proporcionar información específica sobre anime, música, series, artistas, etc."""},
                {"role": "user", "content": query}
            ]
            
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.grok_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "messages": messages,
                    "model": "grok-2-1212",
                    "temperature": 0.3,  # Más determinista para información factual
                    "max_tokens": 200    # Respuestas más concisas
                },
                timeout=10
            )
            
            if response.status_code == 200:
                ai_response = response.json()['choices'][0]['message']['content']
                return ai_response
            else:
                print(f"⚠️ Error Grok Info: {response.status_code}")
                return f"Error obteniendo información sobre: {query}"
                
        except requests.exceptions.Timeout:
            print("⚠️ Timeout en consulta a Grok")
            return f"Timeout consultando información sobre: {query}"
        except Exception as e:
            print(f"⚠️ Error Grok Info: {e}")
            return f"Error consultando información sobre: {query}"

    def get_grok_response(self, user_input):
        """🤖 Obtener respuesta de xAI Grok"""
        if not self.grok_api_key:
            return self._get_fallback_response(user_input)
        
        try:
            # --- NUEVO: Construir contexto usando PersonalityConfig real + hardware si relevante ---
            system_personality = self.personality.get_system_prompt() if self.personality else "Eres asistente virtual."

            # Detectar si la pregunta requiere hardware (keywords)
            hardware_context = ""
            if self.personality and self._needs_hardware_context(user_input):
                hw_summary = self.personality.get_hardware_summary()
                if hw_summary:
                    hardware_context = f"\nContexto hardware usuario: {hw_summary}"

            # Historial breve para continuidad
            recent_history = []
            for h in self.conversation_history[-4:]:
                if h['type'] == 'conversation':
                    recent_history.append({
                        'usuario': h['user_input'],
                        'roxy': h['bot_response']
                    })
            history_json = json.dumps(recent_history, ensure_ascii=False)
            personality_context = f"{system_personality}\nHistorial reciente (compacto): {history_json}{hardware_context}"
            
            # Historial para contexto
            context_messages = []
            for h in self.conversation_history[-4:]:
                if h['type'] == 'conversation':
                    context_messages.extend([
                        {"role": "user", "content": h['user_input']},
                        {"role": "assistant", "content": h['bot_response']}
                    ])
            
            # Apodo preferido
            apodo = "usuario"
            if self.personality:
                apodo = self.personality.config.get("usuario", {}).get("apodo", apodo)

            messages = [
                {"role": "system", "content": f"""{personality_context}
REGLAS DE ESTILO:
- Sin emojis ni adornos raros (TTS limpio)
- Usa el apodo principal '{apodo}' de forma natural, ocasionalmente sin repetirlo en exceso
- Si la pregunta es sobre rendimiento de juegos, usa el contexto de hardware incluido (no vuelvas a preguntarlo)
"""},
            ] + context_messages + [
                {"role": "user", "content": user_input}
            ]
            
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.grok_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "messages": messages,
                    "model": "grok-2-1212",
                    "temperature": 0.7,
                    "max_tokens": 300
                },
                timeout=15
            )
            
            if response.status_code == 200:
                ai_response = response.json()['choices'][0]['message']['content']
                
                # Limpiar respuesta usando función específica para ElevenLabs
                clean_response = self.clean_text_for_elevenlabs(ai_response)
                
                return clean_response
            else:
                self.print_status("Grok", "ERROR", f"Error API: {response.status_code}")
                return self._get_fallback_response(user_input)
                
        except Exception as e:
            self.print_status("Grok", "ERROR", f"Error: {e}")
            return self._get_fallback_response(user_input)

    # --- NUEVO: Heurística para detectar si se necesita contexto de hardware ---
    def _needs_hardware_context(self, user_input: str) -> bool:
        if not user_input:
            return False
        text = user_input.lower()
        keywords = ["gpu", "cpu", "ram", "fps", "frames", "rendimiento", "requisitos", "correr", "corra", "funciona", "hardware", "grafica", "gráfica"]
        gaming_terms = ["juego", "game", "steam", "fortnite", "valorant", "league", "call of duty", "cyberpunk", "re4", "gta", "elden"]
        if any(k in text for k in keywords):
            return True
        # Si menciona un juego y verbo correr/funcionar implícito
        if any(g in text for g in gaming_terms) and ("correr" in text or "corra" in text or "funciona" in text or "irá" in text or "ira" in text):
            return True
        return False
    
    def _get_fallback_response(self, user_input):
        """🔄 Respuestas de respaldo cuando Grok no está disponible"""
        input_lower = user_input.lower()
        
        fallback_responses = {
            'hola': "¡Hola usuario! ¿Cómo estás hoy?",
            'adiós': "¡Nos vemos luego usuario! Cuídate mucho",
            'gracias': "De nada usuario, para eso estoy aquí",
            'cómo estás': "Estoy muy bien usuario, lista para ayudarte en lo que necesites",
            'te amo': "Ay... yo también te quiero mucho usuario",
            'eres linda': "Jeje gracias usuario, tú también eres muy especial para mí"
        }
        
        for key, response in fallback_responses.items():
            if key in input_lower:
                return response
        
        return "Entiendo usuario, aunque no tengo todas mis funciones disponibles ahora. ¿En qué más puedo ayudarte?"
    
    def add_to_history(self, user_input, bot_response, msg_type, metadata=None):
        """📝 Agregar interacción al historial"""
        entry = {
            'user_input': user_input,
            'bot_response': bot_response,
            'type': msg_type,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.conversation_history.append(entry)
        
        # Mantener solo últimas 20 interacciones
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def clean_text_for_elevenlabs(self, text):
        """🧹 Limpiar texto para ElevenLabs eliminando caracteres problemáticos"""
        if not text:
            return ""
        
        # 1. Eliminar caracteres específicamente problemáticos según documentación ElevenLabs
        problematic_chars = ['{', '}', '<', '>', '[', ']']
        clean_text = text
        for char in problematic_chars:
            clean_text = clean_text.replace(char, '')
        
        # 2. Eliminar emojis usando regex Unicode más completo
        # Patrón más robusto que cubre todos los rangos de emojis
        emoji_pattern = re.compile(
            "["
            "\U0001F1E0-\U0001F1FF"  # banderas (iOS)
            "\U0001F300-\U0001F5FF"  # símbolos y pictogramas (incluye 🔧 U+1F527)
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F680-\U0001F6FF"  # transporte y símbolos de mapa
            "\U0001F700-\U0001F77F"  # símbolos alquímicos
            "\U0001F780-\U0001F7FF"  # símbolos geométricos extendidos
            "\U0001F800-\U0001F8FF"  # flechas suplementarias C
            "\U0001F900-\U0001F9FF"  # símbolos suplementarios
            "\U0001FA00-\U0001FA6F"  # símbolos de ajedrez
            "\U0001FA70-\U0001FAFF"  # símbolos extendidos A
            "\U00002600-\U000026FF"  # símbolos misceláneos (incluye ☀️)
            "\U00002700-\U000027BF"  # dingbats
            "\U0000FE00-\U0000FE0F"  # selectores de variación
            "\U0001F000-\U0001F02F"  # fichas de mahjong
            "\U0001F0A0-\U0001F0FF"  # cartas de juego
            "\U0001F100-\U0001F1FF"  # símbolos alfanuméricos encerrados
            "\U0001F200-\U0001F2FF"  # ideogramas CJK encerrados
            "\U0001F300-\U0001F5FF"  # símbolos misceláneos y pictogramas
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F680-\U0001F6FF"  # símbolos de transporte y mapa
            "\U0001F700-\U0001F773"  # símbolos alquímicos
            "\U0001F780-\U0001F7D8"  # símbolos geométricos extendidos
            "\U0001F800-\U0001F80B"  # flechas suplementarias C
            "\U0001F810-\U0001F847"  # flechas suplementarias C
            "\U0001F850-\U0001F859"  # flechas suplementarias C
            "\U0001F860-\U0001F887"  # flechas suplementarias C
            "\U0001F890-\U0001F8AD"  # flechas suplementarias C
            "\U00002000-\U0000206F"  # puntuación general
            "]+", flags=re.UNICODE)
        clean_text = emoji_pattern.sub('', clean_text)
        
        # 2.1. Eliminar emojis específicos que podrían escaparse (método de respaldo)
        specific_emojis = ['🔧', '🎵', '🎤', '🎯', '🚀', '✅', '❌', '⚠️', '📊', '🔊', '🔇', '💬', '🎬', '📱', '🧠', '🎭', '🤖', '🎧', '🎪', '🔄', '💡']
        for emoji in specific_emojis:
            clean_text = clean_text.replace(emoji, '')
        
        # 3. Reemplazar puntos suspensivos por pausa natural
        clean_text = clean_text.replace('...', ', ')
        clean_text = clean_text.replace('…', ', ')  # Carácter de puntos suspensivos Unicode
        
        # 4. Convertir símbolos comunes a texto
        replacements = {
            '$': ' dólares ',
            '€': ' euros ',
            '£': ' libras ',
            '%': ' por ciento ',
            '&': ' y ',
            '@': ' arroba ',
            '#': ' numeral ',
            '+': ' más ',
            '=': ' igual ',
            '*': ' por ',
            '/': ' entre ',
            '\\': ' ',
            '|': ' ',
            '~': ' ',
            '^': ' ',
            '`': ' ',
            '_': ' ',
        }
        
        for symbol, replacement in replacements.items():
            clean_text = clean_text.replace(symbol, replacement)
        
        # 5. Limpiar caracteres restantes manteniendo solo texto válido
        clean_text = re.sub(r'[^\w\s\.,!?¡¿áéíóúñü\-]', '', clean_text, flags=re.IGNORECASE)
        
        # 6. Limpiar espacios múltiples
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        return clean_text.strip()

    def speak_response(self, text):
        """🔊 Convertir texto a voz usando ElevenLabs"""
        if not self.elevenlabs_api_key:
            self.print_status("TTS", "WARNING", "ElevenLabs no configurado - saltando síntesis de voz")
            return False
        
        try:
            # Limpiar texto usando función específica para ElevenLabs
            clean_text = self.clean_text_for_elevenlabs(text)
            
            if not clean_text:
                return False
            
            # Usar voice ID configurada
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": clean_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.6,       # Más estable
                    "similarity_boost": 0.8,  # Mantener consistencia
                    "style": 0.3,           # Un poco más de estilo
                    "use_speaker_boost": True
                }
            }
            
            self.print_status("TTS", "INFO", f"Sintetizando: '{clean_text[:30]}...'")
            
            response = requests.post(url, json=data, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Crear archivo temporal para el audio
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                    tmp_file.write(response.content)
                    tmp_file_path = tmp_file.name
                
                # Reproducir audio
                pygame.mixer.music.load(tmp_file_path)
                pygame.mixer.music.play()
                
                # Esperar a que termine la reproducción
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                # Limpiar archivo temporal
                try:
                    os.unlink(tmp_file_path)
                except:
                    pass  # No importa si no se puede eliminar
                
                self.print_status("TTS", "READY", "Síntesis completada")
                return True
            else:
                error_msg = f"Error {response.status_code}"
                if response.status_code == 401:
                    error_msg += " - API Key inválida"
                elif response.status_code == 422:
                    error_msg += " - Texto demasiado largo o inválido"
                elif response.status_code == 429:
                    error_msg += " - Límite de rate excedido"
                
                self.print_status("TTS", "ERROR", error_msg)
                return False
                
        except Exception as e:
            self.print_status("TTS", "ERROR", f"Error síntesis: {e}")
            return False
    
    def handle_music_with_dj_narration(self, result: CommandResult, original_input: str):
        """🎤 Manejar música con narración de DJ"""
        # Detectar mood basado en el input
        mood = self.detect_music_mood(original_input)
        
        # Iniciar sesión DJ si no está activa
        if not self.dj_narrator.session_active:
            dj_intro = self.dj_narrator.start_session(mood)
            print(f"\n{Colors.PURPLE}🎤 DJ Roxy: {dj_intro}{Colors.END}")
        
        # Ejecutar comando de música
        success = self.unified_detector.execute_command(result)
        
        if success:
            # Obtener información del track si está disponible
            if hasattr(self.unified_detector, 'spotify_controller_unified') and self.unified_detector.spotify_controller_unified:
                current_track = self.unified_detector.spotify_controller_unified.get_current_track()
                if current_track:
                    # Narración del DJ (solo si hay algo que decir)
                    narration = self.dj_narrator.introduce_track(
                        artist=current_track['artist'],
                        song=current_track['name'],
                        genre=self.guess_genre_from_query(original_input)
                    )
                    if narration:  # Solo mostrar si hay narración
                        print(f"\n{Colors.PURPLE}🎤 DJ Roxy: {narration}{Colors.END}")
                    
                    response = f"🎵 ¡Reproduciendo! {current_track['artist']} - {current_track['name']}"
                else:
                    # Narración genérica (solo ocasionalmente)
                    if random.random() < 0.4:  # 40% probabilidad
                        request_response = self.dj_narrator.handle_user_request(
                            original_input, 
                            result.target or "artista", 
                            "canción solicitada"
                        )
                        print(f"\n{Colors.PURPLE}🎤 DJ Roxy: {request_response}{Colors.END}")
                    response = "🎵 ¡Música en camino!"
            else:
                # Sin información específica del track (solo ocasionalmente)
                if random.random() < 0.3:  # 30% probabilidad
                    request_response = self.dj_narrator.handle_user_request(
                        original_input,
                        result.target or "artista",
                        "canción solicitada"
                    )
                    print(f"\n{Colors.PURPLE}🎤 DJ Roxy: {request_response}{Colors.END}")
                response = "🎵 ¡Reproduciendo!"
            
            self.stats["comandos_ejecutados"] += 1
        else:
            response = "Ay perdón, tuve problemas con esa rola. ¿Me das otra opción?"
        
        # Guardar en historial
        self.add_to_history(original_input, response, result.command_type, {
            'action': result.action,
            'target': result.target,
            'confidence': result.confidence,
            'dj_mode': True
        })
        
        return response
    
    def detect_music_mood(self, user_input: str) -> str:
        """Detectar mood musical basado en el input del usuario"""
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ['fiesta', 'party', 'bailar', 'perrear']):
            return 'party'
        elif any(word in input_lower for word in ['relajar', 'chill', 'tranquil', 'suave']):
            return 'chill'
        elif any(word in input_lower for word in ['ejercicio', 'gym', 'entrenar', 'workout']):
            return 'workout'
        elif any(word in input_lower for word in ['romántic', 'amor', 'dedicar']):
            return 'romantic'
        else:
            return 'energetic'
    
    def guess_genre_from_query(self, query: str) -> str:
        """Adivinar género musical basado en la consulta"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['reggaeton', 'bad bunny', 'karol g', 'j balvin']):
            return 'reggaeton'
        elif any(word in query_lower for word in ['rock', 'metal', 'guitarra']):
            return 'rock'
        elif any(word in query_lower for word in ['pop', 'ariana', 'taylor']):
            return 'pop'
        elif any(word in query_lower for word in ['electronic', 'edm', 'house', 'techno']):
            return 'electronic'
        else:
            return 'general'
    
    def toggle_dj_mode(self, activate: Optional[bool] = None) -> str:
        """Activar/desactivar modo DJ narrador"""
        if activate is None:
            # Toggle
            self.dj_mode_active = not self.dj_mode_active
        else:
            self.dj_mode_active = activate
        
        if self.dj_mode_active:
            return "🎤 ¡Modo DJ Narrador ACTIVADO! Ahora soy tu DJ personal estilo DJ Levi"
        else:
            if self.dj_narrator.session_active:
                outro = self.dj_narrator.end_session()
                print(f"\n{Colors.PURPLE}🎤 DJ Roxy: {outro}{Colors.END}")
            return "🎤 Modo DJ Narrador desactivado. Volviendo al modo normal"
    
    def dj_session_stats(self) -> str:
        """Obtener estadísticas de la sesión DJ"""
        if self.dj_narrator.session_active:
            return self.dj_narrator.session_stats()
        else:
            return "No hay sesión DJ activa"
    
    def start_auto_dj(self, mood: str = "auto", duration_minutes: int = 0):
        """Iniciar DJ automático"""
        if self.auto_dj_active:
            return "⚠️ DJ automático ya está activo. Usa 'parar dj' para detenerlo primero."
        
        try:
            # Inicializar DJ automático si no existe
            if not self.auto_dj:
                # Usar los mismos componentes del detector unificado
                spotify_controller = getattr(self.unified_detector, 'spotify_controller_unified', None)
                intelligent_selector = getattr(self.unified_detector, 'intelligent_selector', None)
                
                self.auto_dj = AutoDJMode(
                    spotify_controller=spotify_controller,
                    intelligent_selector=intelligent_selector,
                    dj_narrator=self.dj_narrator
                )
                
                # Configurar callbacks
                self.auto_dj.on_track_start = self._on_auto_dj_track_start
                self.auto_dj.on_track_end = self._on_auto_dj_track_end
                self.auto_dj.on_mood_change = self._on_auto_dj_mood_change
                self.auto_dj.on_session_end = self._on_auto_dj_session_end
            
            # Iniciar sesión automática
            success = self.auto_dj.start_auto_session(mood, duration_minutes)
            
            if success:
                self.auto_dj_active = True
                self.dj_mode_active = True  # También activar modo DJ narrador
                
                duration_text = f" por {duration_minutes} minutos" if duration_minutes > 0 else ""
                return f"🤖 ¡DJ automático iniciado! Reproduciendo música {mood}{duration_text}. Digo 'parar dj' para detener."
            else:
                return "❌ No se pudo iniciar el DJ automático"
                
        except Exception as e:
            self.print_status("Auto DJ", "ERROR", str(e))
            return f"❌ Error iniciando DJ automático: {e}"
    
    def stop_auto_dj(self):
        """Detener DJ automático"""
        if not self.auto_dj_active or not self.auto_dj:
            return "⚠️ DJ automático no está activo"
        
        try:
            self.auto_dj.stop_auto_session()
            self.auto_dj_active = False
            self.dj_mode_active = False  # También desactivar modo DJ narrador
            
            return "⏹️ DJ automático detenido. ¡Gracias por escuchar!"
            
        except Exception as e:
            self.print_status("Auto DJ", "ERROR", str(e))
            return f"❌ Error deteniendo DJ automático: {e}"
    
    def start_auto_dj_with_artist(self, artist: str, duration_minutes: int = 0):
        """Iniciar DJ automático con artista específico"""
        if self.auto_dj_active:
            return "⚠️ DJ automático ya está activo. Usa 'parar dj' para detenerlo primero."
        
        try:
            # Inicializar DJ automático si no existe
            if not self.auto_dj:
                spotify_controller = getattr(self.unified_detector, 'spotify_controller_unified', None)
                intelligent_selector = getattr(self.unified_detector, 'intelligent_selector', None)
                
                self.auto_dj = AutoDJMode(
                    spotify_controller=spotify_controller,
                    intelligent_selector=intelligent_selector,
                    dj_narrator=self.dj_narrator
                )
                
                # Configurar callbacks
                self.auto_dj.on_track_start = self._on_auto_dj_track_start
                self.auto_dj.on_track_end = self._on_auto_dj_track_end
                self.auto_dj.on_mood_change = self._on_auto_dj_mood_change
                self.auto_dj.on_session_end = self._on_auto_dj_session_end
            
            # Forzar búsqueda por artista en lugar de mood
            print(f"🧠 Buscando canciones de {artist}")
            
            # Iniciar sesión con artista específico (usar mood como artista)
            success = self.auto_dj.start_auto_session(artist, duration_minutes)
            
            if success:
                self.auto_dj_active = True
                self.dj_mode_active = True
                duration_text = f" por {duration_minutes} minutos" if duration_minutes > 0 else ""
                return f"🤖 ¡DJ automático iniciado! Reproduciendo música de {artist}{duration_text}. Digo 'parar dj' para detener."
            else:
                return f"❌ Error iniciando DJ automático con {artist}"
                
        except Exception as e:
            self.print_status("Auto DJ", "ERROR", str(e))
            return f"❌ Error en DJ automático con {artist}: {str(e)}"
    
    def start_auto_dj_with_genre(self, genre: str, duration_minutes: int = 0):
        """Iniciar DJ automático con género específico"""
        if self.auto_dj_active:
            return "⚠️ DJ automático ya está activo. Usa 'parar dj' para detenerlo primero."
        
        try:
            # Inicializar DJ automático si no existe
            if not self.auto_dj:
                spotify_controller = getattr(self.unified_detector, 'spotify_controller_unified', None)
                intelligent_selector = getattr(self.unified_detector, 'intelligent_selector', None)
                
                self.auto_dj = AutoDJMode(
                    spotify_controller=spotify_controller,
                    intelligent_selector=intelligent_selector,
                    dj_narrator=self.dj_narrator
                )
                
                # Configurar callbacks
                self.auto_dj.on_track_start = self._on_auto_dj_track_start
                self.auto_dj.on_track_end = self._on_auto_dj_track_end
                self.auto_dj.on_mood_change = self._on_auto_dj_mood_change
                self.auto_dj.on_session_end = self._on_auto_dj_session_end
            
            # Forzar búsqueda por género
            print(f"🧠 Buscando música de {genre}")
            
            # Iniciar sesión con género específico
            success = self.auto_dj.start_auto_session(f"genre:{genre}", duration_minutes)
            
            if success:
                self.auto_dj_active = True
                self.dj_mode_active = True
                duration_text = f" por {duration_minutes} minutos" if duration_minutes > 0 else ""
                return f"🤖 ¡DJ automático iniciado! Reproduciendo música {genre}{duration_text}. Digo 'parar dj' para detener."
            else:
                return f"❌ Error iniciando DJ automático con género {genre}"
                
        except Exception as e:
            self.print_status("Auto DJ", "ERROR", str(e))
            return f"❌ Error en DJ automático con género {genre}: {str(e)}"
    
    def get_auto_dj_status(self):
        """Obtener estado del DJ automático"""
        if not self.auto_dj_active or not self.auto_dj:
            return "🔴 DJ automático inactivo"
        
        try:
            status = self.auto_dj.get_session_status()
            
            if status.get('active'):
                mood = status.get('mood', 'desconocido')
                tracks = status.get('tracks_played', 0)
                duration = status.get('duration_minutes', 0)
                
                return f"🟢 DJ automático activo - Mood: {mood} | Canciones: {tracks} | Duración: {duration}min"
            else:
                return "🟡 DJ automático iniciado pero no activo"
                
        except Exception as e:
            return f"❌ Error obteniendo estado: {e}"
    
    def change_auto_dj_mood(self, new_mood: str):
        """Cambiar mood del DJ automático"""
        if not self.auto_dj_active or not self.auto_dj:
            return "⚠️ DJ automático no está activo"
        
        try:
            success = self.auto_dj.set_mood(new_mood)
            if success:
                return f"🎭 Mood cambiado a: {new_mood}"
            else:
                available_moods = list(self.auto_dj.available_moods.keys())
                return f"❌ Mood inválido. Opciones: {', '.join(available_moods)}"
                
        except Exception as e:
            return f"❌ Error cambiando mood: {e}"
    
    def _on_auto_dj_track_start(self, track: dict, reason: str):
        """Callback cuando el DJ automático inicia una canción"""
        # Agregar al historial de música
        self.music_history.add_played_track(track, user_requested=False)
    
    def _on_auto_dj_track_end(self, track: dict):
        """Callback cuando el DJ automático termina una canción"""
        pass
    
    def _on_auto_dj_mood_change(self, old_mood: str, new_mood: str):
        """Callback cuando el DJ automático cambia de mood"""
        pass
    
    def _on_auto_dj_session_end(self, session):
        """Callback cuando termina la sesión del DJ automático"""
        self.auto_dj_active = False
        self.dj_mode_active = False
    
    def refresh_music_data(self) -> str:
        """Actualizar datos musicales del usuario desde Spotify"""
        try:
            if hasattr(self.unified_detector, 'intelligent_selector') and self.unified_detector.intelligent_selector:
                print("🔄 Actualizando datos de Spotify...")
                self.unified_detector.intelligent_selector.refresh_user_data(force=True)
                
                # Obtener estadísticas actualizadas
                stats = self.unified_detector.intelligent_selector.get_selection_stats()
                
                return (f"✅ Datos musicales actualizados!\n"
                       f"   🎤 Artistas favoritos: {stats.get('favorite_artists_count', 0)}\n"
                       f"   🎼 Géneros favoritos: {stats.get('favorite_genres_count', 0)}\n"
                       f"   🎵 Historial reciente: {stats.get('recent_tracks_count', 0)} canciones\n"
                       f"   ⭐ Top tracks: {stats.get('top_tracks_count', 0)} canciones\n"
                       f"   💾 Biblioteca: {stats.get('saved_tracks_count', 0)} canciones")
            else:
                return "❌ Selector inteligente no disponible"
                
        except Exception as e:
            return f"❌ Error actualizando datos: {e}"
    
    def show_stats(self):
        """📊 Mostrar estadísticas del sistema"""
        uptime = time.time() - self.stats["tiempo_inicio"]
        uptime_str = f"{int(uptime//60)}m {int(uptime%60)}s"
        
        print(f"\n{Colors.CYAN}📊 ESTADÍSTICAS DEL SISTEMA UNIFICADO{Colors.END}")
        print(f"⏱️  Tiempo activo: {uptime_str}")
        print(f"💬 Mensajes procesados: {self.stats['mensajes_procesados']}")
        print(f"🎯 Comandos ejecutados: {self.stats['comandos_ejecutados']}")
        print(f"💭 Conversaciones: {self.stats['conversaciones']}")
        print(f"📝 Historial: {len(self.conversation_history)} entradas")
        
        # Estado de TTS
        tts_status = "🔊 ACTIVO" if self.tts_enabled else "🔇 DESACTIVADO"
        tts_api = "✅ Configurada" if self.elevenlabs_api_key else "❌ Sin configurar"
        print(f"🎤 Síntesis de voz: {tts_status} (API: {tts_api})")
        if self.elevenlabs_api_key:
            print(f"🎵 Voz actual: {self.elevenlabs_voice_id}")
        
        # Estado DJ
        dj_status = "🎤 ACTIVO" if self.dj_mode_active else "🎤 INACTIVO"
        print(f"🎧 Modo DJ Narrador: {dj_status}")
        if self.dj_narrator.session_active:
            print(f"🎵 Sesión DJ: {self.dj_narrator.track_count} tracks reproducidos")
        
        # Estado del selector inteligente
        if hasattr(self.unified_detector, 'intelligent_selector') and self.unified_detector.intelligent_selector:
            selector_stats = self.unified_detector.intelligent_selector.get_selection_stats()
            print(f"🧠 Selector Inteligente: ✅ DISPONIBLE")
            print(f"   🎤 Artistas favoritos: {selector_stats.get('favorite_artists_count', 0)}")
            print(f"   🎼 Géneros favoritos: {selector_stats.get('favorite_genres_count', 0)}")
            print(f"   🎵 Datos recientes: {selector_stats.get('recent_tracks_count', 0)} canciones")
        else:
            print(f"🧠 Selector Inteligente: ❌ NO DISPONIBLE")
        
        # APIs disponibles
        grok_status = "✅" if self.grok_api_key else "❌"
        print(f"🤖 Grok API: {grok_status}")
        print(f"📡 Detector unificado: ✅ ACTIVO")
    
    def run(self):
        """🚀 Ejecutar el bot con sistema unificado"""
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎤 ROXY MEGURDY SISTEMA UNIFICADO ACTIVO{Colors.END}")
        print(f"{Colors.CYAN}💬 Habla o escribe (SALIR para terminar){Colors.END}")
        print(f"{Colors.YELLOW}🎯 Sistema unificado: apps + música + contenido + conversación{Colors.END}")
        
        # Estado de TTS
        if self.tts_enabled:
            print(f"{Colors.GREEN}🔊 SÍNTESIS DE VOZ ACTIVADA - Roxy hablará contigo{Colors.END}")
        else:
            print(f"{Colors.YELLOW}🔇 Síntesis de voz desactivada - solo texto{Colors.END}")
        
        print(f"{Colors.BLUE}💡 Comandos especiales: 'stats', 'tts on/off', 'test tts', 'dj mode on/off', 'dj stats', 'refresh music data', 'voice stats', 'recalibrar', 'wake word on/off'{Colors.END}")
        print(f"{Colors.PURPLE}🎤 Modo DJ: Activa con 'dj mode on' para narración estilo DJ Levi{Colors.END}")
        print(f"{Colors.CYAN}🧠 Selección Inteligente: Roxy aprende de tu historial de Spotify para mejores recomendaciones{Colors.END}")
        print("=" * 60)
        
        try:
            # Inicializar sistema híbrido si está disponible
            if self.voice_system and self.voice_system.is_available:
                self.voice_system.start_hybrid_input()
                print(f"{Colors.GREEN}🎤 Sistema híbrido activado: puedes hablar o escribir simultáneamente{Colors.END}")
            
            while self.running:
                if self.voice_system and self.voice_system.is_available:
                    # Usar sistema con palabra clave si está activado, sino híbrido normal
                    if hasattr(self.voice_system.config, 'wake_word_enabled') and self.voice_system.config.wake_word_enabled:
                        input_type, user_input = self.voice_system.get_input_with_wake_word(
                            f"{Colors.BLUE}💬 Di 'Roxy' para activar voz o escribe:{Colors.END}"
                        )
                    else:
                        input_type, user_input = self.voice_system.get_hybrid_input(
                            f"{Colors.BLUE}💬 Habla o escribe tu mensaje:{Colors.END}"
                        )
                    
                    if input_type == "none":
                        continue
                    elif input_type == "voice":
                        self.print_status("Entrada", "VOICE", f"Reconocido por voz: '{user_input}'")
                    elif input_type == "text":
                        self.print_status("Entrada", "TEXT", f"Escrito: '{user_input}'")
                        
                else:
                    # Fallback: solo texto
                    print(f"\n{Colors.BLUE}Escribe tu mensaje:{Colors.END}")
                    user_input = input().strip()
                    if not user_input:
                        continue
                
                if user_input.upper() == "SALIR":
                    break
                
                if user_input.lower() == "stats":
                    self.show_stats()
                    continue
                
                # Comandos especiales para TTS
                if user_input.lower() in ["tts on", "activar voz", "activar tts"]:
                    if self.elevenlabs_api_key:
                        self.tts_enabled = True
                        print(f"{Colors.GREEN}🔊 Síntesis de voz ACTIVADA{Colors.END}")
                    else:
                        print(f"{Colors.RED}❌ No se puede activar TTS - API key no configurada{Colors.END}")
                    continue
                
                if user_input.lower() in ["tts off", "desactivar voz", "desactivar tts"]:
                    self.tts_enabled = False
                    print(f"{Colors.YELLOW}🔇 Síntesis de voz DESACTIVADA{Colors.END}")
                    continue
                
                if user_input.lower() == "test tts":
                    if self.tts_enabled:
                        test_result = self.speak_response("Hola usuario, esta es una prueba de mi voz")
                        if test_result:
                            print(f"{Colors.GREEN}✅ Test de TTS exitoso{Colors.END}")
                        else:
                            print(f"{Colors.RED}❌ Test de TTS falló{Colors.END}")
                    else:
                        print(f"{Colors.YELLOW}🔇 TTS está desactivado{Colors.END}")
                    continue
                
                # Comandos especiales para Modo DJ
                if user_input.lower() in ["dj mode on", "activar dj", "modo dj", "dj on"]:
                    response = self.toggle_dj_mode(True)
                    print(f"{Colors.PURPLE}{response}{Colors.END}")
                    continue
                
                if user_input.lower() in ["dj mode off", "desactivar dj", "dj off"]:
                    response = self.toggle_dj_mode(False)
                    print(f"{Colors.PURPLE}{response}{Colors.END}")
                    continue
                
                if user_input.lower() in ["dj stats", "sesion dj", "estadisticas dj"]:
                    stats = self.dj_session_stats()
                    print(f"{Colors.PURPLE}🎧 {stats}{Colors.END}")
                    continue
                
                # Comando para actualizar datos musicales
                if user_input.lower() in ["refresh music data", "actualizar musica", "refresh spotify", "update music"]:
                    response = self.refresh_music_data()
                    print(f"{Colors.CYAN}{response}{Colors.END}")
                    continue
                
                # Comandos del sistema de voz mejorado
                if user_input.lower() in ["voice stats", "estadisticas voz", "stats voz"]:
                    if self.voice_system:
                        stats = self.voice_system.get_stats()
                        print(f"{Colors.CYAN}📊 Estadísticas del Sistema de Voz:{Colors.END}")
                        print(f"  🎤 Intentos totales: {stats['total_attempts']}")
                        print(f"  ✅ Reconocimientos exitosos: {stats['successful_recognitions']}")
                        print(f"  📈 Tasa de éxito: {stats['success_rate']:.1f}%")
                        print(f"  🔇 Audio vacío filtrado: {stats['empty_audio_filtered']}")
                        print(f"  🔊 Ruido filtrado: {stats['filtered_noise']}")
                        print(f"  ⚡ Umbral actual: {stats['current_threshold']:.0f}")
                        print(f"  📅 Última calibración: {stats['last_calibration']}")
                    else:
                        print(f"{Colors.RED}❌ Sistema de voz no disponible{Colors.END}")
                    continue
                
                if user_input.lower() in ["recalibrar", "recalibrar voz", "calibrar micrófono"]:
                    if self.voice_system:
                        success = self.voice_system.recalibrate()
                        if success:
                            print(f"{Colors.GREEN}✅ Sistema de voz recalibrado correctamente{Colors.END}")
                        else:
                            print(f"{Colors.RED}❌ Error recalibrando sistema de voz{Colors.END}")
                    else:
                        print(f"{Colors.RED}❌ Sistema de voz no disponible{Colors.END}")
                    continue
                
                if user_input.lower() in ["wake word on", "palabra clave on", "activar palabra clave"]:
                    if self.voice_system:
                        self.voice_system.toggle_wake_word(True)
                        print(f"{Colors.GREEN}🎯 Palabra clave activada - di 'Roxy' para activar voz{Colors.END}")
                    else:
                        print(f"{Colors.RED}❌ Sistema de voz no disponible{Colors.END}")
                    continue
                
                if user_input.lower() in ["wake word off", "palabra clave off", "desactivar palabra clave"]:
                    if self.voice_system:
                        self.voice_system.toggle_wake_word(False)
                        print(f"{Colors.YELLOW}🔇 Palabra clave desactivada{Colors.END}")
                    else:
                        print(f"{Colors.RED}❌ Sistema de voz no disponible{Colors.END}")
                    continue
                
                # Procesar entrada
                response = self.process_user_input(user_input)
                
                if response:
                    print(f"\n{Colors.GREEN}🔧 Roxy: {response}{Colors.END}")
                    
                    # Síntesis de voz si está habilitada
                    if self.tts_enabled:
                        tts_success = self.speak_response(response)
                        if not tts_success:
                            self.print_status("TTS", "WARNING", "Error en síntesis - continuando solo texto")
                    else:
                        self.print_status("TTS", "INFO", "Síntesis desactivada - usa 'tts on' para activar")
        
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⌨️  Interrupción detectada{Colors.END}")
        
        finally:
            self.show_stats()
            print(f"\n{Colors.CYAN}👋 ¡Hasta luego usuario!{Colors.END}")

def main():
    """Función principal"""
    try:
        # Verificar dependencias
        required_files = ["unified_command_detector.py", "personality_config.py"]
        for file in required_files:
            if not os.path.exists(file):
                print(f"❌ Archivo requerido no encontrado: {file}")
                return False
        
        # Inicializar y ejecutar bot
        roxy = RoxyBotUnified()
        roxy.run()
        
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
