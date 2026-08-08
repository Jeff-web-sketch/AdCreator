"""Parse and edit 0 A.D. XML entity definitions."""

import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class UnitTemplate:
    """Represents a 0 A.D. unit template (XML entity definition)."""

    @classmethod
    def from_file(cls, filepath: Path) -> "UnitTemplate":
        if not filepath.exists():
            raise FileNotFoundError(f"Template file not found: {filepath}")
        
        content = filepath.read_text(encoding="utf-8")
        if not content.strip():
            raise ValueError(f"Empty template file: {filepath}")
        
        return cls.from_string(content, filepath.name)

    @classmethod
    def from_string(cls, xml_str: str, filename: str = "") -> "UnitTemplate":
        if not xml_str.strip():
            raise ValueError("XML string cannot be empty")
        
        try:
            tpl = cls()
            tpl.filename = filename
            tpl.root = ET.fromstring(xml_str)
            tpl.parent_attr = tpl.root.get("parent", "")
            tpl.tree = ET.ElementTree(tpl.root)
            return tpl
        except ET.ParseError as e:
            logger.error(f"Failed to parse XML from {filename}: {e}")
            raise ValueError(f"Invalid XML in {filename}: {e}")

    @classmethod
    def new_blank(cls, parent="template_unit_infantry_melee_swordsman",
              filename="gaia_new_unit.xml") -> "UnitTemplate":
        xml = f'''<?xml version="1.0" encoding="utf-8"?>
<Entity parent="{parent}">
  <Attack/>
  <Cost>
    <Resources>
      <food>50</food>
      <wood>0</wood>
      <stone>0</stone>
      <metal>0</metal>
    </Resources>
  </Cost>
  <Health>
    <Max>100</Max>
  </Health>
  <Identity>
    <Civ>gaia</Civ>
    <GenericName>New Unit</GenericName>
    <SpecificName>New Unit</SpecificName>
    <Classes datatype="tokens"/>
    <VisibleClasses datatype="tokens">Infantry</VisibleClasses>
    <Icon>units/new_unit.png</Icon>
  </Identity>
  <Resistance>
    <Entity>
      <Damage>
        <Hack>0</Hack>
        <Pierce>0</Pierce>
      </Damage>
    </Entity>
  </Resistance>
  <UnitMotion>
    <WalkSpeed>8.5</WalkSpeed>
    <Run>
      <Speed>17.0</Speed>
    </Run>
  </UnitMotion>
  <VisualActor>
    <Actor>units/new_unit.xml</Actor>
  </VisualActor>
</Entity>'''
        return cls.from_string(xml, filename)

    def __init__(self):
        self.tree: Optional[ET.ElementTree] = None
        self.root: Optional[ET.Element] = None
        self.parent_attr = ""
        self.filename = ""

    def _ensure(self, tag):
        el = self.root.find(tag)
        if el is None:
            el = ET.SubElement(self.root, tag)
        return el

    def _get(self, comp, *path):
        el = self.root.find(comp)
        if el is None:
            return ""
        for p in path:
            el = el.find(p)
            if el is None:
                return ""
        return el.text or ""

    def _set(self, comp, *path_and_val):
        *path, val = path_and_val
        el = self._ensure(comp)
        for p in path:
            child = el.find(p)
            if child is None:
                child = ET.SubElement(el, p)
            el = child
        el.text = str(val)

    # ── Properties ──────────────────────────────────────────────────────

    @property
    def parent_template(self): return self.parent_attr
    @parent_template.setter
    def parent_template(self, v): self.parent_attr = v; self.root.set("parent", v)

    @property
    def civ(self): return self._get("Identity", "Civ")
    @civ.setter
    def civ(self, v): self._set("Identity", "Civ", v)

    @property
    def generic_name(self): return self._get("Identity", "GenericName")
    @generic_name.setter
    def generic_name(self, v): self._set("Identity", "GenericName", v)

    @property
    def specific_name(self): return self._get("Identity", "SpecificName")
    @specific_name.setter
    def specific_name(self, v): self._set("Identity", "SpecificName", v)

    @property
    def visible_classes(self):
        el = self.root.find("Identity/VisibleClasses")
        if el is None: return ""
        return el.text or ""
    @visible_classes.setter
    def visible_classes(self, v): self._set("Identity", "VisibleClasses", v)

    @property
    def icon(self): return self._get("Identity", "Icon")
    @icon.setter
    def icon(self, v): self._set("Identity", "Icon", v)

    @property
    def max_health(self): return self._get("Health", "Max")
    @max_health.setter
    def max_health(self, v): self._set("Health", "Max", str(v))

    @property
    def food_cost(self): return self._get("Cost", "Resources", "food")
    @food_cost.setter
    def food_cost(self, v): self._set("Cost", "Resources", "food", str(v))

    @property
    def wood_cost(self): return self._get("Cost", "Resources", "wood")
    @wood_cost.setter
    def wood_cost(self, v): self._set("Cost", "Resources", "wood", str(v))

    @property
    def stone_cost(self): return self._get("Cost", "Resources", "stone")
    @stone_cost.setter
    def stone_cost(self, v): self._set("Cost", "Resources", "stone", str(v))

    @property
    def metal_cost(self): return self._get("Cost", "Resources", "metal")
    @metal_cost.setter
    def metal_cost(self, v): self._set("Cost", "Resources", "metal", str(v))

    @property
    def walk_speed(self): return self._get("UnitMotion", "WalkSpeed")
    @walk_speed.setter
    def walk_speed(self, v): self._set("UnitMotion", "WalkSpeed", str(v))

    @property
    def run_speed(self): return self._get("UnitMotion", "Run", "Speed")
    @run_speed.setter
    def run_speed(self, v): self._set("UnitMotion", "Run", "Speed", str(v))

    @property
    def melee_hack(self): return self._get("Attack", "Melee", "Damage", "Hack")
    @melee_hack.setter
    def melee_hack(self, v): self._set("Attack", "Melee", "Damage", "Hack", str(v))

    @property
    def melee_pierce(self): return self._get("Attack", "Melee", "Damage", "Pierce")
    @melee_pierce.setter
    def melee_pierce(self, v): self._set("Attack", "Melee", "Damage", "Pierce", str(v))

    @property
    def melee_crush(self): return self._get("Attack", "Melee", "Damage", "Crush")
    @melee_crush.setter
    def melee_crush(self, v): self._set("Attack", "Melee", "Damage", "Crush", str(v))

    @property
    def melee_range(self): return self._get("Attack", "Melee", "MaxRange")
    @melee_range.setter
    def melee_range(self, v): self._set("Attack", "Melee", "MaxRange", str(v))

    @property
    def ranged_pierce(self): return self._get("Attack", "Ranged", "Damage", "Pierce")
    @ranged_pierce.setter
    def ranged_pierce(self, v): self._set("Attack", "Ranged", "Damage", "Pierce", str(v))

    @property
    def ranged_hack(self): return self._get("Attack", "Ranged", "Damage", "Hack")
    @ranged_hack.setter
    def ranged_hack(self, v): self._set("Attack", "Ranged", "Damage", "Hack", str(v))

    @property
    def ranged_crush(self): return self._get("Attack", "Ranged", "Damage", "Crush")
    @ranged_crush.setter
    def ranged_crush(self, v): self._set("Attack", "Ranged", "Damage", "Crush", str(v))

    @property
    def ranged_range(self): return self._get("Attack", "Ranged", "MaxRange")
    @ranged_range.setter
    def ranged_range(self, v): self._set("Attack", "Ranged", "MaxRange", str(v))

    @property
    def ranged_repeat(self): return self._get("Attack", "Ranged", "RepeatTime")
    @ranged_repeat.setter
    def ranged_repeat(self, v): self._set("Attack", "Ranged", "RepeatTime", str(v))

    @property
    def hack_armor(self): return self._get("Resistance", "Entity", "Damage", "Hack")
    @hack_armor.setter
    def hack_armor(self, v): self._set("Resistance", "Entity", "Damage", "Hack", str(v))

    @property
    def pierce_armor(self): return self._get("Resistance", "Entity", "Damage", "Pierce")
    @pierce_armor.setter
    def pierce_armor(self, v): self._set("Resistance", "Entity", "Damage", "Pierce", str(v))

    @property
    def actor(self): return self._get("VisualActor", "Actor")
    @actor.setter
    def actor(self, v): self._set("VisualActor", "Actor", v)

    # ── Serialization ────────────────────────────────────────────────────

    def to_string(self) -> str:
        try:
            ET.indent(self.tree, space="  ")
        except AttributeError:
            pass
        body = ET.tostring(self.root, encoding="unicode")
        return '<?xml version="1.0" encoding="utf-8"?>\n' + body

    def save(self, filepath: Path):
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(self.to_string(), encoding="utf-8")