from profiles import Logistic

# slightly awkward but there is no static throughput
# see https://factorio.com/blog/post/fff-416
DUMMY_PIPE = Logistic("pipe", "fluid", 0, None)


def get_conveyors(old_conveyors: dict) -> list[Logistic]:
    out = [DUMMY_PIPE]
    for id, conveyor in old_conveyors.items():
        # magic number comes from https://lua-api.factorio.com/stable/prototypes/TransportBeltConnectablePrototype.html
        out.append(Logistic(id, "item", conveyor["speed"] * 480, None))
    return out
