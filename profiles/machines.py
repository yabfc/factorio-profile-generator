from profiles import (
    EffectModule,
    Planet,
    Machine,
    MachineFeature,
    Modifier,
    FixedEffectModule,
    LimitedEffectModule,
)
from profiles.utils import get_allowed_planets, normalize_energy

CONSUMPTION_LIMIT = LimitedEffectModule(
    "consumption-limit",
    [Modifier("consumption", value=0)],
    minValue=0.2,
    maxValue=None,
    hidden=True,
)

# https://lua-api.factorio.com/latest/prototypes/CraftingMachinePrototype.html#energy_source
DEFAULT_DRAIN = FixedEffectModule(
    "idle-default",
    [
        Modifier(
            "consumption",
            0.03333333333333333,
        )
    ],
    hidden=True,
)


def get_machine_effects(old_effects: dict) -> list[EffectModule]:
    out: list[EffectModule] = [CONSUMPTION_LIMIT]
    for id, modifier in old_effects.items():
        if not id.split("-")[-1].isdigit():
            id += "-1"
        tmp = FixedEffectModule(id, [])
        for eid, effect in modifier["effect"].items():
            tmp.modifiers.append(Modifier(eid, effect))
        out.append(tmp)
    return out


def get_allowed_effect_modules(
    allowed_effects: list[str], effect_modules: list[EffectModule]
) -> list[str]:
    out = []
    for module in effect_modules:
        if "crafting-speed" in module.id or module.hidden:
            continue
        used_effects = set([m.id for m in module.modifiers])
        if used_effects.issubset(set(allowed_effects)):
            out.append(module.id)

    return out


def get_machines(
    old_machines: dict, planets: list[Planet], effectModules: list[EffectModule]
) -> tuple[list[Machine], list[EffectModule]]:
    out = []
    effects = []
    all_effects = ["pollution", "speed", "productivity", "consumption", "quality"]
    for id, machine in old_machines.items():
        if machine.get("energy_usage", None):
            requiredPower = normalize_energy(machine["energy_usage"])
        elif machine.get("arm_energy_usage", None):
            requiredPower = normalize_energy(machine["arm_energy_usage"])
        elif machine.get("consumption", None):
            requiredPower = normalize_energy(machine["consumption"])
        elif machine.get("energy_consumption", None):
            requiredPower = normalize_energy(machine["energy_consumption"])
        else:
            print(f"{id} did not have any energy consumption field. Defaulting to 1")
            requiredPower = 1
        if machine.get("passive_energy_usage", None):
            requiredPower += normalize_energy(machine["passive_energy_usage"])

        # https://lua-api.factorio.com/latest/prototypes/CraftingMachinePrototype.html#energy_source
        idle_id = DEFAULT_DRAIN.id
        if machine.get("energy_source", {}).get("drain", None):
            idle_power = normalize_energy(machine["energy_source"]["drain"])
            idle_id = f"idle-{id}"
            effects.append(
                FixedEffectModule(
                    f"idle-{id}",
                    [
                        Modifier(
                            "consumption",
                            idle_power / requiredPower,
                        )
                    ],
                    hidden=True,
                )
            )

        categories = machine.get("crafting_categories", [])
        categories += machine.get("resource_categories", [])
        if len(categories) == 0:
            categories.append(id)
        tmp = Machine(
            id,
            categories,
            requiredPower,
            [MachineFeature("idle", 0, [idle_id], True)],
            True,
            None,
        )
        if "surface_conditions" in machine:
            tmp.limitations = get_allowed_planets(
                machine["surface_conditions"], planets
            )
        moduleSlots = machine.get("module_slots", 0)
        if moduleSlots > 0:
            allowed_effects = machine.get("allowed_effects", all_effects)
            tmp.features.append(
                MachineFeature(
                    "modules",
                    moduleSlots,
                    get_allowed_effect_modules(allowed_effects, effectModules),
                    None,
                )
            )
            tmp.features.append(
                MachineFeature("limit", 0, [CONSUMPTION_LIMIT.id], True)
            )
        if "crafting_categories" in machine:
            tmp.features.append(
                MachineFeature("crafting-speed", 0, [f"crafting-speed-{id}"], True)
            )
            craft_effect = FixedEffectModule(
                f"crafting-speed-{id}",
                [
                    Modifier(
                        "speed",
                        machine["crafting_speed"],
                    )
                ],
                hidden=True,
            )
            effects.append(craft_effect)
        out.append(tmp)

    return (out, effects)
