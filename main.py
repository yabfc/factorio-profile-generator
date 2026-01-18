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


def construct_profile(data: dict) -> dict:
    default_pressure = (
        data.get("surface-property", {}).get("pressure", {}).get("default_value", 1000)
    )
    planets = get_planets(data.get("planet", {}), default_pressure)
    planets += get_planets(data.get("surface", {}), default_pressure)

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
