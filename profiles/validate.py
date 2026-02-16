from profiles import Recipe, Item, Machine


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


def validate_items(items: list[Item], recipes: list[Recipe]) -> bool:
    ids_recipe = set()
    ids_item = set()
    for r in recipes:
        ids_recipe |= set([i.id for i in r.inp])
        ids_recipe |= set([i.id for i in r.out])
    for i in items:
        ids_item.add(i.id)
    for id in ids_recipe.difference(ids_item):
        print(f"Item does not exist but can be produced: {id}")
    return len(ids_recipe.difference(ids_item)) == 0


def validate_machines(machines: list[Machine], recipes: list[Recipe]) -> bool:
    categories_recipe = set()
    categories_machine = set()
    for r in recipes:
        categories_recipe.add(r.category)
    for m in machines:
        categories_machine |= set(m.recipeCategories)
    for id in categories_recipe.difference(categories_machine):
        if id == "manual-harvest":
            print(
                f"{id} is expected to not have a machine assigned. You are the machine"
            )
        else:
            print(
                f"Recipe category does not have a machine it can be produced in: {id}"
            )
    return len(categories_recipe.difference(categories_machine)) == 0
