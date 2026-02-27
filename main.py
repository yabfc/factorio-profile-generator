import json
import sys
import os
from profiles.items import get_fuels, get_heat_capacity, get_items
from profiles.recipes import (
    get_recipes,
    get_recipes_from_other,
    get_recipes_from_resources,
    get_recipes_from_tiles,
)
from profiles.machines import get_machine_effects, get_machines
from profiles.research import get_research
from profiles.validate import validate_recipes, validate_items, validate_machines
from profiles.utils import purge_optional_fields, dump, get_planets
import argparse


def construct_profile(data: dict) -> dict:
    default_pressure = (
        data.get("surface-property", {}).get("pressure", {}).get("default_value", 1000)
    )
    planets = get_planets(data.get("planet", {}), default_pressure)
    planets += get_planets(data.get("surface", {}), default_pressure)

    items = get_items(data["item"], ["rocket-part"])
    items += get_items(data["fluid"], [])
    for cat in [
        "tool",
        "module",
        "ammo",
        "gun",
        "item-with-entity-data",
        "capsule",
        "rail-planner",
        "armor",
        "repair-tool",
        "space-platform-starter-pack",
    ]:
        items += get_items(data.get(cat, {}), [])

    fuels = get_fuels(data["item"])
    fuels += get_fuels(data["fluid"])

    heat_capacity_fluids = get_heat_capacity(data["fluid"])

    recipes = get_recipes(data["recipe"], planets)
    recipes += get_recipes_from_tiles(data["tile"], planets)

    for r in ["resource", "plant", "tree", "fish", "asteroid-chunk"]:
        recipes += get_recipes_from_resources(data.get(r, {}))
    for b in ["boiler", "reactor"]:
        recipes += get_recipes_from_other(data[b], fuels, heat_capacity_fluids, planets)

    effectmodules = get_machine_effects(data["module"])
    research = get_research(data["technology"])

    machines = []
    for part in [
        "furnace",
        "assembling-machine",
        "mining-drill",
        "asteroid-collector",
        "rocket-silo",
        "offshore-pump",
        "boiler",
        "reactor",
    ]:
        tmpmachines, tmpeffectmodules = get_machines(
            data.get(part, {}), planets, effectmodules
        )
        effectmodules += tmpeffectmodules
        machines += tmpmachines

    validate_recipes(recipes)
    validate_items(items, recipes)
    validate_machines(machines, recipes)

    return purge_optional_fields(
        {
            "id": "factorio",
            "name": "Generated Factorio Profile",
            "items": dump(items),
            "recipes": dump(recipes),
            "machines": dump(machines),
            "machineEffects": dump(effectmodules),
            "research": dump(research),
        }
    )


def main():
    parser = argparse.ArgumentParser(
        description="YABFC Profile Generator for Factorio dumps"
    )
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output", default="profile.json")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Could not open file at: '{args.input}'")
        sys.exit(1)
    with open(args.input, "r") as f:
        dump = json.load(f)

    profile = construct_profile(dump)
    with open(args.output, "w") as f:
        json.dump(profile, f, indent=4)


if __name__ == "__main__":
    main()
