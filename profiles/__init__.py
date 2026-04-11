from typing import Union, Literal
import dataclasses


@dataclasses.dataclass
class Settings:
    defaultDuration: int
    allRecipesUnlocked: bool
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
    craftable: bool | None


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


@dataclasses.dataclass
class BaseEffectModule:
    id: str
    modifiers: list[Modifier]
    available: bool = dataclasses.field(default=True, kw_only=True)
    hidden: bool | None = dataclasses.field(default=None, kw_only=True)


@dataclasses.dataclass
class FixedEffectModule(BaseEffectModule):
    type: Literal["fixed"] = "fixed"


@dataclasses.dataclass
class ModifiableEffectModule(BaseEffectModule):
    minValue: float
    maxValue: float
    type: Literal["modifiable"] = "modifiable"


@dataclasses.dataclass
class SteppedEffectModule(BaseEffectModule):
    minValue: float
    maxValue: float
    step: float
    type: Literal["stepped"] = "stepped"


EffectModule = Union[FixedEffectModule, ModifiableEffectModule, SteppedEffectModule]


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


@dataclasses.dataclass
class Conveyor:
    id: str
    speed: int
    features: list[MachineFeature] | None


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
