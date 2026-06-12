import os
from typing import Dict, Any

from executor_service.ui_compressor import compress_ui_for_llm


class PromptBuilder:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.system_prompt = self._load_prompt("system_prompt.txt")
        self.action_prompt = self._load_prompt("action_prompt.txt")

    def _load_prompt(self, filename: str) -> str:
        filepath = os.path.join(self.base_dir, "prompts", filename)
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                return f.read().strip()
        return ""

    def build_planner_prompt(self, goal: str, ui_state: Dict[str, Any], history: list) -> str:
        # Compress UI state — deduplicate, filter, cap at 40 elements
        compressed = compress_ui_for_llm(ui_state)
        visible_elements = compressed.get("elements", [])
        screen = ui_state.get("screen", {})
        metadata = ui_state.get("metadata", {})
        
        # Get element hash map for LLM reference (like SOC)
        element_map = ui_state.get("element_map", {})
        
        # Build element map string for the prompt
        element_map_str = ""
        if element_map:
            for label, elem in element_map.items():
                text = elem.get("text", "")
                coords = elem.get("center", [])
                clickable = elem.get("clickable", False)
                if text and coords:
                    click_str = " (clickable)" if clickable else ""
                    element_map_str += f"  {label}: '{text}' at {coords}{click_str}\n"

        # Build condensed element list (much smaller token footprint)
        condensed_ui = []
        for el in visible_elements:
            text = el.get("text", "").strip()
            center = el.get("center", [])
            el_type = el.get("type", "element")
            clickable = el.get("clickable", False)
            click_mark = " [CLICKABLE]" if clickable else ""
            if center:
                condensed_ui.append(f"[{el_type}] '{text}' at {center}{click_mark}")
            else:
                condensed_ui.append(f"[{el_type}] '{text}'{click_mark}")

        # Only include last 5 history entries
        recent_history = history[-5:] if history else []
        history_str = "\n".join(
            f"  {h.get('action', 'unknown')} ({'success' if h.get('success') else 'failed'})"
            for h in recent_history
        )

        prompt = f"{self.system_prompt}\n\n"
        prompt += f"GOAL: {goal}\n\n"
        
        if element_map_str:
            prompt += f"ELEMENT MAP (use these labels to click):\n{element_map_str}\n"
        
        prompt += (
            "SCREEN:\n"
            f"  coordinate_system={screen.get('coordinate_system', 'screen')}\n"
            f"  capture={screen.get('capture_scope', metadata.get('capture_scope', 'unknown'))}\n"
            f"  app={screen.get('app', metadata.get('app', 'unknown'))}\n"
            f"  origin=({screen.get('origin_x', 0)}, {screen.get('origin_y', 0)})\n"
            f"  size={screen.get('width', '?')}x{screen.get('height', '?')}\n\n"
        )
        prompt += f"VISIBLE UI ({compressed.get('total_filtered', 0)} of {compressed.get('total_raw', 0)} elements):\n"
        prompt += "\n".join(condensed_ui) + "\n\n"
        if history_str:
            prompt += f"RECENT HISTORY:\n{history_str}\n\n"
        
        # Replace ELEMENT_MAP placeholder in action prompt
        action_prompt = self.action_prompt.replace("{ELEMENT_MAP}", element_map_str or "No elements detected")
        prompt += action_prompt

        return prompt
