# src/schema/roadmap.py
from pydantic import BaseModel, field_validator
from fractions import Fraction

CONTRACT_VERSION = "v0.1"

class Row(BaseModel):
    piece_id: str
    mc: int
    onset: Fraction  # 0, 1/4, 1/2, 3/4 for v0
    measure: int
    beat: Fraction
    global_key: str | None = None
    local_key: str | None = None
    rn_root: str | None = None  # e.g., I, ii, V, bII, #vii
    rn_inv: str | None = None   # root, 6, 64, 7, 65, 43, 2
    rn_qual: str | None = None  # M, m, o, +, %, or None
    boundary: str = "NONE"      # NONE | START | END | LINK
    confidence_root: float | None = None
    confidence_inv: float | None = None
    confidence_boundary: float | None = None
    source: str = "gold"
    version: str = CONTRACT_VERSION

    @field_validator("boundary")
    @classmethod
    def _check_boundary(cls, v):
        assert v in {"NONE","START","END","LINK"}
        return v

def validate_dataframe(df) -> None:
    # Lightweight: row-wise validate a small sample; full checks in tests.
    for _, r in df.head(10).iterrows():
        Row(**r.to_dict()) #creates Row object using cells from row r in df
