from xmlrpc.client import boolean
import json
import sys
import os
import dataclasses
from typing import Optional

@dataclasses.dataclass
class BaseItemIo:
    id: str
    type: str
    amount: int


@dataclasses.dataclass
class Recipe:
    id: str
    inp: list[BaseItemIo] = dataclasses.field(metadata={"alias": "in"})
    out: list[BaseItemIo]
    duration: int
    category: str
    priority: int
    available: bool
    limitations: list[str] | None


@dataclasses.dataclass
class Item:
    id: str
    type: str
    category: str
    stackSize: int


@dataclasses.dataclass
class MachineFeature:
    id: str
    itemSlots: int
    effectPerSlot: list[str]


@dataclasses.dataclass
class Machine:
    id: str
    recipeCategories: list[str]
    requiredPower: int
    features: list[MachineFeature]
    available: bool
    limitations: list[str] | None


@dataclasses.dataclass
class Modifier:
    id: str
    value: float
    modifiable: bool
    onlyOutputScales: bool


@dataclasses.dataclass
class EffectModule:
    id: str
    modifiers: list[Modifier]
    perSlot: bool
    available: bool


@dataclasses.dataclass
class Planet:
    id: str
    pressure: int


def get_machine_effects(old_effects: dict) -> list[EffectModule]:
    out = []
    for id, modifier in old_effects.items():
        if not id.split("-")[-1].isdigit():
            id += "-1"
        tmp = EffectModule(id, [], True, True)
        for eid, effect in modifier["effect"].items():
            if "productivity" in id and eid == "speed":
                tmp.modifiers.append(Modifier(eid, effect, False, True))
            else:
                tmp.modifiers.append(Modifier(eid, effect, False, False))
        out.append(tmp)
    return out


def get_machines(
    old_machines: dict, planets: list[Planet]
) -> tuple[list[Machine], list[EffectModule]]:
    out = []
    effects = []
    for id, machine in old_machines.items():
        # power is always in kW - this cuts kW from the string
        requiredPower = (
            int("".join(c for c in machine["energy_usage"] if c.isdigit())) * 1000
        )
        tmp = Machine(id, machine["crafting_categories"], requiredPower, [], True, None)
        if "surface_conditions" in machine.keys():
            for condition in machine["surface_conditions"]:
                if condition.get("property", "") == "pressure":
                    tmp.limitations = get_allowed_planets(condition, planets)
                    break
        moduleSlots = machine.get("module_slots", 1)
        tmp.features.append(
            MachineFeature("modules", moduleSlots, machine["allowed_effects"])
        )
        tmp.features.append(
            MachineFeature("crafting-speed", 0, [f"crafting-speed-{id}"])
        )
        out.append(tmp)
        craft_effect = EffectModule(
            f"crafting-speed-{id}",
            [
                Modifier(
                    "speed",
                    machine["crafting_speed"],
                    False,
                    True,
                )
            ],
            True,
            True,
        )
        effects.append(craft_effect)
    return (out, effects)


def get_items(old_items: dict) -> list[Item]:
    out = []
    for id, item in old_items.items():
        if ("hidden" in item.keys() and item["hidden"]) or (
            "parameter" in item.keys() and item["parameter"]
        ):
            continue
        if item["type"] != "item" and item["type"] != "fluid":
            continue
        out.append(
            Item(item["name"], item["type"], item["subgroup"], item["stack_size"])
        )
    return out


def get_recipes(old_recipes: dict, planets: list[Planet]) -> list[Recipe]:
    out = []
    for id, recipe in old_recipes.items():
        if "hidden" in recipe.keys() and recipe["hidden"]:
            continue

        category = recipe.get("category", "default")
        if category == "parameters":
            continue
        duration = recipe.get("energy_required", 1)
        if "-barrel" in id:
            prio = 30
        else:
            prio = 10
        tmp = Recipe(id, [], [], duration, category, prio, True, None)
        if "surface_conditions" in recipe.keys():
            for condition in recipe["surface_conditions"]:
                if condition.get("property", "") == "pressure":
                    tmp.limitations = get_allowed_planets(condition, planets)
                    break
        for ingredient in recipe["ingredients"]:
            tmp.inp.append(
                BaseItemIo(ingredient["name"], ingredient["type"], ingredient["amount"])
            )
        for result in recipe["results"]:
            tmp.out.append(BaseItemIo(result["name"], result["type"], result["amount"]))
        out.append(tmp)
    return out


def get_allowed_planets(condition: dict, planets: list[Planet]) -> list[str] | None:
    if "min" in condition.keys() and "max" in condition.keys():
        pressure_range = range(condition["min"], condition["max"] + 1)
        return [f"planet:{p.id}" for p in planets if p.pressure in pressure_range]
    elif "min" in condition.keys():
        return [f"planet:{p.id}" for p in planets if p.pressure >= condition["min"]]
    elif "max" in condition.keys():
        return [f"planet:{p.id}" for p in planets if p.pressure <= condition["max"]]
    return None


def get_planets(old_planets: dict, default_pressure: int) -> list[Planet]:
    out = []
    for id, planet in old_planets.items():
        out.append(
            Planet(
                id,
                planet.get("surface_properties", {}).get("pressure", default_pressure),
            )
        )
    return out


def purge_optional_fields(obj):
    # if planetLimitations is not present, it's an implicit null
    # => we can delete the field when it's null
    if isinstance(obj, dict):
        return {
            k: purge_optional_fields(v)
            for k, v in obj.items()
            if not (k == "planetLimitations" and v is None)
        }
    elif isinstance(obj, list):
        return [purge_optional_fields(x) for x in obj]
    return obj

def dump(obj):
    if dataclasses.is_dataclass(obj):
        out = {}
        for f in dataclasses.fields(obj):
            val = getattr(obj, f.name)
            if val is None:
                continue
            key = f.metadata.get("alias", f.name)
            out[key] = dump(val)
        return out
    if isinstance(obj, list):
        return [dump(e) for e in obj]
    if isinstance(obj, dict):
        return {k: dump(v) for k, v in obj.items()}
    return obj

def construct_profile(data: dict) -> dict:
    default_pressure = (
        data.get("surface-property", {}).get("pressure", {}).get("default_value", 1000)
    )
    planets = get_planets(data.get("planet", {}), default_pressure)
    planets += get_planets(data.get("surface", {}), default_pressure)

    recipes = get_recipes(data["recipe"], planets)
    items = get_items(data["item"])
    effectmodules = get_machine_effects(data["module"])

    machines = []
    for part in ["furnace", "assembling-machine"]:
        if part not in data.keys():
            continue
        tmpmachines, tmpeffectmodules = get_machines(data[part], planets)
        effectmodules += tmpeffectmodules
        machines += tmpmachines
    return purge_optional_fields(
        {
            "id": "factorio",
            "name": "Generated Factorio Profile",
            "items": dump(items),
            "recipes": dump(recipes),
            "machines": dump(machines),
            "machineEffects": dump(effectmodules),
        }
    )


def main():
    if len(sys.argv) < 2:
        print("Please specify a dump file")
        sys.exit(1)
    fp = sys.argv[1]
    if not os.path.exists(fp):
        print(f"Could not open file at: '{fp}'")
        sys.exit(1)
    with open(fp, "r") as f:
        dump = json.load(f)
    profile = construct_profile(dump)
    with open("out.json", "w") as f:
        json.dump(profile, f, indent=4)


if __name__ == "__main__":
    main()
