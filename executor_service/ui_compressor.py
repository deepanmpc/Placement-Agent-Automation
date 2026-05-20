from typing import Dict, Any, List
from executor_service.config import Config


def compress_ui_for_llm(ui_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compress raw UI state before sending to the LLM planner.
    
    Transformations:
    1. Deduplicate by text
    2. Filter low-confidence / empty elements
    3. Prioritize interactive elements (buttons, inputs, links)
    4. Cap at MAX_UI_ELEMENTS_FOR_LLM
    5. Generate a structured summary
    """
    raw_elements = ui_state.get("elements", [])
    
    # Step 1: Filter junk
    filtered = []
    seen_texts = set()
    for el in raw_elements:
        text = el.get("text", "").strip()
        
        # Skip empty or too-short text
        if len(text) < Config.MIN_ELEMENT_TEXT_LENGTH:
            continue
        
        # Skip duplicates
        text_lower = text.lower()
        if text_lower in seen_texts:
            continue
        seen_texts.add(text_lower)
        
        filtered.append(el)
    
    # Step 2: Prioritize interactive elements
    interactive_types = {"button", "input", "link", "tab", "menu", "checkbox", "select"}
    interactive = [el for el in filtered if el.get("type", "").lower() in interactive_types]
    non_interactive = [el for el in filtered if el.get("type", "").lower() not in interactive_types]
    
    # Interactive elements first, then text elements
    prioritized = interactive + non_interactive
    
    # Step 3: Cap at limit
    capped = prioritized[:Config.MAX_UI_ELEMENTS_FOR_LLM]
    
    # Step 4: Build compressed state
    return {
        "elements": capped,
        "total_raw": len(raw_elements),
        "total_filtered": len(capped),
        "has_more": len(filtered) > Config.MAX_UI_ELEMENTS_FOR_LLM,
    }


def build_ui_summary(ui_state: Dict[str, Any]) -> str:
    """
    Build a compact text summary for the LLM instead of dumping all elements.
    Much smaller token footprint.
    """
    elements = ui_state.get("elements", [])
    
    buttons = []
    inputs = []
    texts = []
    
    for el in elements:
        text = el.get("text", "").strip()
        if not text:
            continue
        el_type = el.get("type", "text").lower()
        center = el.get("center", [])
        entry = f"'{text}' at {center}" if center else f"'{text}'"
        
        if el_type in ("button", "link", "tab", "menu"):
            buttons.append(entry)
        elif el_type in ("input", "search", "textarea"):
            inputs.append(entry)
        else:
            texts.append(entry)
    
    parts = []
    if inputs:
        parts.append(f"INPUTS: {', '.join(inputs[:10])}")
    if buttons:
        parts.append(f"BUTTONS: {', '.join(buttons[:15])}")
    if texts:
        parts.append(f"TEXT: {', '.join(texts[:15])}")
    
    return "\n".join(parts)
