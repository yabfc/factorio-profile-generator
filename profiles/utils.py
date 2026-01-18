from profiles import POWER_FACTORS, Planet
import dataclasses
import re


def normalize_energy(power_str: str) -> int:
    p, unit = re.split(r"(\d+(?:\.\d+)?)", power_str)[1:]
    if unit not in POWER_FACTORS:
        print(f"{power_str}: {unit} does not exist :(")
    return int(float(p) * POWER_FACTORS[unit])


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


def get_allowed_planets(conditions: dict, planets: list[Planet]) -> list[str] | None:
    limitations = []
    for condition in conditions:
        if condition.get("property", "") == "pressure":
            if "min" in condition and "max" in condition:
                pressure_range = range(condition["min"], condition["max"] + 1)
                limitations += [
                    f"planet:{p.id}" for p in planets if p.pressure in pressure_range
                ]
            elif "min" in condition:
                limitations += [
                    f"planet:{p.id}" for p in planets if p.pressure >= condition["min"]
                ]
            elif "max" in condition:
                limitations += [
                    f"planet:{p.id}" for p in planets if p.pressure <= condition["max"]
                ]
    return limitations if len(limitations) != 0 else None


def purge_optional_fields(obj):
    # if limitations is not present, it's an implicit null
    # => we can delete the field when it's null
    if isinstance(obj, dict):
        return {
            k: purge_optional_fields(v)
            for k, v in obj.items()
            if not (k == "limitations" and v is None)
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
