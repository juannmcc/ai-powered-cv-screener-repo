"""
Domain entity: ChatMessage and ChatResponse
"""

from dataclasses import dataclass, field


@dataclass
class Source:
    candidate: str
    source:    str
    score:     float


@dataclass
class ChatResponse:
    answer:      str
    sources:     list[Source]     = field(default_factory=list)
    suggestions: list[str]        = field(default_factory=list)
