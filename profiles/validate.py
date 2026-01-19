from profiles import Recipe


def validate_recipes(recipes: list[Recipe]) -> bool:
    ids_all = set()
    ids_in = set()
    ids_out = set()
    recipe_ids = set()
    for r in recipes:
        if r.id in recipe_ids:
            print(f"Duplicate Recipe ID: {r.id}")
        else:
            recipe_ids.add(r.id)
        ids_in |= set([i.id for i in r.inp])
        ids_out |= set([i.id for i in r.out])
        ids_all |= ids_in | ids_out
    for id in ids_in.difference(ids_out):
        print(f"Item can't be produced: {id}")
    return len(ids_in.difference(ids_out)) == 0
