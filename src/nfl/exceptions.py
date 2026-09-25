from typing import Any

ERROR_MESSAGES = {
    "UNKNOWN_ERROR": "Unknown error.",
    "INVALID_GAME_MASTER": "Configured game master is invalid.",
    "MISSING_TEMP_EVO": "Missing temporary evolution overrides for {pokemon_id} ({pokemon_form}): {temp_evo_id}",
    "MISSIGN_SPECIES_DATA": "No Pokémon data found for species: {poke_species}",
    "SHADOW_ENEMY": "Enemy Pokémon must be shadow.",
    "TGR_POKEMON_LEVEL": "TGR members Pokémons cannot be of half levels.",
    "INVALID_POKÉMON_DIMENSIONS": "Invalid Pokémon dimensions: weight_kg={weight_kg}, height_m={height_m}. Values must be positive.",
    "SIZE_CLASS_MISMATCH": "Size class mismatch: Pokémon with height {height_m}m cannot be {size_class} ([{lower}, {upper}])",
    "INVALID_ZORUA_DIMENSIONS": "Invalid Zorua dimensions: weight_kg={weight_kg}, height_m={height_m}. Values must be positive.",
    "SIZE_CLASS_MISMATCH_ZORUA": "Size class mismatch: Zorua with height {height_m}m cannot be {size_class} ([{lower}, {upper}])",
    "INVALID_LEVEL_DECIMALS": "Invalid level {level}: must be a multiple of 0.5 (e.g. 1.0, 1.5, 2.0).",
    "INVALID_LEVEL_RANGE": "Invalid level {level}: must be between 1.0 and {max_level:.1f}.",
    "INVALID_LEVEL_RANGE_TGR": "Invalid level {level}: must be between 1 and {max_level}.",
    "NO_RANK_MULTIPLIER": "No rank multiplier configured for {character_category}",
    "DUPLICATE_IDENTITY": "Duplicate entry for identity: {identity}",
    "MULTIPLE_MAIN_SPECIES": "Multiple main species in group {category!r}: {old!r} and {new!r}",
    "MISSING_MAIN_SPECIES": "Species group contains forms but no main species: {forms_list!r}",
    "INVALID_CPM_VALUES": "Invalid CPM values: {attacker_cpm}, {target_cpm}. Values must be positive.",
}


class NflError(Exception):
    """Base class for all NFL exceptions."""

    def __init__(self, code: str, **details: Any):
        self.code = code if code in ERROR_MESSAGES else "UNKNOWN_ERROR"
        self.details = details

        template = ERROR_MESSAGES[self.code]
        message = template.format(**details)

        super().__init__(message)


class ValidationError(NflError):
    """User-provided data is invalid."""


class NotFoundError(NflError):
    """A requested resource could not be found."""


class ConfigurationError(NflError):
    """The library is incorrectly configured."""
