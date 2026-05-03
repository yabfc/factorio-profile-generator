from profiles import (
    Machine,
    Modifier,
    MachineFeature,
    FixedEffectModule,
    EffectModule,
    MODIFIER_TYPES,
)


def add_quality_features(
    quality: dict, machines: list[Machine], effects: list[EffectModule]
) -> tuple[list[Machine], list[EffectModule]]:
    modules = []
    for id, q in quality.items():
        if id == "quality-unknown":
            continue
        for modifier_id in MODIFIER_TYPES:
            modifier = Modifier(modifier_id, 1 + 0.3 * q["level"])
            modules.append(
                FixedEffectModule(
                    f"quality-{id}-{modifier_id}",
                    [modifier],
                    name=id.title(),
                    hidden=True,
                )
            )
    if len(modules) <= len(MODIFIER_TYPES):
        return (machines, effects)

    # only machine speed changes with different quality
    machine_module_ids = [m.id for m in modules if m.id.endswith("speed")]
    used_modules = set(machine_module_ids)
    feature = MachineFeature("quality-tiers", 0, machine_module_ids, True)
    # no drills, asteroid-collector, heating-tower
    for m in machines:
        if "mining-drill" in m.id or m.id in ["asteroid-collector", "heating-tower"]:
            continue
        m.features.append(feature)

    for effect in effects:
        if effect.hidden or len(effect.modifiers) < 1:
            continue
        # we hope and pray that this is the modifier which is affected by quality. There is no clear indication in the source data for data
        modifier = effect.modifiers[0]
        effect.allowedEffects = [m.id for m in modules if m.id.endswith(modifier.id)]
        used_modules |= set(effect.allowedEffects)

    effects += [m for m in modules if m.id in used_modules]
    return (machines, effects)
