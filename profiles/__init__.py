from typing import Union, Literal
import dataclasses


@dataclasses.dataclass
class Settings:
    default_duration: int
    all_recipes_unlocked: bool
    limitations: list[str] | None


@dataclasses.dataclass
class BaseItemIo:
    id: str
    amount: int


@dataclasses.dataclass
class Recipe:
    id: str
    inp: list[BaseItemIo] = dataclasses.field(metadata={"alias": "in"})
    out: list[BaseItemIo]
    duration: int
    category: str
    priority: int
    available: bool
    limitations: list[str] | None


@dataclasses.dataclass
class Item:
    id: str
    type: str
    category: str
    stackSize: int


@dataclasses.dataclass
class MachineFeature:
    id: str
    itemSlots: int
    effectPerSlot: list[str]
    hidden: bool | None


@dataclasses.dataclass
class Machine:
    id: str
    recipeCategories: list[str]
    requiredPower: int
    features: list[MachineFeature]
    available: bool
    limitations: list[str] | None


@dataclasses.dataclass
class Modifier:
    id: str
    value: float
    modifiable: bool
    onlyOutputScales: bool


@dataclasses.dataclass
class EffectModule:
    id: str
    modifiers: list[Modifier]
    perSlot: bool
    available: bool


@dataclasses.dataclass
class Planet:
    id: str
    pressure: int


@dataclasses.dataclass
class UnlockRecipe:
    type: Literal["recipe"]
    ids: list[str]


UnlockType = Union[UnlockRecipe]


@dataclasses.dataclass
class Research:
    id: str
    unlocks: list[UnlockType]
    prerequisites: list[str] | None


@dataclasses.dataclass
class FuelItem(Item):
    fuel_category: str
    fuel_value: int
    burnt_result: str | None


@dataclasses.dataclass
class BurntRecipeStarter:
    id_in: str
    id_out: str
    fuel_value: int
    fuel_category: str


@dataclasses.dataclass
class HeatCapacityFluids:
    id: str
    heat_capacity: int
    default_temperature: int


POWER_FACTORS = {
    "GJ": 1000 * 1000 * 1000,
    "GW": 1000 * 1000 * 1000,
    "MJ": 1000 * 1000,
    "MW": 1000 * 1000,
    "kJ": 1000,
    "kW": 1000,
    "W": 1,
    "J": 1,
}
