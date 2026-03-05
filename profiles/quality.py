from profiles import Machine, EffectModule, Modifier, MachineFeature


def add_quality_features(
    quality: dict, machines: list[Machine]
) -> tuple[list[Machine], list[EffectModule]]:
    modules = []
    for id, q in quality.items():
        if id == "quality-unknown":
            continue
        speed = Modifier("speed", 1 + 0.3 * q["level"], False, False)
        modules.append(EffectModule(f"quality-{id}", [speed], False, True))
    module_ids = [m.id for m in modules]
    feature = MachineFeature("quality-tiers", 0, module_ids, None)
    # no drills, asteroid-collector, heating-tower
    for m in machines:
        if "mining-drill" in m.id or m.id in ["asteroid-collector", "heating-tower"]:
            continue
        m.features.append(feature)

    return (machines, modules)
