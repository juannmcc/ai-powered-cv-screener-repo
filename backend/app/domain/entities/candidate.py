"""
Domain entity: Candidate
Represents a CV candidate in the system.
"""

from dataclasses import dataclass


@dataclass
class Candidate:
    name:   str
    source: str
    avatar: str = ""

    @classmethod
    def from_filename(cls, filename: str) -> "Candidate":
        """Build candidate from PDF filename: cv_01_John_Doe.pdf"""
        stem = filename.replace(".pdf", "")
        name = stem.split("_", 2)[-1].replace("_", " ")
        return cls(
            name=name,
            source=filename,
            avatar=f"/avatars/{stem}.jpg",
        )
