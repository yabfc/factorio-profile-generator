from profiles import Conveyor


def get_conveyors(old_conveyors: dict) -> list[Conveyor]:
    out = []
    for id, conveyor in old_conveyors.items():
        # magic number comes from https://lua-api.factorio.com/stable/prototypes/TransportBeltConnectablePrototype.html
        out.append(Conveyor(id, conveyor["speed"] * 480, None))

    return out
