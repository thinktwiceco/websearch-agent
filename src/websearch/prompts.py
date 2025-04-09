"""Prompts module for web search operations.

This module provides models for generating system and user prompts that can be
used to generate a clean prompt for an LLM. It takes a definition, instructions,
and dontdo and returns a string that can be used as a prompt for an LLM.
"""

from collections import defaultdict

from pydantic import BaseModel


class SystemPrompt(BaseModel):
    """System prompt model.

    This class represents a system prompt that can be used to generate a clean prompt
    for an LLM. It takes a definition, instructions, and dontdo and returns a string
    that can be used as a prompt for an LLM.
    """

    definition: str
    instructions: list[str] | None = None
    dontdo: list[str] | None = None

    def text(self) -> str:
        """Generate a clean prompt from the system prompt.

        This function takes a system prompt and returns a string that can be used as
        a prompt for an LLM. It removes excess newlines and spaces and formats
        the sections with a header and a newline between each section.
        """
        sections = defaultdict(list)
        sections["definition"] = [self.definition]

        if self.instructions:
            sections["instructions"] = self.instructions
        if self.dontdo:
            sections["dontdo"] = self.dontdo

        return generate_clean_prompt(sections)


class UserPrompt(BaseModel):
    """User prompt model.

    This class represents a user prompt that can be used to generate a clean prompt
    for an LLM. It takes a query and optional steps and returns a string that can
    be used as a prompt for an LLM.
    """

    query: str
    steps: list[str] | None = None

    def text(self) -> str:
        """Generate a clean prompt from the user prompt.

        This function takes a user prompt and returns a string that can be used as
        a prompt for an LLM. It removes excess newlines and spaces and formats
        the sections with a header and a newline between each section.
        """
        sections = defaultdict(list)
        sections["query"] = [self.query]
        if self.steps:
            sections["steps"] = self.steps

        return generate_clean_prompt(sections)


def generate_clean_prompt(sections: dict[str, list[str]]) -> str:
    """Generate a clean prompt from a dictionary of sections.

    This function takes a dictionary of sections and returns a string that can be
    used as a prompt for an LLM. It removes excess newlines and spaces and formats
    the sections with a header and a newline between each section.
    """
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
