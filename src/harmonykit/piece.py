# src/harmonykit/piece.py
from __future__ import annotations

from pathlib import Path
from typing import Iterator, Optional

# Local imports (adjust to your package structure)
from .types import HarmonyEvent   # your minimal record class
from .adapter import BaseAdapter  # your adapter that reads TSVs


class Piece:
    """
    Lightweight handle for a musical piece in a DCML-capable corpus.

    Responsibilities (by design, minimal):
    - Identify a piece by `piece_id` (e.g., "K279-1") and which dataset it belongs to.
    - Hold a reference to an Adapter that knows how to find/read this piece's TSVs.
    - Provide lazy access to HarmonyEvents via `events()` (no heavy caching by default).

    Notes:
    - `Piece` should be cheap to construct; do not read files in __init__.
    - Keep the dataset directory read-only; any caches should live elsewhere.
    """

    def __init__(
        self,
        piece_id: str,
        adapter: BaseAdapter,
        dataset_name: Optional[str] = None,
    ) -> None:
        """
        Parameters
        ----------
        piece_id : str
            Identifier used by the corpus (filename stem).
        adapter : BaseAdapter
            Adapter instance configured for the dataset's root and conventions.
        dataset_name : Optional[str]
            Human-readable dataset label (e.g., "mozart"). If omitted, you can
            derive it from `adapter` later or leave it None.
        """
        self._piece_id = str(piece_id)
        self._adapter = adapter
        self._dataset_name = dataset_name

    # ----------------------------- metadata ---------------------------------

    @property
    def piece_id(self) -> str:
        """Stable identifier for this piece (filename stem)."""
        return self._piece_id

    @property
    def dataset_name(self) -> Optional[str]:
        """Optional dataset label (e.g., 'mozart')."""
        return self._dataset_name

    @property
    def root(self) -> Path:
        """Root directory of the dataset (delegated to adapter)."""
        return self._adapter.root

    # ---------------------------- data access --------------------------------

    def annotations_path(self) -> Path:
        """
        Resolved path to the piece's annotations TSV (delegates to adapter).
        May raise FileNotFoundError or RuntimeError (ambiguous) per adapter rules.
        """
        return self._adapter.find_annotations_path(self._piece_id)

    def events(self, dcml_only: bool = False) -> Iterator[HarmonyEvent]:
        """
        Lazily yield HarmonyEvent objects for this piece (delegates to adapter).

        Parameters
        ----------
        dcml_only : bool
            If True, filter to rows recognized as DCML harmony labels
            (adapter decides how to detect this, typically via 'regex_match').
        """
        yield from self._adapter.events(self._piece_id, dcml_only=dcml_only)

    # ----------------------------- repr/debug --------------------------------

    def __repr__(self) -> str:
        ds = f", dataset='{self._dataset_name}'" if self._dataset_name else ""
        return f"Piece(piece_id='{self._piece_id}'{ds})"
