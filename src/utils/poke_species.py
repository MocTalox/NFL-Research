from __future__ import annotations

from dataclasses import dataclass

from utils.utils import to_screaming_snake_case


@dataclass(frozen=True)
class PokeSpecies:
    name: str
    form: str | None = None
    temp_evo: str | None = None
    shadow: bool = False

    @property
    def naming(self) -> str:
        parts: list[str] = []

        if self.shadow:
            parts.append("SHADOW")

        if self.temp_evo is not None:
            parts.append(self.temp_evo)

        parts.append(self.form if self.form is not None else self.name)

        return "_".join(parts)

    @classmethod
    def by_name(cls, name: str) -> PokeSpecies:
        return cls(
            name=to_screaming_snake_case(name),
        )

    @classmethod
    def by_name_form(cls, name: str, form: str) -> PokeSpecies:
        return cls(
            name=to_screaming_snake_case(name),
            form=to_screaming_snake_case(f"{name}_{form}"),
        )

    @classmethod
    def by_full_form(cls, name: str, form: str) -> PokeSpecies:
        return cls(
            name=to_screaming_snake_case(name),
            form=to_screaming_snake_case(form),
        )

    @classmethod
    def by_name_temp_evo(cls, name: str, temp_evo: str) -> PokeSpecies:
        return cls(
            name=to_screaming_snake_case(name),
            temp_evo=to_screaming_snake_case(f"TEMP_EVOLUTION_{temp_evo}"),
        )

    @classmethod
    def by_full_temp_evo(cls, name: str, temp_evo: str) -> PokeSpecies:
        return cls(
            name=to_screaming_snake_case(name),
            temp_evo=to_screaming_snake_case(temp_evo),
        )

    @classmethod
    def by_name_shadow(cls, name: str) -> PokeSpecies:
        return cls(
            name=to_screaming_snake_case(name),
            shadow=True,
        )

    @classmethod
    def by_name_form_shadow(cls, name: str, form: str) -> PokeSpecies:
        return cls(
            name=to_screaming_snake_case(name),
            form=to_screaming_snake_case(f"{name}_{form}"),
            shadow=True,
        )

    @classmethod
    def by_full_form_shadow(cls, name: str, form: str) -> PokeSpecies:
        return cls(
            name=to_screaming_snake_case(name),
            form=to_screaming_snake_case(form),
            shadow=True,
        )
