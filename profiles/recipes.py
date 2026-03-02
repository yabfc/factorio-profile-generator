from profiles import BaseItemIo, Recipe, Planet, FuelItem, HeatCapacityFluids
from profiles.utils import get_allowed_planets, normalize_energy
import fractions
import copy


def get_recipes_from_resources(resources: dict) -> list[Recipe]:
    out = []
    seen = []
    for id, resource in resources.items():
        if "minable" not in resource or resource.get("type", "") in seen:
            continue
        minable = resource["minable"]
        category = resource.get("category", "basic-solid")
        if resource.get("type", "") in ["tree", "fish"]:
            seen.append(resource["type"])
            id = resource["type"]
            category = "manual-harvest"
        if resource.get("type", "") == "asteroid-chunk":
            category = "asteroid-collector"
        if resource.get("type", "") == "plant":
            category = "manual-harvest"

        tmp = Recipe(id, [], [], minable["mining_time"], category, 10, True, None)
        if "required_fluid" in minable:
            tmp.inp.append(
                BaseItemIo(minable["required_fluid"], minable["fluid_amount"])
            )

        if "results" in minable:
            for result in minable["results"]:
                # TODO what to do with amount_min/max & probability
                amount = (
                    result["amount_min"] if "amount_min" in result else result["amount"]
                )
                tmp.out.append(
                    BaseItemIo(result["name"], amount * result.get("probability", 1))
                )
        elif "result" in minable:
            tmp.out.append(BaseItemIo(minable["result"], 1))
        out.append(tmp)
    return out


def get_recipes_from_tiles(tiles: dict, planets: list[Planet]) -> list[Recipe]:
    # fluids that come from tiles like water, lava, heavy oil etc
    out = []
    fluid_planets = {}
    for id, tile in tiles.items():
        if "fluid" not in tile:
            continue
        planet = tile["subgroup"].split("-")[0]
        fluid = tile["fluid"]
        if fluid not in fluid_planets:
            fluid_planets[fluid] = set()
        fluid_planets[fluid].add(planet)
    for fluid, planets in fluid_planets.items():
        out.append(
            Recipe(
                fluid,
                [],
                [BaseItemIo(fluid, 1200)],
                1,
                "offshore-pump",
                10,
                True,
                [f"planet:{planet}" for planet in planets],
            )
        )
    return out


def get_recipes_from_other(
    buildings: dict,
    fuels: list[FuelItem],
    fluids: dict[str, HeatCapacityFluids],
    planets: list[Planet],
) -> list[Recipe]:
    out = []
    for id, building in buildings.items():
        if id in ["heating-tower"]:
            continue
        recipe_id = ""
        temperature_target = building.get("target_temperature", None)
        if "energy_consumption" in building:
            consumption_str = building["energy_consumption"]
        elif "consumption" in building:
            consumption_str = building["consumption"]
        consumption = normalize_energy(consumption_str)
        fuel_categories = building.get("energy_source", {}).get("fuel_categories", [])

        fluid_out = None
        if building.get("output_fluid_box", {}).get("production_type") == "output":
            fluid_out = BaseItemIo(building["output_fluid_box"]["filter"], 0)
            recipe_id = building["output_fluid_box"]["filter"] + "-"
            if fluid_out.id in fluids and temperature_target:
                fluid = fluids[fluid_out.id]
                temperature_delta = temperature_target - fluid.default_temperature
                fluid_out.amount = consumption // (
                    temperature_delta * fluid.heat_capacity
                )
        fluid_in = None
        if building.get("fluid_box", {}).get("production_type") == "input":
            fluid_in = BaseItemIo(building["fluid_box"]["filter"], 60)
            if fluid_in.id in fluids and temperature_target:
                fluid = fluids[fluid_in.id]
                temperature_delta = temperature_target - fluid.default_temperature
                fluid_in.amount = consumption // (
                    temperature_delta * fluid.heat_capacity
                )

        limitations = None
        if "surface_condition" in building:
            limitations = get_allowed_planets(building["surface_conditions"], planets)
        for fuel in fuels:
            out_items = []
            in_items = []
            if fuel.fuel_category not in fuel_categories:
                continue

            # if an item has a really low fuel value like e.g tree-seeds with 100kJ
            # a boiler would run only for 0.05 seconds. This scales it up so
            duration = fuel.fuel_value / consumption
            f = fractions.Fraction(duration).limit_denominator()
            factor = f.denominator
            duration = int(duration * factor)
            if fluid_in:
                tmp = copy.deepcopy(fluid_in)
                tmp.amount *= duration
                in_items.append(tmp)
            if fluid_out:
                tmp = copy.deepcopy(fluid_out)
                tmp.amount *= duration
                out_items.append(tmp)

            if fuel.burnt_result:
                out_items.append(BaseItemIo(fuel.burnt_result, factor))
                fuel.id = fuel.burnt_result
            out.append(
                Recipe(
                    recipe_id + fuel.id,
                    in_items + [BaseItemIo(fuel.id, factor)],
                    out_items,
                    duration,
                    id,
                    10,
                    True,
                    limitations,
                )
            )

    return out


def get_recipes(old_recipes: dict, planets: list[Planet]) -> list[Recipe]:
    out = []
    for id, recipe in old_recipes.items():
        if "hidden" in recipe and recipe["hidden"]:
            continue

        category = recipe.get("category", "crafting")
        if category == "parameters":
            continue
        duration = recipe.get("energy_required", 1)
        if "-barrel" in id:
            prio = 30
        elif category == "recycling-or-hand-crafting":
            prio = 90
        else:
            prio = 10
        tmp = Recipe(id, [], [], duration, category, prio, True, None)
        if "surface_conditions" in recipe:
            tmp.limitations = get_allowed_planets(recipe["surface_conditions"], planets)
        for ingredient in recipe["ingredients"]:
            tmp.inp.append(BaseItemIo(ingredient["name"], ingredient["amount"]))
        for result in recipe["results"]:
            tmp.out.append(
                BaseItemIo(
                    result["name"], result["amount"] * result.get("probability", 1)
                )
            )
        out.append(tmp)
    return out
