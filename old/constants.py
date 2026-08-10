"""Shared constants: styling, parent template names, civilizations."""

from typing import Dict, List

# Color scheme constants - High contrast dark theme for visibility
STYLE: Dict[str, str] = {
    # Background colors - higher contrast
    "bg": "#2d2d3d",           # Dark gray background
    "bg_secondary": "#3d3d4d", # Secondary background
    "panel": "#383848",        # Panel background
    "panel_light": "#4d4d5d",  # Lighter panel for buttons
    "card": "#404050",         # Card background
    
    # Accent colors - vibrant and visible
    "accent": "#7b5eff",       # Bright purple
    "accent_hover": "#9a7cff", # Lighter purple for hover
    "accent_secondary": "#5a5a7a", # Secondary accent
    
    # Text colors - high contrast
    "text": "#ffffff",         # Pure white text
    "text_dim": "#c0c0d0",    # Light gray text
    "text_muted": "#9090a0",  # Muted text
    
    # Input colors - visible borders
    "entry_bg": "#1a1a2a",     # Dark entry background
    "entry_border": "#6a6a8a", # Visible border
    "entry_focus": "#7b5eff",  # Entry focus color
    
    # Status colors - bright and visible
    "success": "#4ade80",      # Bright green
    "warning": "#fbbf24",      # Bright yellow
    "error": "#f87171",        # Bright red
    "info": "#60a5fa",         # Bright blue
    
    # Special colors - visible borders
    "border": "#6a6a8a",       # Visible border color
    "divider": "#505060",      # Visible divider color
    "shadow": "rgba(0, 0, 0, 0.5)", # Darker shadow
}

# Common parent template names for unit inheritance
COMMON_PARENTS: List[str] = [
    "template_unit_infantry_melee_swordsman",
    "template_unit_infantry_melee_spearman",
    "template_unit_infantry_ranged_archer",
    "template_unit_infantry_ranged_javelineer",
    "template_unit_cavalry_melee_swordsman",
    "template_unit_cavalry_melee_spearman",
    "template_unit_cavalry_ranged_archer",
    "template_unit_champion_infantry_swordsman",
    "template_unit_champion_infantry_spearman",
    "template_unit_champion_cavalry_swordsman",
    "template_unit_champion_cavalry_spearman",
    "template_unit_siege_bolt_shooter",
    "template_unit_siege_ram",
    "template_unit_siege_tower",
    "template_unit_support_healer",
    "template_unit_support_female_citizen",
    "template_unit_hero_infantry_swordsman",
    "template_unit_hero_cavalry_swordsman",
]

# Civilization codes
CIVS: List[str] = [
    "gaia", "athen", "brit", "cart", "gaul", "han", "iber", "kush",
    "mace", "maur", "pers", "ptol", "rome", "sele", "spart",
]

# UI spacing constants
SPACING = {
    "tiny": 4,
    "small": 8,
    "medium": 12,
    "large": 16,
    "xlarge": 20,
    "xxlarge": 24,
}

# Border radius constants
BORDER_RADIUS = {
    "small": 4,
    "medium": 8,
    "large": 12,
}