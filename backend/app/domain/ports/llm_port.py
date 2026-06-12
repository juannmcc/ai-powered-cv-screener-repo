"""
Port: LLMPort
Defines the contract that any LLM provider must implement.
"""

from abc import ABC, abstractmethod


class LLMPort(ABC):

    @abstractmethod
    def chat(self, messages: list[dict]) -> str:
        """Send messages and return LLM response."""
        ...

    @abstractmethod
    def is_available(self) -> tuple[bool, str]:
        """Check if provider is available. Returns (ok, message)."""
        ...
