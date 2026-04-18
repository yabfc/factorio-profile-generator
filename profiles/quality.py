from profiles import Machine, Modifier, MachineFeature, FixedEffectModule


def add_quality_features(
    quality: dict, machines: list[Machine]
) -> tuple[list[Machine], list[FixedEffectModule]]:
    modules = []
    for id, q in quality.items():
        if id == "quality-unknown":
            continue
        speed = Modifier("speed", 1 + 0.3 * q["level"])
        modules.append(
            FixedEffectModule(f"quality-{id}", [speed], name=id.title(), hidden=True)
        )
    module_ids = [m.id for m in modules]
    # no need to add a single quality feature
    if len(module_ids) <= 1:
        return (machines, [])
    feature = MachineFeature("quality-tiers", 0, module_ids, True)
    # no drills, asteroid-collector, heating-tower
    for m in machines:
        if "mining-drill" in m.id or m.id in ["asteroid-collector", "heating-tower"]:
            continue
        m.features.append(feature)

    return (machines, modules)
