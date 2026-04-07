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

        out.append(Research(id, unlocks, tech.get("prerequisites", None)))
    return out


def get_research_depths(researches: list[Research]) -> dict[str, int]:
    research_dict = {r.id: r for r in researches}
    depths: dict[str, int] = {}

    def get_depth(research: Research) -> int:
        if research.id in depths:
            return depths[research.id]

        if not research.prerequisites:
            depths[research.id] = 0
            return 0

        result = 1 + max(
            get_depth(research_dict[prereq_id]) for prereq_id in research.prerequisites
        )
        depths[research.id] = result
        return result

    for r in researches:
        get_depth(r)

    return depths
