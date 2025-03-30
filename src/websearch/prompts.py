from collections import defaultdict
from tkinter import N
from pydantic import BaseModel


class SystemPrompt(BaseModel):
    definition: str
    instructions: list[str] | None = None
    dontdo: list[str] | None = None

    def text(self) -> str:
        sections = defaultdict(list)
        sections["definition"] = [self.definition]

        if self.instructions:
            sections["instructions"] = self.instructions
        if self.dontdo:
            sections["dontdo"] = self.dontdo

        return generate_clean_prompt(sections)

class UserPrompt(BaseModel):
    query: str
    steps: list[str] | None = None

    def text(self) -> str:
        sections = defaultdict(list)
        sections["query"] = [self.query]
        if self.steps:
            sections["steps"] = self.steps

        return generate_clean_prompt(sections)

def generate_clean_prompt(sections: dict[str, list[str]]) -> str:
    # Remove excess of newlines and spaces
    retval = ""
    for k, v in sections.items():
        if not isinstance(v, list):
            if isinstance(v, str):
                v = [v]
            else:
                raise ValueError(f"Expected list, got {type(v)}")

        retval += f"## {k.upper()}\n"
        retval += "\n".join(v).strip()
        retval += "\n"
    return retval
