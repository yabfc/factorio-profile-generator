from profiles import EffectModule, Planet, Machine, MachineFeature, Modifier
from profiles.utils import get_allowed_planets, normalize_energy


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
    all_effects = ["pollution", "speed", "productivity", "consumption", "quality"]
    for id, machine in old_machines.items():
        # power is always in kW - this cuts kW from the string
        requiredPower = normalize_energy(machine["energy_usage"])
        categories = machine.get("crafting_categories", [])
        categories += machine.get("resource_categories", [])
        tmp = Machine(id, categories, requiredPower, [], True, None)
        if "surface_conditions" in machine:
            tmp.limitations = get_allowed_planets(
                machine["surface_conditions"], planets
            )
        moduleSlots = machine.get("module_slots", 0)

        tmp.features.append(
            MachineFeature(
                "modules", moduleSlots, machine.get("allowed_effects", all_effects)
            )
        )
        if "crafting_categories" in machine:
            tmp.features.append(
                MachineFeature("crafting-speed", 0, [f"crafting-speed-{id}"])
            )
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
        out.append(tmp)

    return (out, effects)
