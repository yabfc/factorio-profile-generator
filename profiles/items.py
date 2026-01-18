from profiles import Item, FuelItem, HeatCapacityFluids
from profiles.utils import normalize_energy


def get_items(old_items: dict) -> list[Item]:
    out = []
    for id, item in old_items.items():
        if ("hidden" in item and item["hidden"]) or (
            "parameter" in item and item["parameter"]
        ):
            continue
        if item["type"] not in ["item", "fluid"]:
            continue
        out.append(
            Item(
                item["name"], item["type"], item["subgroup"], item.get("stack_size", 0)
            )
        )
    return out


def get_fuels(old_items: dict) -> list[FuelItem]:
    out = []
    for id, item in old_items.items():
        if ("hidden" in item and item["hidden"]) or (
            "parameter" in item and item["parameter"]
        ):
            continue
        if item["type"] not in ["item", "fluid"] or "fuel_category" not in item:
            continue
        burnt_result = None
        if "burnt_result" in item:
            burnt_result = item["burnt_result"]

        out.append(
            FuelItem(
                item["name"],
                item["type"],
                item["subgroup"],
                item.get("stack_size", 0),
                item["fuel_category"],
                normalize_energy(item["fuel_value"]),
                burnt_result,
            )
        )
    return out


def get_heat_capacity(old_fluids: dict) -> dict[str, HeatCapacityFluids]:
    out = {}
    for id, fluid in old_fluids.items():
        if ("hidden" in fluid and fluid["hidden"]) or (
            "parameter" in fluid and fluid["parameter"]
        ):
            continue
        if fluid["type"] not in ["fluid"] or "heat_capacity" not in fluid:
            continue

        out[fluid["name"]] = HeatCapacityFluids(
            fluid["name"],
            normalize_energy(fluid["heat_capacity"]),
            fluid["default_temperature"],
        )
    return out
