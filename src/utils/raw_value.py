from dataclasses import dataclass

@dataclass(frozen=True)
class RawValue:
    str_value: str

    def __str__(self):
        return self.str_value
