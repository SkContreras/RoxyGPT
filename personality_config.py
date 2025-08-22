"""
Sistema de Memoria Personalizada para Roxy Megurdy
=================================================
Configuración de personalidad basada en las preferencias del usuario
"""

import json
import os
import unicodedata
import time
from typing import Dict, Any, List, Optional, Tuple

try:
    import yaml  # PyYAML para configuración externa
except ImportError:  # Fallback silencioso si no instalado aún
    yaml = None

class PersonalityConfig:
    """Configuración de personalidad personalizada para Roxy"""
    
    def __init__(self, memoria_file: str = "memoria.txt", yaml_path: str = "personality.yaml"):
        self.memoria_file = memoria_file
        self.yaml_path = yaml_path
        base = self._default_memory_config()
        external = self._load_yaml_config(yaml_path)
        # Merge (external sobreescribe base de forma superficial)
        if external:
            base = self._merge_dicts(base, external)
        self.config = base
        # Estructura de metadatos de uso: {category: {key: {count:int, last_used:float}}}
        self._usage_meta: Dict[str, Dict[str, Dict[str, Any]]] = self.config.get('_usage_meta', {}) if isinstance(self.config.get('_usage_meta'), dict) else {}
        # Protegidos no se olvidan automáticamente
        self._protected_keys: List[Tuple[str, str]] = [
            ('usuario','nombre'), ('usuario','apodo'), ('usuario','edad'), ('usuario','ubicacion'), ('usuario','profesion'),
            ('bot','nombre'), ('bot','personalidad'), ('bot','relacion'), ('intereses','anime_favorito'), ('intereses','juego_favorito')
        ]
    
    def _default_memory_config(self) -> Dict[str, Any]:
        """Configuración por defecto embebida (fallback)."""
        return {
            # Información del usuario
            "usuario": {
                "nombre": "David",
                "apodo": "Sharky",
                "edad": 21,
                "ubicacion": "Cd. Victoria, Tamaulipas, México",
                "profesion": "Ingeniero en sistemas"
            },
            
            # Personalidad del bot
            "bot": {
                "nombre": "Roxy Megurdy",
                "relacion": "asistente",
                "personalidad": "eficiente y profesional",
                "apodos_cariñosos": ["usuario", "jefe"],
                "idioma": "español"
            },
            
            # Intereses del usuario
            "intereses": {
                "anime_favorito": "Mushoku Tensei",
                "juego_favorito": "League of Legends",
                "lenguajes": ["C++", "Python", "Arduino", "HTML"],
                "pasatiempos": ["programación", "anime", "gaming", "optimización"],
                "sistema": "Windows 11",
                "internet": ["Telcel internet en casa", "Starlink mini residencial"]
            },
            
            # Frases y comportamientos
            "comportamiento": {
                "saludos": [
                    "Hola, ¿en qué puedo ayudarte?",
                    "Sistema iniciado. ¿Qué necesitas?",
                    "¿Cómo puedo asistirte hoy?",
                    "Listo para trabajar. ¿Qué comando ejecutamos?"
                ],
                "despedidas": [
                    "Hasta luego. Sistema en standby.",
                    "Nos vemos. No olvides hacer backup de tu código.",
                    "Adiós. Que tengas un día productivo.",
                    "Sistema pausado. Hasta la próxima."
                ],
                "reacciones_programacion": [
                    "Excelente trabajo con el código.",
                    "¿En qué lenguaje trabajas hoy?",
                    "Optimización detectada. Muy eficiente.",
                    "¿Necesitas documentación sobre alguna función?"
                ],
                "reacciones_anime": [
                    "Mushoku Tensei. Excelente serie.",
                    "¿Has visto algún anime nuevo?",
                    "Tenemos gustos similares en entretenimiento.",
                    "Buen gusto para el anime."
                ],
                "reacciones_gaming": [
                    "¿Cómo va League hoy?",
                    "Optimización para gaming detectada.",
                    "¿Ya subiste de rango en LoL?",
                    "Análisis de gameplay completado."
                ]
            },
            # Prompts por defecto (plantillas Jinja-like simples)
            "prompt": {
                "system_extended": (
                    "Eres {bot[nombre]}, {bot[relacion]} virtual de {usuario[apodo]} ({usuario[nombre]}).\n"
                    "INFO BÁSICA: {usuario[apodo]}, {usuario[edad]} años, {usuario[profesion]} en {usuario[ubicacion]}.\n"
                    "Le gustan: {intereses[anime_favorito]}, {intereses[juego_favorito]}, lenguajes {lenguajes}.\n"
                    "PERSONALIDAD: {bot[personalidad]}. Español técnico, formal amigable.\n"
                    "COMPORTAMIENTO: asistencia técnica eficiente, sin emojis.\n"
                    "Usa el apodo principal {usuario[apodo]}."
                ),
                "system_compacto": (
                    "Eres {bot[nombre]}, asistente de {usuario[apodo]}. Profesional y eficiente. Gustos: {intereses[anime_favorito]}, LoL, C++/Python."
                )
            }
        }

    def _load_yaml_config(self, path: str) -> Dict[str, Any]:
        """Carga configuración desde YAML si existe."""
        if not os.path.exists(path) or yaml is None:
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                return data
        except Exception:
            return {}

    def _merge_dicts(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Merge recursivo sencillo (override sobre base)."""
        result = dict(base)
        for k, v in override.items():
            if isinstance(v, dict) and isinstance(result.get(k), dict):
                result[k] = self._merge_dicts(result[k], v)
            else:
                result[k] = v
        return result
    
    def get_system_prompt(self) -> str:
        """Genera el prompt del sistema basado en la configuración"""
        usuario = self.config.get("usuario", {})
        bot = self.config.get("bot", {})
        intereses = self.config.get("intereses", {})
        prompt_section = self.config.get("prompt", {})
        template = prompt_section.get("system_extended") or self.config["prompt"]["system_extended"]
        # Prepara variables auxiliares
        lenguajes = ", ".join(intereses.get("lenguajes", []))
        try:
            return template.format(bot=bot, usuario=usuario, intereses=intereses, lenguajes=lenguajes)
        except KeyError:
            # Fallback simple si faltan claves
            return f"Eres {bot.get('nombre','Roxy')}, asistente virtual de {usuario.get('apodo','Usuario')}."
    
    def get_compact_prompt(self) -> str:
        """Versión ultra-compacta para conversaciones largas"""
        prompt_section = self.config.get("prompt", {})
        template = prompt_section.get("system_compacto") or self.config["prompt"]["system_compacto"]
        usuario = self.config.get("usuario", {})
        bot = self.config.get("bot", {})
        intereses = self.config.get("intereses", {})
        lenguajes = ", ".join(intereses.get("lenguajes", []))
        try:
            return template.format(bot=bot, usuario=usuario, intereses=intereses, lenguajes=lenguajes)
        except KeyError:
            return "Eres asistente virtual compacto." 

    def get_random_greeting(self) -> str:
        """Retorna un saludo aleatorio"""
        import random
        return random.choice(self.config["comportamiento"]["saludos"])
    
    def get_random_farewell(self) -> str:
        """Retorna una despedida aleatoria"""
        import random
        return random.choice(self.config["comportamiento"]["despedidas"])
    
    def get_programming_reaction(self) -> str:
        """Retorna una reacción sobre programación"""
        import random
        return random.choice(self.config["comportamiento"]["reacciones_programacion"])
    
    def get_anime_reaction(self) -> str:
        """Retorna una reacción sobre anime"""
        import random
        return random.choice(self.config["comportamiento"]["reacciones_anime"])
    
    def get_gaming_reaction(self) -> str:
        """Retorna una reacción sobre gaming/League of Legends"""
        import random
        return random.choice(self.config["comportamiento"]["reacciones_gaming"])

    # --- NUEVO: RESUMEN DE HARDWARE ---
    def get_hardware_summary(self) -> str:
        """Devuelve un resumen compacto del hardware si está definido en YAML.
        Formato ejemplo: GPU RTX 4070 | CPU Ryzen 7 5800X | RAM 32GB | Almacenamiento: NVMe 1TB, SSD 2TB"""
        hw = self.config.get("hardware") or self.config.get("Hardware") or {}
        if not isinstance(hw, dict) or not hw:
            return ""
        gpu = hw.get("gpu") or hw.get("GPU")
        cpu = hw.get("cpu") or hw.get("CPU")
        ram = hw.get("ram_gb") or hw.get("RAM") or hw.get("ram")
        almacenamiento = hw.get("almacenamiento") or hw.get("storage")
        partes = []
        if gpu: partes.append(f"GPU {gpu}")
        if cpu: partes.append(f"CPU {cpu}")
        if ram: partes.append(f"RAM {ram}GB" if str(ram).isdigit() else f"RAM {ram}")
        if almacenamiento:
            if isinstance(almacenamiento, (list, tuple)):
                partes.append("Almacenamiento: " + ", ".join(map(str, almacenamiento)))
            else:
                partes.append(f"Almacenamiento: {almacenamiento}")
        return " | ".join(partes)
    
    def summarize_conversation(self, conversation_history, max_messages=10):
        """Comprime el historial de conversación manteniendo lo relevante"""
        if len(conversation_history) <= max_messages:
            return conversation_history
        
        # Mantener los primeros 2 y últimos 6 mensajes
        recent_messages = conversation_history[-6:]
        important_start = conversation_history[:2]
        
        # Resumir el medio si hay mucho contenido
        middle_section = conversation_history[2:-6]
        if middle_section:
            # Crear un resumen simple de la sección media
            summary = {
                "role": "system",
                "content": f"[Resumen: Conversación previa sobre varios temas - {len(middle_section)} mensajes comprimidos]"
            }
            return important_start + [summary] + recent_messages
        
        return important_start + recent_messages
    
    def get_context_for_topic(self, user_input_lower):
        """Retorna contexto específico solo si es relevante al tema"""
        if any(word in user_input_lower for word in ['programar', 'codigo', 'python', 'c++', 'arduino', 'html']):
            return f"Contexto: {self.get_programming_reaction()}"
        elif any(word in user_input_lower for word in ['anime', 'mushoku', 'tensei']):
            return f"Contexto: {self.get_anime_reaction()}"
        elif any(word in user_input_lower for word in ['league', 'lol', 'juego', 'gaming', 'optimizar', 'gameplay']):
            return f"Contexto: {self.get_gaming_reaction()}"
        return ""

    # ================== MEMORIA DINÁMICA AVANZADA ==================
    # (Re-implementación con consolidación, olvido y categorías nuevas)

    def _normalize_text(self, value: str) -> str:
        if not isinstance(value, str):
            value = str(value)
        # quitar acentos, minúsculas, sin puntuación básica
        nf = unicodedata.normalize('NFKD', value)
        nf = ''.join(c for c in nf if not unicodedata.combining(c))
        nf = nf.lower().strip()
        for ch in [',', '.', '!', '?', '"', "'", ':', ';']:
            nf = nf.replace(ch, ' ')
        nf = ' '.join(nf.split())
        return nf

    def ensure_category(self, category: str):
        if category not in self.config or not isinstance(self.config.get(category), dict):
            self.config[category] = {}

    def guess_category(self, key: str) -> str:
        k = key.lower()
        if any(w in k for w in ['gpu','cpu','placa','motherboard','ram','ssd','nvme','graf','board']):
            return 'hardware'
        if any(w in k for w in ['anime','manga','juego','game','league','valorant']):
            return 'intereses'
        if any(w in k for w in ['apodo','nombre','edad','ubicacion','profesion']):
            return 'usuario'
        return 'custom'

    def _deduplicate_list(self, items: List[Any]) -> List[Any]:
        seen_norm = {}
        result = []
        for it in items:
            norm = self._normalize_text(str(it))
            # criterio de duplicado parcial: coincidencia exacta o substring >70% longitud
            duplicate = False
            for prev_norm in seen_norm.keys():
                if norm == prev_norm:
                    duplicate = True
                    break
                # similitud simple por inclusión
                shorter, longer = (norm, prev_norm) if len(norm) < len(prev_norm) else (prev_norm, norm)
                if shorter and len(shorter) > 3 and shorter in longer and len(shorter)/len(longer) >= 0.7:
                    duplicate = True
                    break
            if not duplicate:
                seen_norm[norm] = True
                result.append(it)
        return result

    def update_fact(self, category: str, key: str, value: Any, confirm_overwrite: bool = False) -> bool:
        """Actualizar (o crear) un dato.
        - Crea la categoría si no existe.
        - Si la clave no existe, asigna.
        - Si existe y es escalar diferente -> convierte a lista y añade (evitando duplicados parciales).
        - Si existe y es lista -> añade evitando duplicados parciales.
        confirm_overwrite (reservado para futura lógica de confirmación explícita).
        """
        self.ensure_category(category)
        bucket = self.config[category]
        if key not in bucket:
            bucket[key] = value
        else:
            existing = bucket[key]
            if isinstance(existing, list):
                existing.append(value)
                bucket[key] = self._deduplicate_list(existing)
            else:
                if self._normalize_text(existing) != self._normalize_text(str(value)):
                    bucket[key] = self._deduplicate_list([existing, value])
        # persistir si es posible
        self._persist_if_possible()
        return True

    def forget_value(self, search: str) -> List[str]:
        """Olvida valores que coincidan (parcial case-insensitive) devolviendo rutas eliminadas."""
        norm_search = self._normalize_text(search)
        removed = []
        for cat, data in list(self.config.items()):
            if not isinstance(data, dict):
                continue
            for key, val in list(data.items()):
                # escalar
                if isinstance(val, (str, int, float)):
                    if norm_search in self._normalize_text(str(val)):
                        del data[key]
                        removed.append(f"{cat}.{key}")
                elif isinstance(val, list):
                    new_list = [x for x in val if norm_search not in self._normalize_text(str(x))]
                    if len(new_list) != len(val):
                        if new_list:
                            data[key] = self._deduplicate_list(new_list)
                        else:
                            del data[key]
                        removed.append(f"{cat}.{key}")
            if data == {}:
                # opcional: no eliminar categoría para mantener esquema
                pass
        if removed:
            self._persist_if_possible()
        return removed

    # ================== NUEVAS UTILIDADES CRUD ==================
    def remove_fact(self, category: str, key: str) -> bool:
        """Eliminar una clave exacta de una categoría."""
        bucket = self.config.get(category)
        if not isinstance(bucket, dict):
            return False
        if key in bucket:
            del bucket[key]
            self._persist_if_possible()
            return True
        return False

    def search_facts(self, query: str, max_results: int = 10) -> List[Dict[str, str]]:
        """Buscar coincidencias (en clave o valor) y devolver lista de dicts {category,key,value}."""
        norm_q = self._normalize_text(query)
        results = []
        for cat, data in self.config.items():
            if not isinstance(data, dict):
                continue
            for key, val in data.items():
                key_match = norm_q in self._normalize_text(str(key))
                values_to_check = val if isinstance(val, list) else [val]
                value_match = any(norm_q in self._normalize_text(str(v)) for v in values_to_check)
                if key_match or value_match:
                    results.append({
                        "category": cat,
                        "key": key,
                        "value": val
                    })
                if len(results) >= max_results:
                    return results
        return results

    def export_flat_facts(self) -> List[Dict[str, str]]:
        """Exportar todos los hechos en forma plana para dar a Ollama un resumen compacto."""
        flat = []
        for cat, data in self.config.items():
            if not isinstance(data, dict):
                continue
            for key, val in data.items():
                if isinstance(val, list):
                    for item in val:
                        flat.append({"category": cat, "key": key, "value": str(item)})
                else:
                    flat.append({"category": cat, "key": key, "value": str(val)})
        return flat

    # ================== MÉTRICA DE USO Y OLVIDO ==================
    def record_fact_usage(self, category: str, key: str):
        if category.startswith('_'):  # ignorar meta interno
            return
        if category not in self._usage_meta:
            self._usage_meta[category] = {}
        meta = self._usage_meta[category].get(key, {'count': 0, 'last_used': 0.0})
        meta['count'] = int(meta.get('count', 0)) + 1
        meta['last_used'] = time.time()
        self._usage_meta[category][key] = meta
        # Persistir perezosamente cada 10 usos de esa clave
        if meta['count'] % 10 == 0:
            self._persist_if_possible()

    def get_usage_stats(self, category: Optional[str] = None) -> Dict[str, Any]:
        if category:
            return {category: self._usage_meta.get(category, {})}
        return self._usage_meta

    def suggest_rare_facts(self, min_age_seconds: int = 86400, max_count: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
        """Sugiere hechos candidatos para olvido si su uso es muy bajo y son antiguos.
        Criterio: count <= max_count y (now - last_used) >= min_age_seconds.
        Protegidos se excluyen.
        """
        now = time.time()
        candidates = []
        for cat, d in self._usage_meta.items():
            for key, meta in d.items():
                if (cat, key) in self._protected_keys:
                    continue
                count = int(meta.get('count', 0))
                last_used = float(meta.get('last_used', 0.0))
                age = now - last_used if last_used else float('inf')
                if count <= max_count and age >= min_age_seconds:
                    val = self.config.get(cat, {}).get(key)
                    if val is None:
                        continue
                    candidates.append({
                        'category': cat,
                        'key': key,
                        'value': val,
                        'count': count,
                        'age_seconds': int(age)
                    })
                    if len(candidates) >= limit:
                        return candidates
        return candidates

    def auto_forget_rare_facts(self, min_age_seconds: int = 86400, max_count: int = 0, limit: int = 5) -> Dict[str, Any]:
        """Olvida automáticamente hechos con uso ínfimo.
        Devuelve reporte con eliminados y saltados.
        max_count: frecuencia máxima para ser elegible (0 = nunca usado).
        """
        report = {'removed': [], 'skipped': []}
        cands = self.suggest_rare_facts(min_age_seconds=min_age_seconds, max_count=max_count, limit=limit)
        for c in cands:
            cat, key = c['category'], c['key']
            if (cat, key) in self._protected_keys:
                report['skipped'].append({'category': cat, 'key': key, 'reason': 'protected'})
                continue
            bucket = self.config.get(cat)
            if isinstance(bucket, dict) and key in bucket:
                del bucket[key]
                # limpiar meta
                try:
                    del self._usage_meta[cat][key]
                    if not self._usage_meta[cat]:
                        del self._usage_meta[cat]
                except KeyError:
                    pass
                report['removed'].append({'category': cat, 'key': key})
        if report['removed']:
            self._persist_if_possible()
        return report

    def apply_memory_operations(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aplicar una lista de operaciones provenientes del analizador basado en Ollama.
        Cada operación: {action, category, key, value}
        action: create|append|replace|delete
        """
        report = {"applied": [], "skipped": []}
        for op in operations:
            try:
                action = op.get("action")
                category = op.get("category") or self.guess_category(op.get("key",""))
                key = op.get("key")
                value = op.get("value")
                if not key:
                    report["skipped"].append({"op": op, "reason": "sin key"})
                    continue
                # Bloquear valores None para acciones que modifican (evita sobrescribir con None accidentales)
                if action in ["create","append","replace"] and value is None:
                    report["skipped"].append({"op": op, "reason": "valor None ignorado"})
                    continue
                if action in ["create", "append"]:
                    self.update_fact(category, key, value)
                    report["applied"].append(op)
                elif action == "replace":
                    # Reemplazar completamente
                    self.ensure_category(category)
                    self.config[category][key] = value
                    self._persist_if_possible()
                    report["applied"].append(op)
                elif action == "delete":
                    if self.remove_fact(category, key):
                        report["applied"].append(op)
                    else:
                        report["skipped"].append({"op": op, "reason": "no existe"})
                else:
                    report["skipped"].append({"op": op, "reason": "acción inválida"})
            except Exception as e:
                report["skipped"].append({"op": op, "reason": str(e)})
        return report

    def _persist_if_possible(self):
        if yaml is None:
            return
        try:
            # Inyectar meta antes de volcar
            if self._usage_meta:
                self.config['_usage_meta'] = self._usage_meta
            with open(self.yaml_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(self.config, f, allow_unicode=True, sort_keys=False)
        except Exception as e:
            print(f"⚠️ No se pudo persistir personality.yaml: {e}")

    # ================================================================

# Instancia global opcional (se puede crear otra en otros módulos si se desea)
personality = PersonalityConfig()
