#!/usr/bin/env python3
"""
FULL COVERAGE Token Transformer
Generates both Kotlin (.kt) and XML (.xml) outputs for ALL token types with mode/theme support.

Features:
- Loads all token files with support for Brand and Theme modes
- Brand modes: Default, Performance, Luxury
- Theme modes: Day (light), Night (dark)
- Extracts ALL token types (colors, spacing, typography, motion, components, accessibility, etc.)
- Generates Kotlin outputs: Color.kt, Spacing.kt, Typography.kt, Motion.kt, etc.
- Generates XML outputs: colors.xml, dimens.xml, typography.xml, animations.xml, etc.
- Generates CSS outputs: tokens.css (CSS custom properties)
- Full coverage: 750+ tokens
- Mode-aware exports: Can export all brand/theme combinations separately
- Separate output folders: _TransformedTokens/kotlin/, _TransformedTokens/xml/, and _TransformedTokens/css/

Usage:
    # Export default combination (Default brand, Day theme)
    python3 token_transformer_full_coverage.py /path/to/workspace
    
    # Export all brand/theme combinations (6 combinations total)
    python3 token_transformer_full_coverage.py /path/to/workspace --modes

Output Structure (with --modes):
    _TransformedTokens/
    ├── kotlin/
    │   ├── default_day/     # Default brand, Day theme
    │   ├── default_night/   # Default brand, Night theme
    │   ├── performance_day/  # Performance brand, Day theme
    │   ├── performance_night/
    │   ├── luxury_day/
    │   └── luxury_night/
    ├── xml/
    │   └── (same structure)
    └── css/
        └── (same structure)
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class TransformerConfig:
    """Configuration for transformer."""
    base_path: str
    kotlin_output_path: Optional[str] = None
    xml_output_path: Optional[str] = None
    css_output_path: Optional[str] = None
    verbose: bool = True


class FullCoverageTransformer:
    """Transform 750+ tokens to both Kotlin and XML formats."""

    def __init__(self, config: TransformerConfig):
        self.config = config
        self.base_path = Path(config.base_path)
        self.token_data = {}
        self.resolved_cache = {}
        self.unresolved_refs = set()
        
        # Initialize output paths
        self.kotlin_output_path = Path(config.kotlin_output_path or self.base_path / "_TransformedTokens" / "kotlin")
        self.xml_output_path = Path(config.xml_output_path or self.base_path / "_TransformedTokens" / "xml")
        self.css_output_path = Path(config.css_output_path or self.base_path / "_TransformedTokens" / "css")
        
        # Create output directories
        self.kotlin_output_path.mkdir(parents=True, exist_ok=True)
        self.xml_output_path.mkdir(parents=True, exist_ok=True)
        self.css_output_path.mkdir(parents=True, exist_ok=True)

    def log(self, message: str, level: str = "info"):
        """Log with emoji indicators."""
        if not self.config.verbose:
            return
        icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌", "debug": "🐛"}
        icon = icons.get(level, "•")
        print(f"{icon}  {message}")

    def load_json(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.log(f"Error loading {file_path}: {e}", "error")
            return {}

    def load_all_tokens(self, brand: str = "Default", theme: str = "Day"):
        """
        Load all token files with support for brand and theme modes.
        
        Args:
            brand: Brand mode - "Default", "Performance", or "Luxury"
            theme: Theme mode - "Day" or "Night"
        """
        # Always load base tokens
        base_files = [
            "Tokens/New/_Base/Value.json",
        ]
        
        # Load brand-specific tokens
        brand_files = [
            f"Tokens/New/01_Brand/{brand}.json",
        ]
        
        # Load theme-specific tokens
        theme_files = [
            f"Tokens/New/03_Themes/{theme}.json",
        ]
        
        # Load shared tokens (motion, interactions, components)
        shared_files = [
            "Tokens/New/04_Motion/Animations.json",
            "Tokens/New/05_Interactions/States.json",
            "Tokens/New/07_Components/Compositions.json",
        ]
        
        all_files = base_files + brand_files + theme_files + shared_files
        
        self.log(f"Loading tokens for Brand={brand}, Theme={theme}...", "info")
        self.log(f"  Total files: {len(all_files)}", "info")
        
        for file_path in all_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                self.log(f"  ✓ {file_path}")
                data = self.load_json(full_path)
                # Deep merge to avoid overwriting nested objects
                self._deep_merge(self.token_data, data)
            else:
                self.log(f"  ⚠ {file_path} not found", "warning")
        
        self.log(f"Loaded all tokens. Total keys: {len(self.token_data)}", "success")
    
    def _deep_merge(self, target: dict, source: dict):
        """Deep merge source dict into target dict."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # Recursively merge nested dicts
                self._deep_merge(target[key], value)
            else:
                # Otherwise, update/add the value
                target[key] = value

    def resolve_reference(self, ref_string: str) -> str:
        """Resolve token references."""
        if ref_string in self.resolved_cache:
            return self.resolved_cache[ref_string]

        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, ref_string)

        if not matches:
            return ref_string

        resolved = ref_string
        for token_path in matches:
            value = self._get_token_value(token_path)
            if value:
                resolved = resolved.replace(f"{{{token_path}}}", str(value))
            else:
                self.unresolved_refs.add(token_path)

        self.resolved_cache[ref_string] = resolved
        return resolved

    def _get_token_value(self, path: str):
        """Get token value by path."""
        parts = path.split('.')
        current = self.token_data

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        if isinstance(current, dict):
            if 'value' in current:
                value = current['value']
                if isinstance(value, str) and '{' in value:
                    return self.resolve_reference(value)
                return value
        elif isinstance(current, (str, int, float, bool)):
            return current

        return None

    # ===== EXTRACTION METHODS =====

    def extract_colors(self) -> Dict[str, str]:
        """Extract all color tokens from primitives, brand, and theme."""
        colors = {}
        
        # Extract color-primitives
        if "color-primitives" in self.token_data:
            for color_group, values in self.token_data["color-primitives"].items():
                if isinstance(values, dict):
                    for level, token_def in values.items():
                        if isinstance(token_def, dict) and "value" in token_def:
                            key = f"color_primitives_{color_group}_{level}"
                            value = self.resolve_reference(str(token_def["value"]))
                            colors[key] = value
        
        # Extract brand colors (color.brandPrimary, color.functional, etc.)
        if "color" in self.token_data:
            color_data = self.token_data["color"]
            if isinstance(color_data, dict):
                for category, category_data in color_data.items():
                    if isinstance(category_data, dict):
                        for name, token_def in category_data.items():
                            if isinstance(token_def, dict) and "value" in token_def:
                                key = f"color_{category}_{name}"
                                value = self.resolve_reference(str(token_def["value"]))
                                colors[key] = value
                            elif isinstance(token_def, dict):
                                # Handle nested structures (e.g., color.brandPrimary.primary)
                                for sub_name, sub_def in token_def.items():
                                    if isinstance(sub_def, dict) and "value" in sub_def:
                                        key = f"color_{category}_{name}_{sub_name}"
                                        value = self.resolve_reference(str(sub_def["value"]))
                                        colors[key] = value
        
        self.log(f"Extracted {len(colors)} color tokens", "info")
        return colors

    def extract_spacing(self) -> Dict[str, int]:
        """Extract spacing tokens."""
        spacing = {}
        if "spacing" in self.token_data:
            for name, token_def in self.token_data["spacing"].items():
                if isinstance(token_def, dict) and "value" in token_def:
                    spacing[name] = token_def["value"]
        self.log(f"Extracted {len(spacing)} spacing tokens", "info")
        return spacing

    def extract_typography(self) -> Dict[str, Dict]:
        """Extract typography tokens (font sizes, line heights, weights, compositions)."""
        typography = {
            "fontSize": {},
            "lineHeight": {},
            "fontWeight": {},
            "compositions": {}  # Typography composition tokens (heading-80, body-100, etc.)
        }
        
        # Extract fontSize
        if "fontSize" in self.token_data:
            fs_data = self.token_data["fontSize"]
            self.log(f"  Found fontSize with {len(fs_data)} tokens", "debug")
            for name, token_def in fs_data.items():
                if not name.startswith("_"):  # Skip comments
                    if isinstance(token_def, dict) and "value" in token_def:
                        typography["fontSize"][name] = token_def["value"]
                        self.log(f"    fontSize.{name} = {token_def['value']}", "debug")
        
        # Extract lineHeight
        if "lineHeight" in self.token_data:
            lh_data = self.token_data["lineHeight"]
            self.log(f"  Found lineHeight with {len(lh_data)} tokens", "debug")
            for name, token_def in lh_data.items():
                if not name.startswith("_"):  # Skip comments
                    if isinstance(token_def, dict) and "value" in token_def:
                        typography["lineHeight"][name] = token_def["value"]
                        self.log(f"    lineHeight.{name} = {token_def['value']}", "debug")
        
        # Extract font weights from Typography-Advanced
        if "Typography-Advanced" in self.token_data:
            typo_adv = self.token_data["Typography-Advanced"]
            if isinstance(typo_adv, dict):
                for name, token_def in typo_adv.items():
                    if not name.startswith("_") and isinstance(token_def, dict) and "value" in token_def:
                        if "font-weight" in name.lower():
                            weight_name = name.replace("font-weight-", "").replace("-", "_")
                            typography["fontWeight"][weight_name] = token_def["value"]
        
        # Extract Typography composition tokens (heading-80, body-100, etc.)
        if "Typography" in self.token_data:
            typo_compositions = self.token_data["Typography"]
            if isinstance(typo_compositions, dict):
                for name, token_def in typo_compositions.items():
                    if not name.startswith("_") and isinstance(token_def, dict) and "value" in token_def:
                        value = token_def["value"]
                        if isinstance(value, dict):
                            # Resolve fontFamily references and extract all typography properties
                            resolved_value = {}
                            for key, val in value.items():
                                if key == "fontFamily" and isinstance(val, str) and val.startswith("{") and val.endswith("}"):
                                    # Resolve fontFamily reference (e.g., {fontFamily.hmi})
                                    font_family_path = val.strip("{}")
                                    resolved_font = self._get_token_value(font_family_path)
                                    if resolved_font:
                                        # Extract font name from resolved value (e.g., "tt commons pro", "Arial, sans-serif", "Georgia, serif")
                                        font_name = resolved_font if isinstance(resolved_font, str) else str(resolved_font)
                                        font_name_lower = font_name.lower()
                                        # Map to Android system fonts:
                                        # - "Arial, sans-serif" or "tt commons pro" → sans-serif (TT Commons Pro is a sans-serif font)
                                        # - "Georgia, serif" → serif
                                        if "georgia" in font_name_lower or ("serif" in font_name_lower and "sans-serif" not in font_name_lower):
                                            resolved_value[key] = "serif"
                                        else:
                                            # Default to sans-serif for Arial, TT Commons Pro, and any other sans-serif fonts
                                            resolved_value[key] = "sans-serif"
                                    else:
                                        resolved_value[key] = "sans-serif"  # Default fallback
                                elif key == "letterSpacing" and isinstance(val, (str, int, float)):
                                    # Resolve letterSpacing if it's a reference, otherwise keep the value
                                    if isinstance(val, str) and val.startswith("{") and val.endswith("}"):
                                        letter_spacing_path = val.strip("{}")
                                        resolved_letter_spacing = self._get_token_value(letter_spacing_path)
                                        if resolved_letter_spacing is not None:
                                            resolved_value[key] = resolved_letter_spacing
                                        else:
                                            # If resolution fails, try to extract numeric value from the path
                                            # e.g., {letterSpacing.normal} -> check if there's a numeric value
                                            resolved_value[key] = val  # Keep original if can't resolve
                                    else:
                                        # Direct value (number or string number)
                                        resolved_value[key] = float(val) if isinstance(val, (str, int, float)) and str(val).replace('.', '').isdigit() else val
                                else:
                                    # Keep other values as-is (fontSize, lineHeight, etc.)
                                    resolved_value[key] = val
                            typography["compositions"][name] = resolved_value
        
        # Fallback: create standard weights if not found
        if not typography["fontWeight"]:
            self.log("  No font weights found, using defaults", "debug")
            typography["fontWeight"] = {
                "light": 300,
                "regular": 400,
                "medium": 500,
                "semibold": 600,
                "bold": 700
            }
        
        total = sum(len(v) for v in typography.values())
        self.log(f"Extracted {total} typography tokens (sizes: {len(typography['fontSize'])}, heights: {len(typography['lineHeight'])}, weights: {len(typography['fontWeight'])}, compositions: {len(typography['compositions'])})", "info")
        return typography

    def extract_elevation(self) -> Dict[str, Dict]:
        """Extract elevation/shadow tokens."""
        elevation = {}
        if "elevation" in self.token_data:
            for name, token_def in self.token_data["elevation"].items():
                if isinstance(token_def, dict) and "value" in token_def:
                    elevation[name] = token_def["value"]
        self.log(f"Extracted {len(elevation)} elevation tokens", "info")
        return elevation

    def extract_radius(self) -> Dict[str, int]:
        """Extract border radius tokens."""
        radius = {}
        if "borderRadius" in self.token_data:
            for name, token_def in self.token_data["borderRadius"].items():
                if isinstance(token_def, dict) and "value" in token_def:
                    radius[name] = token_def["value"]
        self.log(f"Extracted {len(radius)} border radius tokens", "info")
        return radius

    def extract_border_width(self) -> Dict[str, str]:
        """Extract border width tokens."""
        border_width = {}
        if "borderWidth" in self.token_data:
            for name, token_def in self.token_data["borderWidth"].items():
                if isinstance(token_def, dict) and "value" in token_def:
                    border_width[name] = token_def["value"]
        self.log(f"Extracted {len(border_width)} border width tokens", "info")
        return border_width

    def extract_text_case(self) -> Dict[str, str]:
        """Extract text case tokens."""
        text_case = {}
        if "textCase" in self.token_data:
            for name, token_def in self.token_data["textCase"].items():
                if isinstance(token_def, dict) and "value" in token_def:
                    text_case[name] = token_def["value"]
        self.log(f"Extracted {len(text_case)} text case tokens", "info")
        return text_case

    def extract_letter_spacing(self) -> Dict[str, Dict]:
        """Extract letter spacing tokens."""
        letter_spacing = {}
        if "letterSpacing" in self.token_data:
            letter_spacing = self.token_data["letterSpacing"]
        self.log(f"Extracted {len(letter_spacing)} letter spacing token groups", "info")
        return letter_spacing

    def extract_layout(self) -> Dict[str, Dict]:
        """Extract layout tokens (breakpoints, spacing modes, touch targets)."""
        layout = {}
        if "layout" in self.token_data:
            layout = self.token_data["layout"]
        self.log(f"Extracted {len(layout)} layout token groups", "info")
        return layout

    def extract_platforms(self) -> Dict[str, Dict]:
        """Extract platform-specific tokens (Android, QNX)."""
        platforms = {}
        if "platforms" in self.token_data:
            platforms = self.token_data["platforms"]
        self.log(f"Extracted {len(platforms)} platform-specific token groups", "info")
        return platforms

    def extract_motion(self) -> Dict[str, Dict]:
        """Extract motion/animation tokens (durations, easing, transitions)."""
        motion = {}
        if "motion" in self.token_data:
            motion = self.token_data["motion"]
        self.log(f"Extracted {len(motion)} motion token groups (duration, easing, transitions)", "info")
        return motion

    def extract_accessibility(self) -> Dict[str, str]:
        """Extract accessibility tokens."""
        accessibility = {}
        
        # From color-primitives.Accessibility
        if "color-primitives" in self.token_data:
            if "Accessibility" in self.token_data["color-primitives"]:
                for name, token_def in self.token_data["color-primitives"]["Accessibility"].items():
                    if isinstance(token_def, dict) and "value" in token_def:
                        accessibility[name] = str(token_def["value"])
        
        # From root level Accessibility
        if "Accessibility" in self.token_data:
            for name, token_def in self.token_data["Accessibility"].items():
                if isinstance(token_def, dict) and "value" in token_def:
                    accessibility[name] = str(token_def["value"])
        
        # Fallback: create standard accessibility tokens
        if not accessibility:
            accessibility = {
                "wcag_aa_text_on_primary": "#ffffff",
                "wcag_aa_text_on_error": "#ffffff",
                "wcag_aa_text_on_success": "#ffffff",
                "wcag_aa_text_on_warning": "#000000",
                "high_contrast_primary": "#0033cc",
                "high_contrast_text": "#000000",
                "focus_indicator": "#ffff00",
                "focus_indicator_dark": "#ffff00"
            }
        
        self.log(f"Extracted {len(accessibility)} accessibility tokens", "info")
        return accessibility

    def extract_interactions(self) -> Dict[str, Dict]:
        """Extract interaction state tokens (hover, active, focus, disabled, etc.)."""
        interactions = {}
        if "interaction" in self.token_data:
            interactions = self.token_data["interaction"]
        self.log(f"Extracted {len(interactions)} interaction state groups (hover, active, focus, disabled, etc.)", "info")
        return interactions

    def extract_components(self) -> Dict[str, Dict]:
        """Extract component-specific tokens (button, card, notification, input, checkbox, radio, toggle, select, modal)."""
        components = {}
        # Extract all known component types (from Compositions.json)
        for key in ["button", "input", "card", "notification", "form", "checkbox", "radio", "toggle", "select", "modal"]:
            if key in self.token_data:
                components[key] = self.token_data[key]
        self.log(f"Extracted {len(components)} component groups (buttons, cards, notifications, forms, inputs, checkboxes, radios, toggles, selects, modals)", "info")
        return components

    def extract_all_tokens(self) -> Dict[str, Any]:
        """Extract all token types."""
        return {
            "colors": self.extract_colors(),
            "spacing": self.extract_spacing(),
            "typography": self.extract_typography(),
            "elevation": self.extract_elevation(),
            "radius": self.extract_radius(),
            "border_width": self.extract_border_width(),
            "text_case": self.extract_text_case(),
            "letter_spacing": self.extract_letter_spacing(),
            "layout": self.extract_layout(),
            "platforms": self.extract_platforms(),
            "motion": self.extract_motion(),
            "accessibility": self.extract_accessibility(),
            "interactions": self.extract_interactions(),
            "components": self.extract_components(),
        }

    # ===== KOTLIN OUTPUT GENERATION =====

    def generate_kotlin_color(self, colors: Dict[str, str], mode_suffix: str = None) -> str:
        """Generate Color.kt with all color tokens - valid Kotlin identifiers only."""
        package = 'com.example.hmithemedemo.ui.theme'
        if mode_suffix:
            # Keep underscores in package name to match directory structure
            package = f'{package}.{mode_suffix}'
        
        kotlin = f'package {package}\n\nimport androidx.compose.ui.graphics.Color\n\n'
        kotlin += 'object ColorTokens {\n'
        
        for name, value in sorted(colors.items()):
            # Clean the color value (remove #, handle hex)
            clean_value = value.lstrip("#")
            # Ensure it's a valid hex color with alpha channel
            if len(clean_value) == 6:
                # RGB format - add FF alpha for full opacity
                clean_value = "FF" + clean_value.upper()
            elif len(clean_value) == 8:
                # ARGB format - keep as is
                clean_value = clean_value.upper()
            else:
                # Try to extract hex from string
                hex_match = re.search(r'[0-9A-Fa-f]{6,8}', clean_value)
                if hex_match:
                    extracted = hex_match.group().upper()
                    if len(extracted) == 6:
                        clean_value = "FF" + extracted
                    else:
                        clean_value = extracted
                else:
                    clean_value = "FF000000"  # Fallback to opaque black
            
            prop_name = self._to_camel_case(name)
            kotlin += f'    val {prop_name} = Color(0x{clean_value})\n'
        
        kotlin += '}\n'
        return kotlin

    def generate_kotlin_spacing(self, spacing: Dict[str, int], mode_suffix: str = None) -> str:
        """Generate Spacing.kt - organized by token name suffix with valid Kotlin identifiers."""
        package = 'com.example.hmithemedemo.ui.theme'
        if mode_suffix:
            package = f'{package}.{mode_suffix}'
        
        kotlin = f'package {package}\n\nimport androidx.compose.ui.unit.dp\n\n'
        kotlin += 'object SpacingTokens {\n'
        
        # Extract numeric suffix from token name for grouping
        def get_sort_key(item):
            name, value = item
            # Extract numeric part from name (e.g., "spacing-2" -> 2, "compact-16" -> 16)
            parts = re.split(r'[-_]', name)
            if parts and parts[-1].isdigit():
                suffix_num = int(parts[-1])
            else:
                suffix_num = 999
            return (suffix_num, name)
        
        sorted_spacing = sorted(spacing.items(), key=get_sort_key)
        
        last_suffix = None
        for name, value in sorted_spacing:
            # Extract suffix for grouping
            parts = re.split(r'[-_]', name)
            suffix = parts[-1] if parts else ""
            suffix_num = int(suffix) if suffix.isdigit() else 999
            
            # Add comment header for each new token suffix group
            if suffix_num != last_suffix:
                if last_suffix is not None:
                    kotlin += '\n'
                kotlin += f'    // {suffix} (variants: spacing, compact, spacious)\n'
                last_suffix = suffix_num
            
            prop_name = self._to_camel_case(name)
            # If name starts with number, use spacing prefix
            if prop_name and prop_name[0].isdigit():
                prop_name = 'spacing' + prop_name
            
            kotlin += f'    val {prop_name} = {value}.dp\n'
        
        kotlin += '}\n'
        return kotlin

    def generate_kotlin_typography(self, typography: Dict[str, Dict], mode_suffix: str = None) -> str:
        """Generate Typography.kt."""
        package = 'com.example.hmithemedemo.ui.theme'
        if mode_suffix:
            package = f'{package}.{mode_suffix}'
        
        kotlin = f'package {package}\n\nimport androidx.compose.ui.unit.sp\n\n'
        kotlin += 'object TypographyTokens {\n'
        
        # Font Sizes
        if typography["fontSize"]:
            kotlin += '    // Font Sizes (sp)\n'
            for name in sorted(typography["fontSize"].keys(), key=lambda x: int(x) if x.isdigit() else 999):
                value = typography["fontSize"][name]
                kotlin += f'    val fontSize{name} = {value}.sp\n'
        else:
            kotlin += '    // Font Sizes (sp) - Placeholder\n'
            for i in range(11):
                kotlin += f'    val fontSize{i} = 12.sp\n'
        
        # Line Heights
        kotlin += '\n    // Line Heights (sp)\n'
        if typography["lineHeight"]:
            for name in sorted(typography["lineHeight"].keys(), key=lambda x: int(x) if x.isdigit() else 999):
                value = typography["lineHeight"][name]
                kotlin += f'    val lineHeight{name} = {value}.sp\n'
        else:
            for i in range(5):
                kotlin += f'    val lineHeight{i} = 20.sp\n'
        
        # Font Weights
        kotlin += '\n    // Font Weights\n'
        weights = typography["fontWeight"] if typography["fontWeight"] else {
            "light": 300,
            "regular": 400,
            "medium": 500,
            "semibold": 600,
            "bold": 700
        }
        for name, value in sorted(weights.items()):
            kotlin += f'    val fontWeight{name.capitalize()} = {value}\n'
        
        kotlin += '}\n'
        return kotlin

    def generate_kotlin_radius(self, radius: Dict[str, int], mode_suffix: str = None) -> str:
        """Generate BorderRadius.kt with all border radius tokens - valid Kotlin identifiers."""
        package = 'com.example.hmithemedemo.ui.theme'
        if mode_suffix:
            package = f'{package}.{mode_suffix}'
        
        kotlin = f'package {package}\n\nimport androidx.compose.ui.unit.dp\n\n'
        kotlin += 'object BorderRadiusTokens {\n'
        kotlin += '    // Border radius values for rounded corners\n\n'
        
        if radius:
            for name in sorted(radius.keys()):
                value = radius[name]
                prop_name = self._to_camel_case(name)
                # If name is just a number, prefix with radius
                if prop_name and (prop_name.isdigit() or prop_name.startswith('_')):
                    prop_name = 'radius' + prop_name.lstrip('_')
                kotlin += f'    val {prop_name} = {value}.dp\n'
        
        kotlin += '}\n'
        return kotlin

    def generate_kotlin_elevation(self, elevation: Dict[str, Any], mode_suffix: str = None) -> str:
        """Generate Elevation.kt - extracts blur value from shadow objects."""
        package = 'com.example.hmithemedemo.ui.theme'
        if mode_suffix:
            package = f'{package}.{mode_suffix}'
        
        kotlin = f'package {package}\n\nimport androidx.compose.ui.unit.dp\n\n'
        kotlin += 'object ElevationTokens {\n'
        kotlin += '    // Material Design 3 elevation levels (blur values from shadow)\n'
        
        if elevation:
            for name in sorted(elevation.keys(), key=lambda x: int(x) if x.isdigit() else 999):
                value = elevation[name]
                prop_name = self._to_camel_case(name)
                # If name is just a number, prefix with underscore
                if prop_name and (prop_name.isdigit() or (prop_name.startswith('_') and prop_name[1:].isdigit())):
                    prop_name = '_' + prop_name.lstrip('_')
                
                # The value is already the shadow dict (extracted by extract_elevation)
                if isinstance(value, dict):
                    # It's a shadow dict - extract blur value
                    blur = value.get("blur", 0)
                    # Extract numeric value if it's a string like "4px"
                    if isinstance(blur, str):
                        blur = int(blur.replace('px', '').strip()) if blur.replace('px', '').strip().isdigit() else 0
                    elif isinstance(blur, (int, float)):
                        blur = int(blur)
                    else:
                        blur = 0
                    kotlin += f'    val {prop_name} = {blur}.dp\n'
                elif isinstance(value, (int, float)):
                    kotlin += f'    val {prop_name} = {int(value)}.dp\n'
                else:
                    kotlin += f'    val {prop_name} = 0.dp\n'
        else:
            # Fallback
            kotlin += '    val _0 = 0.dp      // Flat\n'
            kotlin += '    val _1 = 2.dp      // Small shadow\n'
            kotlin += '    val _2 = 4.dp      // Medium shadow\n'
            kotlin += '    val _3 = 8.dp      // Large shadow\n'
            kotlin += '    val _4 = 16.dp     // Extra-large shadow\n'
        
        kotlin += '}\n'
        return kotlin

    def generate_kotlin_motion(self, motion: Dict[str, Any], mode_suffix: str = None) -> str:
        """Generate Motion.kt (durations, easing, transitions)."""
        package = 'com.example.hmithemedemo.ui.theme'
        if mode_suffix:
            package = f'{package}.{mode_suffix}'
        
        kotlin = f'package {package}\n\n'
        kotlin += 'object MotionTokens {\n'
        
        # Durations
        kotlin += '    // Durations (milliseconds)\n'
        if "duration" in motion:
            for name, token_def in motion["duration"].items():
                if isinstance(token_def, dict) and "value" in token_def:
                    kotlin += f'    val duration{self._to_camel_case(name)} = {token_def["value"]}\n'
        else:
            kotlin += '    val durationShort = 100\n'
            kotlin += '    val durationStandard = 300\n'
            kotlin += '    val durationSlow = 500\n'
        
        # Easing
        kotlin += '\n    // Easing Functions\n'
        if "easing" in motion:
            for name, token_def in motion["easing"].items():
                if isinstance(token_def, dict) and "value" in token_def:
                    kotlin += f'    val easing{self._to_camel_case(name)} = "{token_def["value"]}"\n'
        else:
            kotlin += '    val easingDefault = "cubic-bezier(0.25, 0.46, 0.45, 0.94)"\n'
            kotlin += '    val easingEntrance = "cubic-bezier(0.34, 1.56, 0.64, 1)"\n'
            kotlin += '    val easingExit = "cubic-bezier(0.66, 0, 0.66, 0.07)"\n'
        
        # Transitions (NEW)
        kotlin += '\n    // Transitions (combined duration + easing)\n'
        if "transition" in motion:
            for name, token_def in motion["transition"].items():
                if isinstance(token_def, dict) and "value" in token_def:
                    kotlin += f'    val transition{self._to_camel_case(name)} = "{token_def["value"]}"\n'
        
        kotlin += '}\n'
        return kotlin

    def generate_kotlin_accessibility(self, accessibility: Dict[str, str], mode_suffix: str = None) -> str:
        """Generate Accessibility.kt."""
        package = 'com.example.hmithemedemo.ui.theme'
        if mode_suffix:
            package = f'{package}.{mode_suffix}'
        
        kotlin = f'package {package}\n\nimport androidx.compose.ui.graphics.Color\n\n'
        kotlin += 'object AccessibilityTokens {\n'
        
        for name, value in sorted(accessibility.items()):
            if isinstance(value, str) and value.startswith("#"):
                kotlin += f'    val {self._to_camel_case(name)} = Color(0x{value.lstrip("#")})\n'
            else:
                kotlin += f'    val {self._to_camel_case(name)} = "{value}"\n'
        
        kotlin += '}\n'
        return kotlin

    def generate_kotlin_interactions(self, interactions: Dict[str, Dict], mode_suffix: str = None) -> str:
        """Generate Interactions.kt for state tokens (hover, active, focus, disabled)."""
        package = 'com.example.hmithemedemo.ui.theme'
        if mode_suffix:
            package = f'{package}.{mode_suffix}'
        
        kotlin = f'package {package}\n\nimport androidx.compose.ui.graphics.Color\n\n'
        kotlin += 'object InteractionTokens {\n'
        
        for state_name, state_def in sorted(interactions.items()):
            kotlin += f'\n    // {state_name.capitalize()} State\n'
            state_obj_name = self._to_camel_case(state_name)
            # Ensure it starts with uppercase for object name
            if state_obj_name:
                state_obj_name = state_obj_name[0].upper() + state_obj_name[1:]
            else:
                state_obj_name = state_name.title()
            kotlin += f'    object {state_obj_name} {{\n'
            
            if isinstance(state_def, dict):
                for property_name, property_def in sorted(state_def.items()):
                    if isinstance(property_def, dict) and "value" in property_def:
                        value = property_def["value"]
                        prop_name = self._to_camel_case(property_name)
                        if isinstance(value, str) and value.startswith("#"):
                            clean_value = value.lstrip("#").upper()
                            kotlin += f'        val {prop_name} = Color(0x{clean_value})\n'
                        elif isinstance(value, (int, float)):
                            kotlin += f'        val {prop_name} = {value}\n'
                        else:
                            kotlin += f'        val {prop_name} = "{value}"\n'
            
            kotlin += '    }\n'
        
        kotlin += '}\n'
        return kotlin

    def generate_kotlin_token_provider(self) -> str:
        """Generate TokenProvider.kt - factory that maps brands/themes to token objects."""
        kotlin = '''package com.example.hmithemedemo.ui.theme.tokens

import com.example.hmithemedemo.ui.theme.default_day.ColorTokens as DefaultDayColorTokens
import com.example.hmithemedemo.ui.theme.default_day.SpacingTokens as DefaultDaySpacingTokens
import com.example.hmithemedemo.ui.theme.default_day.TypographyTokens as DefaultDayTypographyTokens
import com.example.hmithemedemo.ui.theme.default_day.BorderRadiusTokens as DefaultDayBorderRadiusTokens

import com.example.hmithemedemo.ui.theme.default_night.ColorTokens as DefaultNightColorTokens
import com.example.hmithemedemo.ui.theme.default_night.SpacingTokens as DefaultNightSpacingTokens
import com.example.hmithemedemo.ui.theme.default_night.TypographyTokens as DefaultNightTypographyTokens
import com.example.hmithemedemo.ui.theme.default_night.BorderRadiusTokens as DefaultNightBorderRadiusTokens

import com.example.hmithemedemo.ui.theme.luxury_day.ColorTokens as LuxuryDayColorTokens
import com.example.hmithemedemo.ui.theme.luxury_day.SpacingTokens as LuxuryDaySpacingTokens
import com.example.hmithemedemo.ui.theme.luxury_day.TypographyTokens as LuxuryDayTypographyTokens
import com.example.hmithemedemo.ui.theme.luxury_day.BorderRadiusTokens as LuxuryDayBorderRadiusTokens

import com.example.hmithemedemo.ui.theme.luxury_night.ColorTokens as LuxuryNightColorTokens
import com.example.hmithemedemo.ui.theme.luxury_night.SpacingTokens as LuxuryNightSpacingTokens
import com.example.hmithemedemo.ui.theme.luxury_night.TypographyTokens as LuxuryNightTypographyTokens
import com.example.hmithemedemo.ui.theme.luxury_night.BorderRadiusTokens as LuxuryNightBorderRadiusTokens

import com.example.hmithemedemo.ui.theme.performance_day.ColorTokens as PerformanceDayColorTokens
import com.example.hmithemedemo.ui.theme.performance_day.SpacingTokens as PerformanceDaySpacingTokens
import com.example.hmithemedemo.ui.theme.performance_day.TypographyTokens as PerformanceDayTypographyTokens
import com.example.hmithemedemo.ui.theme.performance_day.BorderRadiusTokens as PerformanceDayBorderRadiusTokens

import com.example.hmithemedemo.ui.theme.performance_night.ColorTokens as PerformanceNightColorTokens
import com.example.hmithemedemo.ui.theme.performance_night.SpacingTokens as PerformanceNightSpacingTokens
import com.example.hmithemedemo.ui.theme.performance_night.TypographyTokens as PerformanceNightTypographyTokens
import com.example.hmithemedemo.ui.theme.performance_night.BorderRadiusTokens as PerformanceNightBorderRadiusTokens

/**
 * Token Provider Factory
 * Automatically maps brand/theme combinations to the correct token objects.
 * 
 * Brand mapping:
 *   "A" or "Default" -> Default brand
 *   "B" or "Luxury" -> Luxury brand
 *   "C" or "Performance" -> Performance brand
 * 
 * Theme mapping:
 *   true or "Night" -> Night theme
 *   false or "Day" -> Day theme
 */
object TokenProvider {
    /**
     * Get color tokens for the specified brand and theme.
     */
    fun getColorTokens(brand: String, darkTheme: Boolean): Any {
        return when {
            brand.equals("B", ignoreCase = true) || brand.equals("Luxury", ignoreCase = true) -> {
                if (darkTheme) LuxuryNightColorTokens else LuxuryDayColorTokens
            }
            brand.equals("C", ignoreCase = true) || brand.equals("Performance", ignoreCase = true) -> {
                if (darkTheme) PerformanceNightColorTokens else PerformanceDayColorTokens
            }
            else -> { // Default or "A"
                if (darkTheme) DefaultNightColorTokens else DefaultDayColorTokens
            }
        }
    }
    
    /**
     * Get spacing tokens (same across all brands/themes, but included for consistency).
     */
    fun getSpacingTokens(brand: String, darkTheme: Boolean): Any {
        return when {
            brand.equals("B", ignoreCase = true) || brand.equals("Luxury", ignoreCase = true) -> {
                if (darkTheme) LuxuryNightSpacingTokens else LuxuryDaySpacingTokens
            }
            brand.equals("C", ignoreCase = true) || brand.equals("Performance", ignoreCase = true) -> {
                if (darkTheme) PerformanceNightSpacingTokens else PerformanceDaySpacingTokens
            }
            else -> {
                if (darkTheme) DefaultNightSpacingTokens else DefaultDaySpacingTokens
            }
        }
    }
    
    /**
     * Get typography tokens (same across all brands/themes, but included for consistency).
     */
    fun getTypographyTokens(brand: String, darkTheme: Boolean): Any {
        return when {
            brand.equals("B", ignoreCase = true) || brand.equals("Luxury", ignoreCase = true) -> {
                if (darkTheme) LuxuryNightTypographyTokens else LuxuryDayTypographyTokens
            }
            brand.equals("C", ignoreCase = true) || brand.equals("Performance", ignoreCase = true) -> {
                if (darkTheme) PerformanceNightTypographyTokens else PerformanceDayTypographyTokens
            }
            else -> {
                if (darkTheme) DefaultNightTypographyTokens else DefaultDayTypographyTokens
            }
        }
    }
    
    /**
     * Get border radius tokens (same across all brands/themes, but included for consistency).
     */
    fun getBorderRadiusTokens(brand: String, darkTheme: Boolean): Any {
        return when {
            brand.equals("B", ignoreCase = true) || brand.equals("Luxury", ignoreCase = true) -> {
                if (darkTheme) LuxuryNightBorderRadiusTokens else LuxuryDayBorderRadiusTokens
            }
            brand.equals("C", ignoreCase = true) || brand.equals("Performance", ignoreCase = true) -> {
                if (darkTheme) PerformanceNightBorderRadiusTokens else PerformanceDayBorderRadiusTokens
            }
            else -> {
                if (darkTheme) DefaultNightBorderRadiusTokens else DefaultDayBorderRadiusTokens
            }
        }
    }
}
'''
        return kotlin

    # ===== XML OUTPUT GENERATION =====

    def generate_xml_colors(self, colors: Dict[str, str]) -> str:
        """Generate colors.xml."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- COLOR TOKENS - Generated from design tokens -->\n\n'
        
        for name, value in sorted(colors.items()):
            # Android color resources cannot contain gradients - extract hex color or skip
            if isinstance(value, str) and "linear-gradient" in value.lower():
                # Extract first hex color from gradient (e.g., "linear-gradient(... #1A1A1A95 ...)" -> "#1A1A1A95")
                hex_match = re.search(r'#([0-9A-Fa-f]{6,8})', value)
                if hex_match:
                    # Use the first hex color found in the gradient
                    extracted_color = "#" + hex_match.group(1)
                    xml += f'    <color name="{self._to_snake_case(name)}">{extracted_color}</color>\n'
                else:
                    # Skip gradient colors that can't be parsed
                    continue
            elif isinstance(value, str) and value.startswith("#"):
                # Valid hex color
                xml += f'    <color name="{self._to_snake_case(name)}">{value}</color>\n'
            else:
                # Skip invalid color values
                continue
        
        xml += '</resources>\n'
        return xml

    def generate_xml_radius(self, radius: Dict[str, int]) -> str:
        """Generate radius.xml for border radius tokens."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- BORDER RADIUS TOKENS - Corner rounding values -->\n\n'
        for name in sorted(radius.keys(), key=lambda x: int(x) if x.isdigit() else 999):
            value = radius[name]
            # For numeric names, use them directly without the spacing_ prefix
            resource_name = name if name.isdigit() else self._to_snake_case(name)
            xml += f'    <dimen name="border_radius_{resource_name}">{value}dp</dimen>\n'
        xml += '</resources>\n'
        return xml

    def generate_xml_dimens(self, spacing: Dict[str, int], border_width: Dict[str, str] = None) -> str:
        """Generate dimens.xml (Android convention for spacing and border widths)."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- SPACING TOKENS - 4pt grid system - Organized by token name suffix -->\n\n'
        
        # Extract numeric suffix from token name for grouping
        def get_sort_key(item):
            name, value = item
            # Extract numeric part from name (e.g., "spacing-2" -> 2, "compact-16" -> 16)
            parts = name.split('-')
            if parts[-1].isdigit():
                suffix_num = int(parts[-1])
            else:
                suffix_num = 999
            return (suffix_num, name)
        
        sorted_spacing = sorted(spacing.items(), key=get_sort_key)
        
        last_suffix = None
        for name, value in sorted_spacing:
            suffix = name.split('-')[-1]
            suffix_num = int(suffix) if suffix.isdigit() else 999
            
            # Add comment header for each new token suffix group
            if suffix_num != last_suffix:
                if last_suffix is not None:
                    xml += '\n'
                xml += f'    <!-- {suffix} (variants: spacing, compact, spacious) -->\n'
                last_suffix = suffix_num
            
            xml += f'    <dimen name="{self._to_snake_case(name)}">{value}dp</dimen>\n'
        
        # Add border width tokens
        if border_width:
            xml += '\n    <!-- BORDER WIDTH TOKENS -->\n\n'
            for name, value in sorted(border_width.items()):
                xml += f'    <dimen name="border_{self._to_snake_case(name)}">{value}</dimen>\n'
        
        xml += '</resources>\n'
        return xml

    def generate_xml_styles(self, typography: Dict[str, Dict]) -> str:
        """Generate styles.xml (typography)."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- TYPOGRAPHY TOKENS - Font sizes, line heights, font weights -->\n\n'
        
        # Font Sizes
        if typography["fontSize"]:
            xml += '    <!-- Font Sizes (sp) -->\n'
            for name in sorted(typography["fontSize"].keys(), key=lambda x: int(x) if x.isdigit() else 999):
                value = typography["fontSize"][name]
                xml += f'    <dimen name="font_size_{self._to_snake_case(name)}">{value}sp</dimen>\n'
            xml += '\n'
        else:
            xml += '    <!-- Font Sizes (sp) -->\n'
            # Fallback
            for i in range(11):
                xml += f'    <dimen name="font_size_{i}">12sp</dimen>  <!-- Placeholder -->\n'
            xml += '\n'
        
        # Line Heights
        if typography["lineHeight"]:
            xml += '    <!-- Line Heights (sp) -->\n'
            for name in sorted(typography["lineHeight"].keys(), key=lambda x: int(x) if x.isdigit() else 999):
                value = typography["lineHeight"][name]
                xml += f'    <dimen name="line_height_{self._to_snake_case(name)}">{value}sp</dimen>\n'
            xml += '\n'
        else:
            xml += '    <!-- Line Heights (sp) -->\n'
            # Fallback
            for i in range(5):
                xml += f'    <dimen name="line_height_{i}">20sp</dimen>  <!-- Placeholder -->\n'
            xml += '\n'
        
        # Font Weights
        xml += '    <!-- Font Weights -->\n'
        weights = typography["fontWeight"] if typography["fontWeight"] else {
            "light": 300,
            "regular": 400,
            "medium": 500,
            "semibold": 600,
            "bold": 700
        }
        for name, weight in sorted(weights.items()):
            xml += f'    <integer name="font_weight_{self._to_snake_case(name)}">{weight}</integer>\n'
        
        xml += '</resources>\n'
        return xml

    def generate_xml_typography_unified(self, typography: Dict[str, Dict], letter_spacing: Dict[str, Dict] = None, text_case: Dict[str, str] = None) -> str:
        """Generate unified typography.xml combining font sizes, line heights, weights, letter spacing, text case, and font families."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- COMPREHENSIVE TYPOGRAPHY TOKENS -->\n'
        xml += '    <!-- Combines font sizes, line heights, font weights, letter spacing, text case, and font families -->\n\n'
        
        # Font Families and Letter Spacing from Typography compositions
        xml += '    <!-- ========== TYPOGRAPHY COMPOSITIONS (font families, letter spacing) ========== -->\n'
        if typography.get("compositions"):
            for comp_name, comp_value in sorted(typography["compositions"].items()):
                if isinstance(comp_value, dict):
                    resource_name = self._to_snake_case(comp_name)
                    
                    # Generate font family string
                    if "fontFamily" in comp_value:
                        font_family = comp_value["fontFamily"]
                        xml += f'    <string name="typography_{resource_name}_font_family">{font_family}</string>\n'
                    
                    # Generate letter spacing string (for reference - Android letterSpacing doesn't support resources in XML)
                    # These will be used in TextAppearance styles
                    if "letterSpacing" in comp_value:
                        letter_spacing = comp_value["letterSpacing"]
                        # Store as string for reference (will be used in styles.xml)
                        xml += f'    <string name="typography_{resource_name}_letter_spacing">{letter_spacing}</string>\n'
        xml += '\n'
        
        # Font Sizes
        xml += '    <!-- ========== FONT SIZES ========== -->\n'
        if typography.get("fontSize"):
            for name in sorted(typography["fontSize"].keys(), key=lambda x: int(x) if x.isdigit() else 999):
                value = typography["fontSize"][name]
                # For numeric names, use them directly without the spacing_ prefix
                resource_name = name if name.isdigit() else self._to_snake_case(name)
                xml += f'    <dimen name="font_size_{resource_name}">{value}sp</dimen>\n'
        xml += '\n'
        
        # Line Heights
        xml += '    <!-- ========== LINE HEIGHTS ========== -->\n'
        if typography.get("lineHeight"):
            for name in sorted(typography["lineHeight"].keys(), key=lambda x: int(x) if x.isdigit() else 999):
                value = typography["lineHeight"][name]
                # For numeric names, use them directly without the spacing_ prefix
                resource_name = name if name.isdigit() else self._to_snake_case(name)
                xml += f'    <dimen name="line_height_{resource_name}">{value}sp</dimen>\n'
        xml += '\n'
        
        # Font Weights
        xml += '    <!-- ========== FONT WEIGHTS ========== -->\n'
        weights = typography.get("fontWeight") if typography.get("fontWeight") else {
            "light": 300,
            "regular": 400,
            "medium": 500,
            "semibold": 600,
            "bold": 700
        }
        for name, weight in sorted(weights.items()):
            xml += f'    <integer name="font_weight_{self._to_snake_case(name)}">{weight}</integer>\n'
        xml += '\n'
        
        # Letter Spacing (from Typography compositions - already handled above)
        # Note: Android letterSpacing attribute doesn't support resource references in XML,
        # so these are generated as strings for reference/documentation
        # They should be used programmatically or via TextAppearance styles
        
        # Text Case
        if text_case:
            xml += '    <!-- ========== TEXT CASE ========== -->\n'
            for name, value in sorted(text_case.items()):
                xml += f'    <string name="text_case_{self._to_snake_case(name)}">{value}</string>\n'
            xml += '\n'
        
        xml += '</resources>\n'
        return xml

    def generate_xml_attrs(self, accessibility: Dict[str, str]) -> str:
        """Generate attrs.xml (accessibility color tokens)."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- ACCESSIBILITY TOKENS - WCAG AA compliant colors, focus indicators, high contrast -->\n\n'
        
        # WCAG Text Pairs (white/black text on colored backgrounds)
        wcag_pairs = {k: v for k, v in accessibility.items() if 'wcag' in k.lower()}
        if wcag_pairs:
            xml += '    <!-- WCAG AA Compliant Text Pairs -->\n'
            for name, value in sorted(wcag_pairs.items()):
                clean_name = name.replace('-', '_').replace('wcag_aa_text_on_', 'text_on_').lower()
                xml += f'    <color name="accessibility_{clean_name}">{value}</color>\n'
            xml += '\n'
        
        # Focus Indicators
        focus_items = {k: v for k, v in accessibility.items() if 'focus' in k.lower()}
        if focus_items:
            xml += '    <!-- Focus Indicators (for keyboard navigation) -->\n'
            for name, value in sorted(focus_items.items()):
                clean_name = name.replace('-', '_').lower()
                xml += f'    <color name="accessibility_{clean_name}">{value}</color>\n'
            xml += '\n'
        
        # High Contrast Mode
        contrast_items = {k: v for k, v in accessibility.items() if 'high' in k.lower() or 'contrast' in k.lower()}
        if contrast_items:
            xml += '    <!-- High Contrast Mode (for accessibility) -->\n'
            for name, value in sorted(contrast_items.items()):
                clean_name = name.replace('-', '_').lower()
                xml += f'    <color name="accessibility_{clean_name}">{value}</color>\n'
        
        # Catch any remaining tokens
        used_keys = set(wcag_pairs.keys()) | set(focus_items.keys()) | set(contrast_items.keys())
        remaining = {k: v for k, v in accessibility.items() if k not in used_keys}
        if remaining:
            xml += '\n    <!-- Other Accessibility Tokens -->\n'
            for name, value in sorted(remaining.items()):
                clean_name = name.replace('-', '_').lower()
                xml += f'    <color name="accessibility_{clean_name}">{value}</color>\n'
        
        xml += '</resources>\n'
        return xml

    def generate_xml_animations(self, motion: Dict[str, Any]) -> str:
        """Generate animations.xml (motion tokens)."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- MOTION TOKENS - Durations, easing functions, and transitions -->\n\n'
        
        # Durations
        xml += '    <!-- Durations (milliseconds) -->\n'
        if "duration" in motion:
            for name, token_def in motion["duration"].items():
                if isinstance(token_def, dict) and "value" in token_def:
                    xml += f'    <integer name="motion_duration_{self._to_snake_case(name)}">{token_def["value"]}</integer>\n'
        else:
            # Fallback
            xml += '    <integer name="motion_duration_short">100</integer>  <!-- Placeholder -->\n'
            xml += '    <integer name="motion_duration_standard">300</integer>  <!-- Placeholder -->\n'
            xml += '    <integer name="motion_duration_slow">500</integer>  <!-- Placeholder -->\n'
        
        # Easing
        xml += '\n    <!-- Easing Functions -->\n'
        if "easing" in motion:
            for name, token_def in motion["easing"].items():
                if isinstance(token_def, dict) and "value" in token_def:
                    easing_value = token_def["value"]
                    xml += f'    <string name="motion_easing_{self._to_snake_case(name)}">{easing_value}</string>\n'
        else:
            xml += '    <string name="motion_easing_default">cubic-bezier(0.25, 0.46, 0.45, 0.94)</string>  <!-- Placeholder -->\n'
            xml += '    <string name="motion_easing_entrance">cubic-bezier(0.34, 1.56, 0.64, 1)</string>  <!-- Placeholder -->\n'
        
        # Transitions
        xml += '\n    <!-- Transitions (combined duration + easing) -->\n'
        if "transition" in motion:
            for name, token_def in motion["transition"].items():
                if isinstance(token_def, dict) and "value" in token_def:
                    transition_value = token_def["value"]
                    # Resolve template syntax in transitions
                    if isinstance(transition_value, str):
                        transition_value = self.resolve_reference(transition_value)
                        # If still contains template syntax, use resolved values
                        if '{' in transition_value:
                            # Try to extract and resolve individual parts
                            # For now, use a simple fallback
                            transition_value = transition_value.replace('{motion.duration.fast}', '150ms')
                            transition_value = transition_value.replace('{motion.duration.standard}', '300ms')
                            transition_value = transition_value.replace('{motion.duration.slow}', '500ms')
                            transition_value = transition_value.replace('{motion.easing.smooth}', 'cubic-bezier(0.4, 0, 0.2, 1)')
                            transition_value = transition_value.replace('{motion.easing.default}', 'cubic-bezier(0.25, 0.46, 0.45, 0.94)')
                            transition_value = transition_value.replace('{motion.easing.entrance}', 'cubic-bezier(0.34, 1.56, 0.64, 1)')
                            transition_value = transition_value.replace('{motion.easing.exit}', 'cubic-bezier(0.66, 0, 0.66, 0.07)')
                    xml += f'    <string name="motion_transition_{self._to_snake_case(name)}">{transition_value}</string>\n'
        
        xml += '</resources>\n'
        return xml

    def generate_xml_text_case(self, text_case: Dict[str, str]) -> str:
        """Generate text-case.xml for text transformation tokens."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- TEXT CASE TOKENS - Text transformation values -->\n\n'
        for name, value in sorted(text_case.items()):
            xml += f'    <string name="text_case_{self._to_snake_case(name)}">{value}</string>\n'
        xml += '</resources>\n'
        return xml

    def generate_xml_letter_spacing(self, letter_spacing: Dict[str, Dict]) -> str:
        """Generate letter-spacing.xml for letter spacing tokens."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- LETTER SPACING TOKENS - Fine-grained typography control -->\n\n'
        
        for category, tokens in sorted(letter_spacing.items()):
            xml += f'    <!-- {category.capitalize()} -->\n'
            if isinstance(tokens, dict):
                for name, token_def in sorted(tokens.items()):
                    if isinstance(token_def, dict) and "value" in token_def:
                        xml += f'    <dimen name="letter_spacing_{self._to_snake_case(category)}_{self._to_snake_case(name)}">{token_def["value"]}em</dimen>\n'
            xml += '\n'
        
        xml += '</resources>\n'
        return xml

    def generate_xml_layout(self, layout: Dict[str, Dict]) -> str:
        """Generate layout.xml for layout tokens (breakpoints, spacing modes)."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- LAYOUT TOKENS - Breakpoints, spacing modes, touch targets -->\n\n'
        
        for category, tokens in sorted(layout.items()):
            xml += f'    <!-- {category.capitalize()} -->\n'
            if isinstance(tokens, dict):
                for name, token_def in sorted(tokens.items()):
                    if isinstance(token_def, dict) and "value" in token_def:
                        value = token_def["value"]
                        xml += f'    <dimen name="layout_{self._to_snake_case(category)}_{self._to_snake_case(name)}">{value}dp</dimen>\n'
            xml += '\n'
        
        xml += '</resources>\n'
        return xml

    def generate_xml_platforms(self, platforms: Dict[str, Dict]) -> str:
        """Generate platforms.xml for platform-specific tokens."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- PLATFORM-SPECIFIC TOKENS - Android, QNX, Web configurations -->\n\n'
        
        for platform, tokens in sorted(platforms.items()):
            xml += f'    <!-- {platform.upper()} Platform -->\n'
            if isinstance(tokens, dict):
                for name, token_def in sorted(tokens.items()):
                    if isinstance(token_def, dict):
                        # Only extract the "value" key, ignore "type" and other metadata
                        if "value" in token_def:
                            value = token_def["value"]
                            xml += f'    <string name="platform_{self._to_snake_case(platform)}_{self._to_snake_case(name)}">{value}</string>\n'
                    elif isinstance(token_def, (str, int, float)):
                        # Direct value (not wrapped in dict)
                        xml += f'    <string name="platform_{self._to_snake_case(platform)}_{self._to_snake_case(name)}">{token_def}</string>\n'
            xml += '\n'
        
        xml += '</resources>\n'
        return xml

    def generate_xml_interactions(self, interactions: Dict[str, Dict], colors: Dict[str, str] = None) -> str:
        """Generate interactions.xml for state tokens."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- INTERACTION STATE TOKENS - Hover, active, focus, disabled, etc. -->\n\n'
        
        # Helper to resolve color references
        def resolve_color_value(value_str):
            """Resolve color reference to hex value."""
            if isinstance(value_str, str):
                # Check if it's already a hex color
                if value_str.startswith("#"):
                    return value_str
                # Try to resolve as reference
                resolved = self.resolve_reference(value_str)
                # If still contains template syntax, try to find in colors dict
                if colors and '{' in resolved:
                    # Extract color path from template syntax
                    import re
                    matches = re.findall(r'\{([^}]+)\}', resolved)
                    for match in matches:
                        # Try to find matching color key
                        color_key = match.replace('.', '_').replace('-', '_')
                        # Search for matching color
                        for color_name, color_value in colors.items():
                            if color_key.lower() in color_name.lower() or color_name.lower().endswith(color_key.lower()):
                                return color_value
                # If resolved is a hex color, return it
                if resolved.startswith("#"):
                    return resolved
                # Otherwise return original if no match found
                return value_str
            return value_str
        
        for state_name, state_def in sorted(interactions.items()):
            xml += f'    <!-- {state_name.capitalize()} State -->\n'
            if isinstance(state_def, dict):
                for property_name, property_def in sorted(state_def.items()):
                    if isinstance(property_def, dict) and "value" in property_def:
                        value = property_def["value"]
                        full_name = f"interaction_{self._to_snake_case(state_name)}_{self._to_snake_case(property_name)}"
                        
                        # Resolve value if it's a string with references
                        if isinstance(value, str):
                            value = self.resolve_reference(value)
                        
                        # Determine resource type
                        if isinstance(value, str) and value.startswith("#"):
                            xml += f'    <color name="{full_name}">{value}</color>\n'
                        elif isinstance(value, str) and ("color" in property_name.lower() or "background" in property_name.lower() or "border" in property_name.lower() or "text" in property_name.lower()):
                            # Try to resolve as color
                            resolved_color = resolve_color_value(value)
                            if resolved_color and resolved_color.startswith("#"):
                                xml += f'    <color name="{full_name}">{resolved_color}</color>\n'
                            elif isinstance(value, str) and '{' in value:
                                # Still has template syntax - try one more resolution pass
                                final_value = self.resolve_reference(value)
                                if final_value.startswith("#"):
                                    xml += f'    <color name="{full_name}">{final_value}</color>\n'
                                else:
                                    # Fallback to string if can't resolve
                                    xml += f'    <string name="{full_name}">{value}</string>\n'
                            else:
                                # Fallback to string if can't resolve
                                xml += f'    <string name="{full_name}">{value}</string>\n'
                        elif isinstance(value, (int, float)):
                            # Use dimen for numeric values (opacity, delta, etc.)
                            xml += f'    <dimen name="{full_name}">{value}dp</dimen>\n'
                        else:
                            xml += f'    <string name="{full_name}">{value}</string>\n'
            xml += '\n'
        
        xml += '</resources>\n'
        return xml

    def generate_xml_components(self, components: Dict[str, Dict]) -> str:
        """Generate components.xml for component-specific tokens."""
        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<resources>\n'
        xml += '    <!-- COMPONENT TOKENS - Buttons, Cards, Notifications, Forms -->\n\n'
        
        for component_name, component_def in sorted(components.items()):
            xml += f'    <!-- {component_name.capitalize()} Component -->\n'
            
            if isinstance(component_def, dict):
                for variant_name, variant_def in sorted(component_def.items()):
                    if isinstance(variant_def, dict):
                        for property_name, property_def in sorted(variant_def.items()):
                            # Sanitize names: replace hyphens with underscores for valid Android resource names
                            safe_component_name = self._to_snake_case(component_name)
                            safe_variant_name = self._to_snake_case(variant_name)
                            safe_property_name = self._to_snake_case(property_name)
                            
                            # Skip type properties (they're just metadata)
                            if property_name.endswith("_type") or property_name == "type":
                                if isinstance(property_def, str):
                                    full_name = f"component_{safe_component_name}_{safe_variant_name}_{safe_property_name}"
                                    xml += f'    <string name="{full_name}">{property_def}</string>\n'
                                continue
                            
                            if isinstance(property_def, dict) and "value" in property_def:
                                value = property_def["value"]
                                full_name = f"component_{safe_component_name}_{safe_variant_name}_{safe_property_name}"
                                
                                # Check for JSON-like strings BEFORE resolving (they're not valid Android resources)
                                # These are composition tokens that contain JSON-like structures - not valid Android XML
                                value_str = str(value) if value else ""
                                is_json_like = False
                                if isinstance(value, str) or (isinstance(value, (dict, list))):
                                    # Convert to string for checking
                                    if not isinstance(value, str):
                                        value_str = str(value)
                                    else:
                                        value_str = value
                                    
                                    value_lower = value_str.lower()
                                    # Check for JSON-like patterns
                                    is_json_like = (
                                        value_str.strip().startswith("{") or 
                                        value_str.strip().startswith("'") or
                                        ("{" in value_str and "'" in value_str and ":" in value_str) or  # {'key': 'value'}
                                        ("':" in value_str and value_str.count("'") >= 2) or
                                        ('{"' in value_str) or
                                        ("'fill'" in value_lower) or
                                        ("'fill':" in value_lower) or
                                        ("'textcolor':" in value_lower) or
                                        ("'padding':" in value_lower) or
                                        ("'borderradius':" in value_lower) or
                                        (value_str.count("'") >= 2 and ":" in value_str)  # Multiple quoted keys
                                    )
                                
                                if is_json_like:
                                    # Convert to simple identifier string (skip JSON-like component definitions)
                                    xml += f'    <string name="{full_name}">{safe_component_name}_{safe_variant_name}_{safe_property_name}</string>\n'
                                    continue
                                
                                # Resolve value if it's a string with references (only if not JSON-like)
                                if isinstance(value, str):
                                    value = self.resolve_reference(value)
                                
                                # Double-check after resolution
                                if isinstance(value, str) and (value.strip().startswith("{") or "'fill':" in value):
                                    xml += f'    <string name="{full_name}">{safe_component_name}_{safe_variant_name}_{safe_property_name}</string>\n'
                                    continue
                                elif isinstance(value, str) and value.startswith("#"):
                                    xml += f'    <color name="{full_name}">{value}</color>\n'
                                elif isinstance(value, (int, float)):
                                    xml += f'    <dimen name="{full_name}">{value}dp</dimen>\n'
                                else:
                                    xml += f'    <string name="{full_name}">{value}</string>\n'
                            elif isinstance(property_def, str):
                                # Direct string value without "value" key
                                # Sanitize names: replace hyphens with underscores for valid Android resource names
                                safe_component_name = self._to_snake_case(component_name)
                                safe_variant_name = self._to_snake_case(variant_name)
                                safe_property_name = self._to_snake_case(property_name)
                                full_name = f"component_{safe_component_name}_{safe_variant_name}_{safe_property_name}"
                                # Skip JSON-like strings
                                is_json_like = (property_def.strip().startswith("{") or 
                                              property_def.strip().startswith("'") or
                                              ("':" in property_def and "'" in property_def) or
                                              ('{"' in property_def) or
                                              ("{'fill'" in property_def))
                                if is_json_like:
                                    xml += f'    <string name="{full_name}">{safe_component_name}_{safe_variant_name}_{safe_property_name}</string>\n'
                                else:
                                    xml += f'    <string name="{full_name}">{property_def}</string>\n'
            xml += '\n'
        
        xml += '</resources>\n'
        return xml

    # ===== CSS OUTPUT GENERATION =====

    def generate_css_tokens(self, tokens: Dict[str, Any]) -> str:
        """Generate comprehensive CSS custom properties file."""
        css = '/* Design Tokens - CSS Custom Properties */\n'
        css += '/* Generated from design tokens with mode/theme support */\n\n'
        css += ':root {\n'
        
        # Colors
        css += '\n  /* ========== COLORS ========== */\n'
        for name, value in sorted(tokens["colors"].items()):
            css_var = f'  --{self._to_kebab_case(name)}: {value};\n'
            css += css_var
        
        # Spacing
        css += '\n  /* ========== SPACING ========== */\n'
        for name, value in sorted(tokens["spacing"].items()):
            css += f'  --spacing-{self._to_kebab_case(name)}: {value}px;\n'
        
        # Typography - Font Sizes
        css += '\n  /* ========== TYPOGRAPHY - FONT SIZES ========== */\n'
        if tokens["typography"].get("fontSize"):
            for name, value in sorted(tokens["typography"]["fontSize"].items()):
                css += f'  --font-size-{self._to_kebab_case(name)}: {value}px;\n'
        
        # Typography - Line Heights
        css += '\n  /* ========== TYPOGRAPHY - LINE HEIGHTS ========== */\n'
        if tokens["typography"].get("lineHeight"):
            for name, value in sorted(tokens["typography"]["lineHeight"].items()):
                css += f'  --line-height-{self._to_kebab_case(name)}: {value}px;\n'
        
        # Typography - Font Weights
        css += '\n  /* ========== TYPOGRAPHY - FONT WEIGHTS ========== */\n'
        if tokens["typography"].get("fontWeight"):
            for name, value in sorted(tokens["typography"]["fontWeight"].items()):
                css += f'  --font-weight-{self._to_kebab_case(name)}: {value};\n'
        
        # Border Radius
        css += '\n  /* ========== BORDER RADIUS ========== */\n'
        for name, value in sorted(tokens["radius"].items()):
            css += f'  --border-radius-{self._to_kebab_case(name)}: {value}px;\n'
        
        # Border Width
        css += '\n  /* ========== BORDER WIDTH ========== */\n'
        if tokens.get("border_width"):
            for name, value in sorted(tokens["border_width"].items()):
                css += f'  --border-width-{self._to_kebab_case(name)}: {value}px;\n'
        
        # Elevation
        css += '\n  /* ========== ELEVATION ========== */\n'
        if tokens.get("elevation"):
            for name, value in sorted(tokens["elevation"].items()):
                if isinstance(value, dict) and "value" in value:
                    shadow_val = value["value"]
                    if isinstance(shadow_val, dict):
                        blur = shadow_val.get("blur", 4)
                        css += f'  --elevation-{self._to_kebab_case(name)}: {blur}px;\n'
                    else:
                        css += f'  --elevation-{self._to_kebab_case(name)}: {value}px;\n'
                else:
                    css += f'  --elevation-{self._to_kebab_case(name)}: {value}px;\n'
        
        # Motion - Durations
        css += '\n  /* ========== MOTION - DURATIONS ========== */\n'
        if tokens.get("motion") and "duration" in tokens["motion"]:
            for name, token_def in sorted(tokens["motion"]["duration"].items()):
                if isinstance(token_def, dict) and "value" in token_def:
                    css += f'  --motion-duration-{self._to_kebab_case(name)}: {token_def["value"]}ms;\n'
        
        # Motion - Easing
        css += '\n  /* ========== MOTION - EASING ========== */\n'
        if tokens.get("motion") and "easing" in tokens["motion"]:
            for name, token_def in sorted(tokens["motion"]["easing"].items()):
                if isinstance(token_def, dict) and "value" in token_def:
                    css += f'  --motion-easing-{self._to_kebab_case(name)}: {token_def["value"]};\n'
        
        # Accessibility
        css += '\n  /* ========== ACCESSIBILITY ========== */\n'
        for name, value in sorted(tokens["accessibility"].items()):
            css += f'  --accessibility-{self._to_kebab_case(name)}: {value};\n'
        
        # Interactions
        css += '\n  /* ========== INTERACTIONS ========== */\n'
        if tokens.get("interactions"):
            for state_name, state_def in sorted(tokens["interactions"].items()):
                if isinstance(state_def, dict):
                    for property_name, property_def in sorted(state_def.items()):
                        if isinstance(property_def, dict) and "value" in property_def:
                            value = property_def["value"]
                            css_var_name = f'--interaction-{self._to_kebab_case(state_name)}-{self._to_kebab_case(property_name)}'
                            if isinstance(value, str) and value.startswith("#"):
                                css += f'  {css_var_name}: {value};\n'
                            elif isinstance(value, (int, float)):
                                css += f'  {css_var_name}: {value}px;\n'
                            else:
                                css += f'  {css_var_name}: {value};\n'
        
        css += '}\n'
        return css

    def _to_kebab_case(self, name: str) -> str:
        """Convert camelCase/snake_case to kebab-case."""
        # First convert to snake_case, then replace underscores with hyphens
        snake = self._to_snake_case(name)
        return snake.replace('_', '-')

    # ===== UTILITY METHODS =====

    def _to_camel_case(self, name: str) -> str:
        """Convert snake_case/kebab-case to valid Kotlin camelCase identifier."""
        # First normalize: replace dashes and underscores with spaces, then split
        normalized = re.sub(r'[-_]', ' ', name)
        components = normalized.split()
        
        if not components:
            return name
        
        # Handle numbers at start by prefixing with underscore
        first = components[0]
        if first and first[0].isdigit():
            first = '_' + first
        
        # Convert to camelCase
        result = first.lower() + ''.join(x.title() for x in components[1:])
        
        # Remove any remaining invalid characters
        result = re.sub(r'[^a-zA-Z0-9_]', '', result)
        
        # Ensure it doesn't start with a number
        if result and result[0].isdigit():
            result = '_' + result
        
        return result if result else name

    def _to_snake_case(self, name: str) -> str:
        """Convert camelCase/mixed to snake_case, replacing hyphens with underscores for valid Android resource names."""
        # First replace hyphens with underscores (Android resource names cannot contain hyphens)
        name = name.replace('-', '_')
        # Then convert camelCase to snake_case
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        result = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        # Android resource names must start with a letter, not a number
        if result and result[0].isdigit():
            result = f"spacing_{result}"
        return result

    # ===== MAIN EXECUTION =====

    def _cleanup_root_files(self):
        """Clean up old root-level token files when using --modes."""
        # Kotlin root files to remove (keep TokenProvider.kt)
        kotlin_root_files = [
            "Color.kt", "Spacing.kt", "Typography.kt", "BorderRadius.kt",
            "Elevation.kt", "Motion.kt", "Accessibility.kt", "Interactions.kt"
        ]
        
        # XML root files to remove
        xml_root_files = [
            "colors.xml", "dimens.xml", "radius.xml", "typography.xml",
            "attrs.xml", "animations.xml", "interactions.xml", "components.xml",
            "layout.xml", "platforms.xml"
        ]
        
        # Remove Kotlin root files
        for filename in kotlin_root_files:
            filepath = self.kotlin_output_path / filename
            if filepath.exists():
                filepath.unlink()
                self.log(f"  Removed old root file: {filename}", "info")
        
        # Remove XML root files
        for filename in xml_root_files:
            filepath = self.xml_output_path / filename
            if filepath.exists():
                filepath.unlink()
                self.log(f"  Removed old root file: {filename}", "info")

    def generate_all_outputs(self, export_modes: bool = True):
        """
        Generate all Kotlin and XML output files.
        
        Args:
            export_modes: If True, export separate files for each brand/theme combination.
                          If False, export only the default combination.
        """
        if export_modes:
            # Clean up old root-level files when using --modes
            self._cleanup_root_files()
            
            # Export all brand/theme combinations
            brands = ["Default", "Performance", "Luxury"]
            themes = ["Day", "Night"]
            
            self.log("="*60, "info")
            self.log("EXPORTING ALL MODE COMBINATIONS", "info")
            self.log("="*60, "info")
            
            for brand in brands:
                for theme in themes:
                    self.log(f"\n📦 Exporting: Brand={brand}, Theme={theme}", "info")
                    self.token_data = {}  # Reset for each combination
                    self.resolved_cache = {}
                    self.unresolved_refs = set()
                    
                    # Load tokens for this combination
                    self.load_all_tokens(brand=brand, theme=theme)
                    all_tokens = self.extract_all_tokens()
                    
                    # Generate outputs with mode suffix
                    mode_suffix = f"{brand.lower()}_{theme.lower()}"
                    self._generate_kotlin_outputs(all_tokens, mode_suffix=mode_suffix)
                    self._generate_xml_outputs(all_tokens, mode_suffix=mode_suffix)
                    self._generate_css_outputs(all_tokens, mode_suffix=mode_suffix)
            
            self.log("\n✅ All mode combinations exported successfully!", "success")
        else:
            # Export only default combination
            self.load_all_tokens(brand="Default", theme="Day")
            all_tokens = self.extract_all_tokens()
            
            self.log("Generating Kotlin outputs...", "info")
            self._generate_kotlin_outputs(all_tokens)
            
            self.log("Generating XML outputs...", "info")
            self._generate_xml_outputs(all_tokens)
            
            self.log("Generating CSS outputs...", "info")
            self._generate_css_outputs(all_tokens)
            
            self.log("✅ All outputs generated successfully!", "success")
            self._print_summary(all_tokens)

    def _generate_kotlin_outputs(self, tokens: Dict[str, Any], mode_suffix: str = None):
        """Generate all Kotlin files."""
        outputs = {
            "Color.kt": self.generate_kotlin_color(tokens["colors"], mode_suffix),
            "Spacing.kt": self.generate_kotlin_spacing(tokens["spacing"], mode_suffix),
            "Typography.kt": self.generate_kotlin_typography(tokens["typography"], mode_suffix),
            "BorderRadius.kt": self.generate_kotlin_radius(tokens["radius"], mode_suffix),
            "Elevation.kt": self.generate_kotlin_elevation(tokens["elevation"], mode_suffix),
            "Motion.kt": self.generate_kotlin_motion(tokens["motion"], mode_suffix),
            "Accessibility.kt": self.generate_kotlin_accessibility(tokens["accessibility"], mode_suffix),
            "Interactions.kt": self.generate_kotlin_interactions(tokens["interactions"], mode_suffix),
        }
        
        # Create mode-specific subdirectory if exporting modes
        output_path = self.kotlin_output_path
        if mode_suffix:
            output_path = self.kotlin_output_path / mode_suffix
            output_path.mkdir(parents=True, exist_ok=True)
        
        for filename, content in outputs.items():
            filepath = output_path / filename
            with open(filepath, 'w') as f:
                f.write(content)
            self.log(f"  Generated {filepath.relative_to(self.kotlin_output_path.parent)}", "success")
        
        # Generate TokenProvider.kt in the root kotlin directory (only once, after all modes)
        if mode_suffix == "performance_night":  # Generate after last mode
            provider_path = self.kotlin_output_path / "TokenProvider.kt"
            with open(provider_path, 'w') as f:
                f.write(self.generate_kotlin_token_provider())
            self.log(f"  Generated {provider_path.relative_to(self.kotlin_output_path.parent)}", "success")

    def _generate_xml_outputs(self, tokens: Dict[str, Any], mode_suffix: str = None):
        """Generate all XML files."""
        outputs = {
            "colors.xml": self.generate_xml_colors(tokens["colors"]),
            "dimens.xml": self.generate_xml_dimens(tokens["spacing"], tokens.get("border_width")),
            "radius.xml": self.generate_xml_radius(tokens["radius"]),
            "typography.xml": self.generate_xml_typography_unified(tokens["typography"], tokens.get("letter_spacing"), tokens.get("text_case")),
            "attrs.xml": self.generate_xml_attrs(tokens["accessibility"]),
            "animations.xml": self.generate_xml_animations(tokens["motion"]),
            "interactions.xml": self.generate_xml_interactions(tokens["interactions"], colors=tokens["colors"]),
            "components.xml": self.generate_xml_components(tokens["components"]),
        }
        
        # Add optional token files if they have content
        if tokens.get("layout"):
            outputs["layout.xml"] = self.generate_xml_layout(tokens["layout"])
        if tokens.get("platforms"):
            outputs["platforms.xml"] = self.generate_xml_platforms(tokens["platforms"])
        
        # Create mode-specific subdirectory if exporting modes
        output_path = self.xml_output_path
        if mode_suffix:
            output_path = self.xml_output_path / mode_suffix
            output_path.mkdir(parents=True, exist_ok=True)
        
        for filename, content in outputs.items():
            filepath = output_path / filename
            with open(filepath, 'w') as f:
                f.write(content)
            self.log(f"  Generated {filepath.relative_to(self.xml_output_path.parent)}", "success")

    def _generate_css_outputs(self, tokens: Dict[str, Any], mode_suffix: str = None):
        """Generate all CSS files."""
        outputs = {
            "tokens.css": self.generate_css_tokens(tokens),
        }
        
        # Create mode-specific subdirectory if exporting modes
        output_path = self.css_output_path
        if mode_suffix:
            output_path = self.css_output_path / mode_suffix
            output_path.mkdir(parents=True, exist_ok=True)
        
        for filename, content in outputs.items():
            filepath = output_path / filename
            with open(filepath, 'w') as f:
                f.write(content)
            self.log(f"  Generated {filepath.relative_to(self.css_output_path.parent)}", "success")

    def _print_summary(self, tokens: Dict[str, Any], mode_suffix: str = None):
        """Print generation summary."""
        mode_info = f" (Mode: {mode_suffix})" if mode_suffix else ""
        print("\n" + "="*60)
        print(f"FULL COVERAGE TOKEN TRANSFORMATION COMPLETE{mode_info}")
        print("="*60)
        print(f"\n📁 Kotlin outputs: {self.kotlin_output_path}")
        print(f"   ├─ Color.kt ({len(tokens['colors'])} colors)")
        print(f"   ├─ Spacing.kt ({len(tokens['spacing'])} tokens)")
        print(f"   ├─ Typography.kt ({sum(len(v) for v in tokens['typography'].values())} tokens)")
        print(f"   ├─ BorderRadius.kt ({len(tokens['radius'])} tokens)")
        print(f"   ├─ Elevation.kt ({len(tokens['elevation'])} tokens)")
        print(f"   ├─ Motion.kt ({len(tokens.get('motion', {}))} groups)")
        print(f"   ├─ Accessibility.kt ({len(tokens['accessibility'])} tokens)")
        print(f"   └─ Interactions.kt ({len(tokens.get('interactions', {}))} state groups)")
        
        print(f"\n📁 XML outputs: {self.xml_output_path}")
        print(f"   ├─ colors.xml ({len(tokens['colors'])} colors)")
        print(f"   ├─ dimens.xml ({len(tokens['spacing'])} spacing values)")
        print(f"   ├─ typography.xml ({sum(len(v) for v in tokens['typography'].values())} typography values)")
        print(f"   ├─ radius.xml ({len(tokens['radius'])} radius values)")
        print(f"   ├─ attrs.xml ({len(tokens['accessibility'])} accessibility values)")
        print(f"   ├─ animations.xml ({len(tokens.get('motion', {}))} motion groups)")
        print(f"   ├─ interactions.xml ({len(tokens.get('interactions', {}))} state groups)")
        print(f"   └─ components.xml ({len(tokens.get('components', {}))} component groups)")
        
        print(f"\n📁 CSS outputs: {self.css_output_path}")
        print(f"   └─ tokens.css (all tokens as CSS custom properties)")
        
        total_tokens = (
            len(tokens['colors']) +
            len(tokens['spacing']) +
            sum(len(v) for v in tokens['typography'].values()) +
            len(tokens.get('elevation', {})) +
            len(tokens.get('motion', {})) +
            len(tokens['accessibility'])
        )
        
        print(f"\n✅ TOTAL TOKENS TRANSFORMED: {total_tokens}+")
        print(f"   ✓ Base tokens loaded")
        print(f"   ✓ Brand and theme tokens loaded")
        print(f"   ✓ All token types extracted")
        print(f"   ✓ Both Kotlin and XML outputs generated")
        print("="*60 + "\n")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 token_transformer_full_coverage.py /path/to/workspace [--modes]")
        print("  --modes: Export separate files for each brand/theme combination")
        sys.exit(1)
    
    base_path = sys.argv[1]
    export_modes = "--modes" in sys.argv
    
    config = TransformerConfig(base_path=base_path, verbose=True)
    transformer = FullCoverageTransformer(config)
    transformer.generate_all_outputs(export_modes=export_modes)


if __name__ == "__main__":
    main()

