from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable, List, Tuple, Optional, Union
from enum import Enum
from pathlib import Path      # robust path handling
import re     

class Brace(Enum):
    NONE = "NONE"
    OPEN = "OPEN"         # "{"
    CLOSE = "CLOSE"       # "}"
    BOUNDARY = "BOUNDARY" # "}{"
    
    
@dataclass(slots=True)  # add frozen=True if you want immutability
class HarmonyEvent:
    """
    A single harmony event from a DCML harmony .tsv row.

    Attributes
    ----------
    piece_id : str
        Identifier for the piece (e.g. "K279-1").
    mc : int
        Measure-count index (stable, not the printed measure number).
    mc_onset : Fraction
        Onset within the measure (fraction of a whole note). Example: "1/4".
    label : str
        Raw DCML label (e.g., "V7", "I6", "{", "PAC").
    regex_match : Optional[str]
        Regex category from ms3 (often "dcml").
    globalkey : Optional[str]
        Overall piece key, if available.
    localkey : Optional[str]
        Local key at this position, if available.
    numeral : Optional[str]
        Roman numeral parsed by upstream tools.
    figbass : Optional[str]
        Figured-bass / inversion marker (e.g., "6", "64", "7").
    """
    piece_id: str
    mc: int
    mc_onset: Union[str, int, float, Fraction]
    label: str
    regex_match: Optional[str] = None
    globalkey: Optional[str] = None
    localkey: Optional[str] = None
    numeral: Optional[str] = None
    figbass: Optional[str] = None
    chord_type: Optional[str] = None

    def __post_init__(self):
        self.mc = int(self.mc)      # Force measure count to integer
        self.mc_onset = Fraction(str(self.mc_onset))        # Force mc onset to fraction
        self.label = str(self.label).strip()    # Remove spaces from label
        
    @property
    def brace(self) -> Brace:
        raw = self.label
        if "}{".lower() in raw:
            return Brace.BOUNDARY
        elif "{" in raw:
            return Brace.OPEN
        elif "}" in raw:
            return Brace.CLOSE
        else:
            return Brace.NONE

    @property
    def clean_label(self) -> Optional[str]:
        txt = (
            self.label.replace("}{", "")
                      .replace("{", "")
                      .replace("}", "")
                      .strip()
        )
        return txt or None

