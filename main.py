import json
import sys
import os
from profiles.items import get_fuels, get_heat_capacity, get_items
from profiles.recipes import (
    get_recipes,
    get_recipes_from_other,
    get_recipes_from_ressources,
    get_recipes_from_tiles,
)
from profiles.machines import get_machine_effects, get_machines
from profiles.research import get_research
from profiles.validate import validate_recipes
from profiles.utils import purge_optional_fields, dump, get_planets
from profiles.model import FactorioDataRaw
from pathlib import Path
import argparse
import sys


def construct_profile(data: FactorioDataRaw) -> dict:
    default_pressure = 1000
    if data.surface_property:
        pressure = data.surface_property.get("pressure", None)
        if pressure:
            default_pressure = pressure.default_value

    planets = get_planets(data.planet, default_pressure)
    planets += get_planets(data.surface, default_pressure)

    items = get_items(data["item"])
    items += get_items(data["fluid"])

    fuels = get_fuels(data["item"])
    fuels += get_fuels(data["fluid"])

    heat_capacity_fluids = get_heat_capacity(data["fluid"])

    recipes = get_recipes(data["recipe"], planets)
    recipes += get_recipes_from_ressources(data["resource"])
    recipes += get_recipes_from_ressources(data.get("plant", {}))
    recipes += get_recipes_from_tiles(data["tile"], planets)
    for b in ["boiler", "reactor"]:
        recipes += get_recipes_from_other(data[b], fuels, heat_capacity_fluids, planets)

    effectmodules = get_machine_effects(data["module"])
    research = get_research(data["technology"])

    machines = []
    for part in ["furnace", "assembling-machine", "mining-drill"]:
        if part not in data:
            continue
        tmpmachines, tmpeffectmodules = get_machines(data[part], planets)
        effectmodules += tmpeffectmodules
        machines += tmpmachines

    validate_recipes(recipes)

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
    parser = argparse.ArgumentParser(description="YABFC Profile Generator for Factorio dumps")
    parser.add_argument("-i", "--input", required=True)
    parser.add_argument("-o", "--output", default="out.json")
    parser.add_argument("-k", "--no-validation", action="store_true")
    
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Could not open file at: '{args.input}'")
        sys.exit(1)
    with open(args.input, "r") as f:
        dump = json.load(f)
    if not args.no_validation:
        FactorioDataRaw.model_validate(dump, strict=False)
        print(f"Factorio dump is valid")

    raw_dump = FactorioDataRaw.model_construct(**dump)
    profile = construct_profile(raw_dump)
    with open("out.json", "w") as f:
        json.dump(profile, f, indent=4)


if __name__ == "__main__":
    main()
