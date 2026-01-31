from profiles import Research, UnlockRecipe


def get_research(old_tech: dict) -> list[Research]:
    out = []
    for id, tech in old_tech.items():
        unlocks = []
        effect_dict = {}
        for effect in tech.get("effects", []):
            if effect["type"] not in effect_dict:
                effect_dict[effect["type"]] = []
            effect_dict[effect["type"]].append(
                [v for k, v in effect.items() if k != "type"][0]
            )
        for utype, vals in effect_dict.items():
            if utype == "unlock-recipe":
                unlocks.append(UnlockRecipe("recipe", vals))
            # TODO add other types like producitvity effects
        if len(unlocks) == 0:
            continue
        out.append(Research(id, unlocks, tech.get("prerequisites", None), False))
    return out
