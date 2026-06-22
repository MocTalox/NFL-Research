from __future__ import annotations

from dataclasses import dataclass
import re

from core.gm_holoholo import HoloPokemonId, HoloPokemonForm, HoloTempEvoId


def _to_screaming_snake_case(text: str) -> str:
    # Convert camelCase/PascalCase boundaries to underscores
    text = re.sub(r"([a-z])([A-Z])", r"\1_\2", text)

    # Replace non-alphanumeric sequences with underscores
    text = re.sub(r"[^A-Za-z0-9]+", "_", text)

    # Collapse multiple underscores
    text = re.sub(r"_+", "_", text)

    # Remove leading/trailing underscores and turn upper case
    return text.strip("_").upper()

@dataclass(frozen=True, order=True, kw_only=True)
class PokeSpecies:
    name: HoloPokemonId
    form: HoloPokemonForm = HoloPokemonForm(0)
    temp_evo: HoloTempEvoId = HoloTempEvoId(0)
    shadow: bool = False

    @property
    def identity(self) -> PokeSpecies:
        return PokeSpecies(
            name=self.name,
            form=self.form,
            temp_evo=self.temp_evo,
            shadow=self.shadow,
        )

    def is_the_same(self, other: PokeSpecies) -> bool:
        return type(self) is type(other) and self == other

    def __str__(self):
        parts: list[str] = []

        if self.shadow:
            parts.append("SHADOW")

        if self.temp_evo:
            parts.append(self.temp_evo.name)

        parts.append(self.form.name if self.form else self.name.name)

        return "_".join(parts)

    @classmethod
    def by_name(cls, name: str) -> PokeSpecies:
        return cls(
            name=HoloPokemonId[_to_screaming_snake_case(name)],
        )

    @classmethod
    def by_name_form(cls, name: str, form: str) -> PokeSpecies:
        return cls(
            name=HoloPokemonId[_to_screaming_snake_case(name)],
            form=HoloPokemonForm[_to_screaming_snake_case(f"{name}_{form}")],
        )

    @classmethod
    def by_full_form(cls, name: str, form: str) -> PokeSpecies:
        return cls(
            name=HoloPokemonId[_to_screaming_snake_case(name)],
            form=HoloPokemonForm[_to_screaming_snake_case(form)],
        )

    @classmethod
    def by_name_temp_evo(cls, name: str, temp_evo: str) -> PokeSpecies:
        return cls(
            name=HoloPokemonId[_to_screaming_snake_case(name)],
            temp_evo=HoloTempEvoId[_to_screaming_snake_case(f"TEMP_EVOLUTION_{temp_evo}")],
        )

    @classmethod
    def by_full_temp_evo(cls, name: str, temp_evo: str) -> PokeSpecies:
        return cls(
            name=HoloPokemonId[_to_screaming_snake_case(name)],
            temp_evo=HoloTempEvoId[_to_screaming_snake_case(temp_evo)],
        )

    @classmethod
    def by_name_shadow(cls, name: str) -> PokeSpecies:
        return cls(
            name=HoloPokemonId[_to_screaming_snake_case(name)],
            shadow=True,
        )

    @classmethod
    def by_name_form_shadow(cls, name: str, form: str) -> PokeSpecies:
        return cls(
            name=HoloPokemonId[_to_screaming_snake_case(name)],
            form=HoloPokemonForm[_to_screaming_snake_case(f"{name}_{form}")],
            shadow=True,
        )

    @classmethod
    def by_full_form_shadow(cls, name: str, form: str) -> PokeSpecies:
        return cls(
            name=HoloPokemonId[_to_screaming_snake_case(name)],
            form=HoloPokemonForm[_to_screaming_snake_case(form)],
            shadow=True,
        )
