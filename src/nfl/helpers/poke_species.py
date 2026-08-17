from __future__ import annotations

import re
from dataclasses import dataclass

from nfl.proto import HoloPokemonForm, HoloPokemonId, HoloTempEvoId


@dataclass(frozen=True, order=True, kw_only=True)
class PokeSpecies:
    name: HoloPokemonId
    form: HoloPokemonForm = HoloPokemonForm.FORM_UNSET
    temp_evo: HoloTempEvoId = HoloTempEvoId.TEMP_EVOLUTION_UNSET
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
    def resolve(
        cls,
        name: str,
        form: str | None = None,
        temp_evo: str | None = None,
        shadow: bool = False,
    ) -> PokeSpecies:
        name = PokeSpecies.resolve_id(name)
        form = PokeSpecies.resolve_id(form) if form else None
        temp_evo = PokeSpecies.resolve_id(temp_evo) if temp_evo else None
        if (
            form
            and form != HoloPokemonForm.FORM_UNSET.name
            and not form.startswith(f"{name}_")
        ):
            form = f"{name}_{form}"
        if temp_evo and not temp_evo.startswith("TEMP_EVOLUTION_"):
            temp_evo = f"TEMP_EVOLUTION_{temp_evo}"
        return cls(
            name=HoloPokemonId[name],
            form=HoloPokemonForm[form] if form else HoloPokemonForm.FORM_UNSET,
            temp_evo=HoloTempEvoId[temp_evo]
            if temp_evo
            else HoloTempEvoId.TEMP_EVOLUTION_UNSET,
            shadow=shadow,
        )

    @staticmethod
    def resolve_id(id: str) -> str:
        # Convert camelCase/PascalCase boundaries to underscores
        id = re.sub(r"([a-z])([A-Z])", r"\1_\2", id)

        # Replace non-alphanumeric sequences with underscores
        id = re.sub(r"[^A-Za-z0-9]+", "_", id)

        # Collapse multiple underscores
        id = re.sub(r"_+", "_", id)

        # Remove leading/trailing underscores and turn upper case
        return id.strip("_").upper()
