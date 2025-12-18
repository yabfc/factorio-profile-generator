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
    inp: list[BaseItemIo]
    out: list[BaseItemIo]
    duration: int
    category: str
    priority: int


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


def get_machine_effects(old_effects: dict) -> list[EffectModule]:
    out = []
    for id, modifier in old_effects.items():
        if not id.split("-")[-1].isdigit():
            id += "-1"
        tmp = EffectModule(id, [], True)
        for eid, effect in modifier["effect"].items():
            if "productivity" in id and eid == "speed":
                tmp.modifiers.append(Modifier(eid, effect, False, True))
            else:
                tmp.modifiers.append(Modifier(eid, effect, False, False))
        out.append(tmp)
    return out


def get_machines(old_machines: dict) -> tuple[list[Machine], list[EffectModule]]:
    out = []
    effects = []
    for id, machine in old_machines.items():
        # power is always in kW - this cuts kW from the string
        requiredPower = int("".join(c for c in machine["energy_usage"] if c.isdigit())) * 1000
        tmp = Machine(id, machine["crafting_categories"], requiredPower, [])
        moduleSlots = 1 if "module_slots" not in machine.keys() else machine["module_slots"]
        tmp.features.append(MachineFeature("modules", moduleSlots, machine["allowed_effects"]))
        tmp.features.append(MachineFeature("crafting-speed",0,[f"crafting-speed-{id}"]))
        out.append(tmp)
        craft_effect = EffectModule(f"crafting-speed-{id}", [Modifier("speed", machine["crafting_speed"], False, True,)], True)
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


def get_recipes(old_recipes: dict) -> list[Recipe]:
    out = []
    for id, recipe in old_recipes.items():
        if "hidden" in recipe.keys() and recipe["hidden"]:
            continue

        category = "default" if "category" not in recipe.keys() else recipe["category"]
        if category == "parameters":
            continue
        duration = 1 if "energy_required" not in recipe.keys() else recipe["energy_required"]
        if "-barrel" in id:
            prio = 30
        else:
            prio = 10
        tmp = Recipe(id, [], [], duration, category, prio)
        for ingredient in recipe["ingredients"]:
            tmp.inp.append(
                BaseItemIo(ingredient["name"], ingredient["type"], ingredient["amount"])
            )
        for result in recipe["results"]:
            tmp.out.append(BaseItemIo(result["name"], result["type"], result["amount"]))
        out.append(tmp)
    return out


def construct_profile(data: dict) -> dict:
    recipes = get_recipes(data["recipe"])
    items = get_items(data["item"])
    effectmodules = get_machine_effects(data["module"])

    machines = []
    for part in ["furnace", "assembling-machine"]:
        if part not in data.keys():
            continue
        tmpmachines, tmpeffectmodules = get_machines(data[part])
        effectmodules += tmpeffectmodules
        machines += tmpmachines
    return {
        "id": "factorio",
        "name": "Generated Factorio Profile",
        "items": [ dataclasses.asdict(e) for e in items],
        "recipes": [ dataclasses.asdict(e) for e in recipes],
        "machines": [ dataclasses.asdict(e) for e in machines],
        "machineEffects": [ dataclasses.asdict(e) for e in effectmodules],
    }


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
