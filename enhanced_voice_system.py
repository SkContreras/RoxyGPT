"""
Sistema de Reconocimiento de Voz Mejorado - Roxy Megurdy
======================================================
Soluciona problemas de:
- Audio vacío o ruido innecesario
- Detección de fin de habla
- Sistema híbrido voz/texto
- Confirmación por voz de comandos
"""

import speech_recognition as sr
import numpy as np
import threading
import time
import queue
import re
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

@dataclass
class AudioConfig:
    """Configuración de audio optimizada"""
    # Umbrales de energía
    energy_threshold: float = 4000  # Más alto para filtrar ruido
    dynamic_energy_threshold: bool = True
    dynamic_energy_adjustment_damping: float = 0.15
    dynamic_energy_ratio: float = 1.5
    
    # Timeouts y límites
    timeout: float = 3.0  # Tiempo máximo esperando audio
    phrase_time_limit: float = 10.0  # Tiempo máximo de frase
    pause_threshold: float = 0.8  # Pausa para considerar fin de habla
    
    # Filtros de audio
    min_audio_length: float = 0.5  # Mínimo 0.5 segundos de audio
    noise_filter_enabled: bool = True
    
    # Confirmación de comandos
    require_confirmation: list = field(default_factory=lambda: ["eliminar", "borrar", "cerrar aplicación", "apagar"])
    confirmation_timeout: float = 5.0
    
    # Activación por palabra clave
    wake_word_enabled: bool = False
    wake_words: list = field(default_factory=lambda: ["roxy", "hey roxy", "oye roxy", "hola roxy"])
    wake_word_timeout: float = 30.0  # Tiempo escuchando palabra clave

@dataclass
class VoiceResult:
    """Resultado del reconocimiento de voz"""
    text: Optional[str]
    confidence: float
    audio_length: float
    energy_level: float
    is_valid: bool
    error_message: Optional[str] = None
    requires_confirmation: bool = False

class EnhancedVoiceSystem:
    """Sistema de reconocimiento de voz mejorado"""
    
    def __init__(self, config: AudioConfig = None):
        self.config = config or AudioConfig()
        self.recognizer = None
        self.microphone = None
        self.is_available = False
        self.background_listener = None
        self.listening_active = False
        
        # Cola para entrada híbrida
        self.input_queue = queue.Queue()
        self.text_input_thread = None
        
        # Estadísticas
        self.stats = {
            "total_attempts": 0,
            "successful_recognitions": 0,
            "filtered_noise": 0,
            "empty_audio_filtered": 0,
            "last_calibration": None
        }
        
        self.initialize_voice_system()
    
    def initialize_voice_system(self):
        """Inicializar el sistema de reconocimiento de voz"""
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Configurar reconocedor con parámetros optimizados
            self.recognizer.energy_threshold = self.config.energy_threshold
            self.recognizer.dynamic_energy_threshold = self.config.dynamic_energy_threshold
            self.recognizer.dynamic_energy_adjustment_damping = self.config.dynamic_energy_adjustment_damping
            self.recognizer.dynamic_energy_ratio = self.config.dynamic_energy_ratio
            self.recognizer.pause_threshold = self.config.pause_threshold
            
            self.calibrate_microphone()
            self.is_available = True
            print("🎤 Sistema de voz mejorado inicializado correctamente")
            
        except Exception as e:
            print(f"⚠️ Error inicializando sistema de voz: {e}")
            self.is_available = False
    
    def calibrate_microphone(self):
        """Calibrar micrófono con detección inteligente de ruido ambiente"""
        if not self.microphone or not self.recognizer:
            return False
            
        try:
            print("🔧 Calibrando micrófono... (mantente en silencio)")
            
            with self.microphone as source:
                # Calibración más larga para mejor detección de ruido
                self.recognizer.adjust_for_ambient_noise(source, duration=2.0)
                
            # Ajustar umbral basado en ruido ambiente
            ambient_noise = self.recognizer.energy_threshold
            
            # Establecer umbral dinámico basado en ruido ambiente
            if ambient_noise < 1000:
                # Ambiente muy silencioso
                self.recognizer.energy_threshold = max(ambient_noise * 3, 2000)
            elif ambient_noise < 3000:
                # Ambiente normal
                self.recognizer.energy_threshold = ambient_noise * 2
            else:
                # Ambiente ruidoso
                self.recognizer.energy_threshold = ambient_noise * 1.5
            
            self.stats["last_calibration"] = datetime.now()
            print(f"✅ Micrófono calibrado - Umbral: {self.recognizer.energy_threshold:.0f}")
            return True
            
        except Exception as e:
            print(f"❌ Error calibrando micrófono: {e}")
            return False
    
    def is_audio_valid(self, audio_data, duration: float) -> Tuple[bool, float, str]:
        """
        Validar si el audio contiene habla válida
        Returns: (is_valid, energy_level, reason)
        """
        try:
            # Convertir audio a numpy array para análisis
            audio_array = np.frombuffer(audio_data.get_raw_data(), dtype=np.int16)
            
            # Calcular métricas de audio
            energy_level = np.sqrt(np.mean(audio_array.astype(np.float32)**2))
            max_amplitude = np.max(np.abs(audio_array))
            
            # Filtro 1: Duración mínima
            if duration < self.config.min_audio_length:
                return False, energy_level, f"Audio muy corto ({duration:.2f}s < {self.config.min_audio_length}s)"
            
            # Filtro 2: Energía mínima (detectar silencio)
            min_energy = self.recognizer.energy_threshold * 0.3
            if energy_level < min_energy:
                return False, energy_level, f"Energía muy baja ({energy_level:.0f} < {min_energy:.0f})"
            
            # Filtro 3: Amplitud mínima
            if max_amplitude < 1000:
                return False, energy_level, "Amplitud muy baja (posible ruido)"
            
            # Filtro 4: Detectar ruido constante vs habla
            # La habla tiene variaciones, el ruido es más constante
            audio_std = np.std(audio_array.astype(np.float32))
            if audio_std < energy_level * 0.1:
                return False, energy_level, "Patrón de ruido constante detectado"
            
            return True, energy_level, "Audio válido"
            
        except Exception as e:
            return False, 0.0, f"Error analizando audio: {e}"
    
    def recognize_speech_enhanced(self, show_status: bool = True) -> VoiceResult:
        """Reconocimiento de voz mejorado con filtros inteligentes"""
        if not self.is_available:
            return VoiceResult(
                text=None, confidence=0.0, audio_length=0.0, 
                energy_level=0.0, is_valid=False, 
                error_message="Sistema de voz no disponible"
            )
        
        self.stats["total_attempts"] += 1
        
        try:
            if show_status:
                print("🎤 Escuchando... (habla claramente)")
            
            start_time = time.time()
            
            with self.microphone as source:
                # Escuchar con timeouts optimizados
                audio = self.recognizer.listen(
                    source, 
                    timeout=self.config.timeout,
                    phrase_time_limit=self.config.phrase_time_limit
                )
            
            audio_length = time.time() - start_time
            
            # Validar audio antes de procesar
            is_valid, energy_level, reason = self.is_audio_valid(audio, audio_length)
            
            if not is_valid:
                if show_status:
                    print(f"🔇 Audio filtrado: {reason}")
                
                if "muy corto" in reason or "muy baja" in reason:
                    self.stats["empty_audio_filtered"] += 1
                else:
                    self.stats["filtered_noise"] += 1
                
                return VoiceResult(
                    text=None, confidence=0.0, audio_length=audio_length,
                    energy_level=energy_level, is_valid=False, error_message=reason
                )
            
            # Procesar audio válido
            if show_status:
                print("🔄 Procesando audio válido...")
            
            try:
                # Reconocimiento con Google (más preciso)
                text = self.recognizer.recognize_google(audio, language="es-ES")
                
                # Calcular confianza basada en métricas
                confidence = self._calculate_confidence(text, energy_level, audio_length)
                
                # Verificar si requiere confirmación
                requires_confirmation = self._requires_confirmation(text)
                
                self.stats["successful_recognitions"] += 1
                
                if show_status:
                    print(f"✅ Reconocido: '{text}' (confianza: {confidence:.2f})")
                
                return VoiceResult(
                    text=text, confidence=confidence, audio_length=audio_length,
                    energy_level=energy_level, is_valid=True,
                    requires_confirmation=requires_confirmation
                )
                
            except sr.UnknownValueError:
                return VoiceResult(
                    text=None, confidence=0.0, audio_length=audio_length,
                    energy_level=energy_level, is_valid=False,
                    error_message="No se pudo entender el audio"
                )
            except sr.RequestError as e:
                return VoiceResult(
                    text=None, confidence=0.0, audio_length=audio_length,
                    energy_level=energy_level, is_valid=False,
                    error_message=f"Error del servicio de reconocimiento: {e}"
                )
                
        except sr.WaitTimeoutError:
            if show_status:
                print("⏰ Timeout - no se detectó voz")
            return VoiceResult(
                text=None, confidence=0.0, audio_length=0.0,
                energy_level=0.0, is_valid=False,
                error_message="Timeout - no se detectó voz"
            )
        except Exception as e:
            return VoiceResult(
                text=None, confidence=0.0, audio_length=0.0,
                energy_level=0.0, is_valid=False,
                error_message=f"Error inesperado: {e}"
            )
    
    def _calculate_confidence(self, text: str, energy_level: float, duration: float) -> float:
        """Calcular confianza basada en múltiples factores"""
        confidence = 0.5  # Base
        
        # Factor 1: Longitud del texto (más palabras = más confianza)
        words = len(text.split())
        if words >= 3:
            confidence += 0.2
        elif words >= 2:
            confidence += 0.1
        
        # Factor 2: Energía de audio
        if energy_level > self.recognizer.energy_threshold * 2:
            confidence += 0.15
        elif energy_level > self.recognizer.energy_threshold * 1.5:
            confidence += 0.1
        
        # Factor 3: Duración apropiada
        if 1.0 <= duration <= 8.0:
            confidence += 0.15
        elif 0.5 <= duration <= 12.0:
            confidence += 0.05
        
        return min(confidence, 1.0)
    
    def _requires_confirmation(self, text: str) -> bool:
        """Verificar si el comando requiere confirmación"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.config.require_confirmation)
    
    def confirm_command(self, command: str) -> bool:
        """Solicitar confirmación por voz para comandos importantes"""
        print(f"⚠️ Comando detectado: '{command}'")
        print("🎤 Di 'sí' o 'confirmar' para ejecutar, 'no' o 'cancelar' para cancelar:")
        
        start_time = time.time()
        while time.time() - start_time < self.config.confirmation_timeout:
            result = self.recognize_speech_enhanced(show_status=False)
            
            if result.is_valid and result.text:
                text_lower = result.text.lower()
                if any(word in text_lower for word in ["sí", "si", "confirmar", "confirmo", "ok", "vale"]):
                    print("✅ Comando confirmado")
                    return True
                elif any(word in text_lower for word in ["no", "cancelar", "cancelo", "para"]):
                    print("❌ Comando cancelado")
                    return False
        
        print("⏰ Timeout en confirmación - comando cancelado")
        return False
    
    def start_hybrid_input(self):
        """Iniciar sistema híbrido de entrada (voz + texto)"""
        self.text_input_thread = threading.Thread(target=self._text_input_worker, daemon=True)
        self.text_input_thread.start()
    
    def _text_input_worker(self):
        """Worker thread para entrada de texto"""
        while True:
            try:
                text = input()
                if text.strip():
                    self.input_queue.put(("text", text.strip()))
            except (EOFError, KeyboardInterrupt):
                break
    
    def get_hybrid_input(self, prompt: str = "Habla o escribe tu mensaje:") -> Tuple[str, str]:
        """
        Obtener entrada híbrida (voz o texto)
        Returns: (input_type, content) donde input_type es 'voice' o 'text'
        """
        print(f"💬 {prompt}")
        print("   - Presiona ENTER para activar voz")
        print("   - O escribe directamente tu mensaje")
        
        # Verificar si hay entrada de texto pendiente
        try:
            input_type, content = self.input_queue.get_nowait()
            return input_type, content
        except queue.Empty:
            pass
        
        # Esperar entrada de texto
        text_input = input().strip()
        
        if text_input:
            return "text", text_input
        else:
            # Activar reconocimiento de voz
            result = self.recognize_speech_enhanced()
            if result.is_valid and result.text:
                return "voice", result.text
            else:
                return "none", ""
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema"""
        success_rate = 0
        if self.stats["total_attempts"] > 0:
            success_rate = (self.stats["successful_recognitions"] / self.stats["total_attempts"]) * 100
        
        return {
            **self.stats,
            "success_rate": success_rate,
            "is_available": self.is_available,
            "current_threshold": self.recognizer.energy_threshold if self.recognizer else 0
        }
    
    def listen_for_wake_word(self) -> bool:
        """Escuchar palabra clave de activación"""
        if not self.is_available or not self.config.wake_word_enabled:
            return False
            
        print(f"👂 Escuchando palabra clave... (di una de: {', '.join(self.config.wake_words)})")
        
        start_time = time.time()
        while time.time() - start_time < self.config.wake_word_timeout:
            try:
                # Escuchar con timeout corto para palabras clave
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=1.0, phrase_time_limit=3.0)
                
                # Reconocer con menor precisión para palabras clave
                try:
                    text = self.recognizer.recognize_google(audio, language="es-ES").lower()
                    
                    # Verificar si contiene palabra clave
                    for wake_word in self.config.wake_words:
                        if wake_word.lower() in text:
                            print(f"🎯 Palabra clave detectada: '{wake_word}' en '{text}'")
                            return True
                            
                except (sr.UnknownValueError, sr.RequestError):
                    # Ignorar errores de reconocimiento para palabras clave
                    pass
                    
            except sr.WaitTimeoutError:
                # Continuar escuchando
                continue
            except Exception:
                # Ignorar otros errores
                continue
        
        print("⏰ Timeout escuchando palabra clave")
        return False
    
    def get_input_with_wake_word(self, prompt: str = "Habla o escribe:") -> Tuple[str, str]:
        """
        Obtener entrada con opción de palabra clave
        Returns: (input_type, content)
        """
        if self.config.wake_word_enabled:
            print(f"💬 {prompt}")
            print("   - Di una palabra clave para activar voz")
            print("   - O escribe directamente tu mensaje")
            
            # Verificar entrada de texto inmediata
            try:
                input_type, content = self.input_queue.get_nowait()
                return input_type, content
            except queue.Empty:
                pass
            
            # Escuchar palabra clave
            if self.listen_for_wake_word():
                print("🎤 Palabra clave detectada - ahora habla tu comando:")
                result = self.recognize_speech_enhanced()
                if result.is_valid and result.text:
                    return "voice", result.text
            
            # Si no hay palabra clave, verificar entrada de texto
            print("✍️ No se detectó palabra clave - escribe tu mensaje:")
            text_input = input().strip()
            if text_input:
                return "text", text_input
            else:
                return "none", ""
        else:
            # Sin palabra clave, usar método híbrido normal
            return self.get_hybrid_input(prompt)
    
    def toggle_wake_word(self, enabled: bool = None) -> bool:
        """Activar/desactivar palabra clave"""
        if enabled is None:
            self.config.wake_word_enabled = not self.config.wake_word_enabled
        else:
            self.config.wake_word_enabled = enabled
        
        status = "activada" if self.config.wake_word_enabled else "desactivada"
        print(f"🎯 Palabra clave {status}")
        
        if self.config.wake_word_enabled:
            print(f"   Palabras clave: {', '.join(self.config.wake_words)}")
        
        return self.config.wake_word_enabled
    
    def recalibrate(self):
        """Recalibrar el sistema si hay problemas"""
        print("🔧 Recalibrando sistema de voz...")
        success = self.calibrate_microphone()
        if success:
            print("✅ Recalibración exitosa")
        else:
            print("❌ Error en recalibración")
        return success

def demo_enhanced_voice():
    """Demo del sistema de voz mejorado"""
    print("🎤 Demo del Sistema de Voz Mejorado")
    print("=" * 40)
    
    voice_system = EnhancedVoiceSystem()
    
    if not voice_system.is_available:
        print("❌ Sistema de voz no disponible")
        return
    
    print("\n🔧 Probando reconocimiento básico...")
    result = voice_system.recognize_speech_enhanced()
    print(f"Resultado: {result}")
    
    print("\n🔧 Probando entrada híbrida...")
    input_type, content = voice_system.get_hybrid_input()
    print(f"Entrada {input_type}: {content}")
    
    print("\n📊 Estadísticas:")
    stats = voice_system.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    demo_enhanced_voice()
