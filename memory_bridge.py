"""MemoryBridge
Filtro inteligente para decidir qué hechos persistir en personality.yaml.
Características:
 - Heurística previa para descartar comandos efímeros.
 - LLM produce propuesta en JSON restringido.
 - Resolución de conflictos y límite de operaciones.
 - Cooldown por (category,key) y deduplicación contra estado actual.
"""
from __future__ import annotations
import json
import re
import time
from typing import List, Dict, Any

try:  # Import de ollama opcional
    import ollama  # type: ignore
    OLLAMA_AVAILABLE = True
except ImportError:  # Entorno sin ollama -> modo deshabilitado
    OLLAMA_AVAILABLE = False

from personality_config import PersonalityConfig, personality as global_personality


class MemoryBridge:
    def __init__(self, personality_cfg: PersonalityConfig | None = None, model: str = "llama3:latest"):
        self.personality = personality_cfg or global_personality
        self.model = model
        self.enabled = OLLAMA_AVAILABLE
        # Parámetros de selectividad
        self.min_len_fact = 6
        self.cooldown_seconds = 300  # 5 min
        self.max_ops_per_turn = 2
        self._recent_ops: Dict[tuple, float] = {}

    # ---------------- Heurísticas previas ----------------
    def _is_potential_fact(self, text: str) -> bool:
        t = text.lower().strip()
        if len(t) < self.min_len_fact:
            return False
        # Evitar comandos de control sin afirmación factual
        if re.search(r"\b(cambia|cambiar|reproduce|pon|abre|pausa|para|siguiente|skip|busca|play|volumen)\b", t):
            if not re.search(r"\b(mi\s+|tengo\s+|ahora\s+es|es\s+un|es\s+una|favorito|se\s+llama|prefiero)\b", t):
                return False
        # Patrones de hecho/preferencia
        return bool(re.search(r"\b(mi\s+\w+\s+es|tengo\s+|ahora\s+es|favorito|prefiero|se\s+llama)\b", t))

    def _build_context_snapshot(self, limit: int = 25) -> str:
        flat = self.personality.export_flat_facts()
        if len(flat) > limit:
            flat = flat[:limit]
        # Registrar uso de los hechos expuestos (indica que siguen siendo relevantes)
        for f in flat:
            try:
                self.personality.record_fact_usage(f['category'], f['key'])
            except Exception:
                pass
        return "\n".join(f"- {f['category']}.{f['key']}: {f['value']}" for f in flat)

    def _resolve_conflicts(self, ops: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        priority = {'delete': 3, 'replace': 2, 'create': 1, 'append': 0}
        grouped: Dict[tuple, List[Dict[str, Any]]] = {}
        order = []
        for op in ops:
            k = (op.get('category'), op.get('key'))
            if not all(k):
                continue
            if k not in grouped:
                grouped[k] = []
                order.append(k)
            grouped[k].append(op)
        final_ops: List[Dict[str, Any]] = []
        for k in order:
            variants = grouped[k]
            best = None
            best_rank = -1
            for v in variants:
                act = v.get('action') or ''
                r = priority.get(str(act), -1)
                if r > best_rank:
                    best_rank = r
                    best = v
            if best:
                final_ops.append(best)
        return final_ops

    def _cooldown_and_dedupe(self, ops: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        now = time.time()
        for op in ops:
            cat, key = op.get('category'), op.get('key')
            if not cat or not key:
                continue
            ck = (cat, key)
            # Cooldown
            if now - self._recent_ops.get(ck, 0) < self.cooldown_seconds:
                continue
            # Redundancia
            existing_bucket = self.personality.config.get(cat, {}) if isinstance(self.personality.config.get(cat), dict) else {}
            existing_val = existing_bucket.get(key)
            val = op.get('value')
            if op['action'] in ['create', 'replace', 'append'] and existing_val is not None and val is not None:
                nv = str(val).strip().lower()
                if isinstance(existing_val, list):
                    if any(str(x).strip().lower() == nv for x in existing_val):
                        continue
                else:
                    if str(existing_val).strip().lower() == nv:
                        continue
            out.append(op)
            self._recent_ops[ck] = now
            if len(out) >= self.max_ops_per_turn:
                break
        return out

    # ---------------- Flujo principal ----------------
    def propose_operations(self, user_input: str, bot_response: str = "") -> Dict[str, Any]:
        if not self.enabled:
            return {"operations": [], "reasoning": "ollama_off"}
        if not self._is_potential_fact(user_input):
            return {"operations": [], "reasoning": "no_fact_candidate"}

        snapshot = self._build_context_snapshot()
        instruction = (
            "Eres un filtro de MEMORIA. Devuelve SOLO JSON. Decide si el usuario dio un DATO NUEVO o CAMBIO REAL.\n"
            "Ignora saludos, comandos de control y peticiones temporales.\n"
            f"HECHOS (parcial):\n{snapshot}\n\n"
            f"USUARIO: {user_input}\nBOT: {bot_response}\n\n"
            "FORMAT JSON: {\"operations\":[{\"action\":...,\"category\":...,\"key\":...,\"value\":...}],\"reasoning\":\"...\"}.\n"
            "Acciones permitidas: create|append|replace|delete. Máx 2. Si nada: operations vacía.\nJSON:")

        try:
            resp = ollama.generate(model=self.model, prompt=instruction, options={"temperature": 0.1, "num_predict": 250})
            raw = (resp.get('response') or '').strip()
            start, end = raw.find('{'), raw.rfind('}') + 1
            if start < 0 or end <= start:
                return {"operations": [], "reasoning": "no_json"}
            try:
                data = json.loads(raw[start:end])
            except Exception:
                return {"operations": [], "reasoning": "parse_fail"}
            ops = data.get('operations') if isinstance(data, dict) else []
            if not isinstance(ops, list):
                return {"operations": [], "reasoning": "bad_format"}
            cleaned: List[Dict[str, Any]] = []
            for op in ops[:5]:
                if not isinstance(op, dict):
                    continue
                action = op.get('action')
                if action not in ['create', 'append', 'replace', 'delete']:
                    continue
                key = op.get('key')
                if not key:
                    continue
                if action in ['create', 'append', 'replace'] and op.get('value') is None:
                    continue
                cleaned.append({
                    'action': action,
                    'category': op.get('category') or self.personality.guess_category(key),
                    'key': key,
                    'value': op.get('value')
                })
            if not cleaned:
                return {"operations": [], "reasoning": data.get('reasoning', '')}
            resolved = self._resolve_conflicts(cleaned)
            final_ops = self._cooldown_and_dedupe(resolved)
            return {"operations": final_ops, "reasoning": data.get('reasoning', '')}
        except Exception as e:
            return {"operations": [], "reasoning": f"error:{e}"}

    def query_facts(self, query: str, max_results: int = 5):
        return self.personality.search_facts(query, max_results=max_results)

    def run_maintenance(self, min_age_seconds: int = 7*24*3600, max_count: int = 0, limit: int = 5) -> Dict[str, Any]:
        """Ejecuta limpieza automática de hechos casi nunca usados.
        Por defecto: candidatos con 0 usos y >=7 días de antigüedad.
        """
        try:
            return self.personality.auto_forget_rare_facts(min_age_seconds=min_age_seconds, max_count=max_count, limit=limit)
        except Exception as e:
            return {"removed": [], "skipped": [], "error": str(e)}


if __name__ == '__main__':  # Prueba manual ligera
    mb = MemoryBridge()
    print(mb.propose_operations("mi anime favorito ahora es Vinland Saga"))
