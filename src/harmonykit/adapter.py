# src/harmonykit/adapter.py
from pathlib import Path
from typing import Iterator, Optional

import pandas as pd  # or ms3 if you decide to depend on it

from .types import HarmonyEvent
from .utils.exceptions import (
    InvalidPieceIdError,
    PieceNotFoundError,
    MultipleMatchesError,
)


class BaseAdapter:
    """
    Adapter for a dataset of DCML TSVs.

    Responsibilities:
    - Store dataset root (validated path) + dataset name.
    - Locate an annotations TSV file for a given piece_id.
    - Load TSV rows into memory (pandas DataFrame).
    - Convert rows into HarmonyEvent objects (streaming).
    """

    def __init__(self, dataset_name: str, root_dir: str | Path):
        """
        Initialize the adapter with dataset metadata.

        - Normalize and validate root_dir (must exist and be a directory).
        - Store dataset_name for provenance.
        """
        self.dataset_name = dataset_name
        self.root = Path(root_dir).expanduser().resolve()
        if not self.root.exists():
            raise FileNotFoundError(f"Corpus root not found: {self.root}")
        if not self.root.is_dir():
            raise NotADirectoryError(f"Corpus root is not a directory: {self.root}")

    # -------------------------------------------------------------------------
    # Step 1: path resolution
    # -------------------------------------------------------------------------

    def _validate_piece_id(self, piece_id: str) -> None:
        """
        Ensure piece_id is a safe string (no slashes, no '..').
        Raise InvalidPieceIdError if not.
        """
        if "/" in piece_id or ".." in piece_id:
            raise InvalidPieceIdError(f"Illegal piece_id: {piece_id}")

    def find_annotations_path(self, piece_id: str) -> Path:
        """
        Locate the harmonies TSV for a given piece_id under self.root/harmonies.

        Tries known filename templates. Returns a resolved Path.
        Raises:
            PieceNotFoundError  if no file found
            MultipleMatchesError if more than one file matches
        """
        self._validate_piece_id(piece_id)

        harmonies_dir = self.root / "harmonies"
        if not harmonies_dir.exists():
            raise PieceNotFoundError(f"No 'harmonies' folder found in {self.root}")

        # Candidate patterns (customize if needed)
        candidates = [
            harmonies_dir / f"{piece_id}.harmonies.tsv",
            harmonies_dir / f"{piece_id}.annotations.tsv",
            harmonies_dir / f"{piece_id}_annotations.tsv",
            harmonies_dir / f"{piece_id}.tsv",
        ]

        matches = [p.resolve() for p in candidates if p.exists()]
        if not matches:
            matches = list(harmonies_dir.glob(f"{piece_id}*.tsv"))

        if not matches:
            raise PieceNotFoundError(f"No annotations TSV for piece_id={piece_id}")
        if len(matches) > 1:
            raise MultipleMatchesError(
                f"Multiple TSVs matched piece_id={piece_id}: {[m.name for m in matches]}"
            )

        return matches[0]

    # -------------------------------------------------------------------------
    # Step 2: load table
    # -------------------------------------------------------------------------

    def _load_dataframe(self, tsv_path: Path) -> pd.DataFrame:
        """
        Load the TSV file into a DataFrame.
        Keep everything as strings; coerce in HarmonyEvent.
        """
        return pd.read_csv(
            tsv_path,
            sep="\t",
            dtype=str,
            keep_default_na=False,
            encoding="utf-8",
        )

    # -------------------------------------------------------------------------
    # Step 3–4: normalize + yield HarmonyEvents
    # -------------------------------------------------------------------------

    def events(self, piece_id: str, dcml_only: bool = False) -> Iterator[HarmonyEvent]:
        """
        Yield HarmonyEvent objects for the given piece_id.

        Pipeline:
        - Find the annotations path.
        - Load the TSV into a DataFrame.
        - Sort by mc/mc_onset if available.
        - Optionally filter to rows with regex_match == 'dcml'.
        - Convert each row into a HarmonyEvent.
        """
        tsv_path = self.find_annotations_path(piece_id)
        df = self._load_dataframe(tsv_path)

        # sort deterministically
        sort_cols = [c for c in ("mc", "mc_onset") if c in df.columns]
        if sort_cols:
            df = df.sort_values(sort_cols, kind="mergesort")

        if dcml_only and "regex_match" in df.columns:
            df = df[df["regex_match"] == "dcml"]

        for _, row in df.iterrows():
            yield HarmonyEvent(
                piece_id=piece_id,
                mc=row.get("mc", 0),
                mc_onset=row.get("mc_onset", "0"),
                label=row.get("label", ""),
                regex_match=row.get("regex_match"),
                globalkey=row.get("globalkey"),
                localkey=row.get("localkey"),
                numeral=row.get("numeral"),
                figbass=row.get("figbass"),
            )
