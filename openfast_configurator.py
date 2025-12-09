"""Utility for programmatic OpenFAST input manipulation.

This module provides a thin wrapper around ``openfast_io`` that makes it easier
for automation scripts to read a main ``.fst`` file and adjust common
parameters such as blade geometry, control configuration, and output requests.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional, Tuple

import pandas as pd
from openfast_io.fast_input_file import FASTInputFile


class OpenFASTConfigurator:
    """High-level helper for editing OpenFAST input decks.

    Parameters
    ----------
    fst_path:
        Path to the primary ``.fst`` file that ties together all module input
        files. Relative references in the file are resolved against this path.
    """

    def __init__(self, fst_path: Path | str):
        self.fst_path = Path(fst_path)
        self.root = FASTInputFile(self.fst_path)
        self.base_dir = self.fst_path.parent

    @staticmethod
    def _strip_quotes(raw_value: str) -> str:
        if isinstance(raw_value, str) and raw_value.startswith("\"") and raw_value.endswith("\""):
            return raw_value.strip('"')
        return raw_value

    def _resolve_child(self, key: str) -> Tuple[FASTInputFile, Path]:
        try:
            raw_value = self.root[key]
        except KeyError as exc:  # pragma: no cover - defensive programming
            raise KeyError(f"The key {key!r} was not found in the FAST file") from exc
        child_path = self.base_dir / self._strip_quotes(raw_value)
        return FASTInputFile(child_path), child_path

    @staticmethod
    def _get_table(file_obj: FASTInputFile, preferred_keys: Iterable[str]) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        data = getattr(file_obj, "data", None)
        if not isinstance(data, dict):
            return None, None
        for key in preferred_keys:
            if key in data:
                return data[key], key
        return None, None

    def _ensure_length_match(self, *arrays: Iterable) -> int:
        lengths = [len(list(arr)) for arr in arrays]
        if len(set(lengths)) != 1:
            raise ValueError(f"Blade geometry arrays must all be the same length: {lengths}")
        return lengths[0]

    def update_blade_geometry(self, blade_index: int, span: List[float], chord: List[float], twist: List[float]) -> None:
        """Update the blade geometry table with new spanwise chord and twist.

        The method loads the blade input file referenced by ``BldFile(<n>)`` and
        rewrites the geometry table. If a table is not present it will be
        created with the provided inputs.
        """

        table_candidates = [f"BldFile({blade_index})", f"BldFile{blade_index}"]
        blade_file = None
        blade_path = None
        for candidate in table_candidates:
            if candidate in getattr(self.root, "data", {}):
                blade_file, blade_path = self._resolve_child(candidate)
                break
        if blade_file is None:
            raise KeyError(f"No blade file reference found for blade index {blade_index}")

        self._ensure_length_match(span, chord, twist)
        table, key = self._get_table(blade_file, ["BldProp", "BladeGeom", "BldAero"])
        new_table = pd.DataFrame({
            "BlSpn": list(span),
            "BlChord": list(chord),
            "BlTwist": list(twist),
        })

        data = getattr(blade_file, "data", None)
        if isinstance(data, dict):
            if key:
                data[key] = new_table
            else:
                data["BldProp"] = new_table
        blade_file.write(blade_path)

    def update_control_setting(self, module_field: str, parameter: str, value) -> None:
        """Set a control-related parameter in a linked module file.

        Examples include ``ServoFile`` for ServoDyn or a custom controller
        reference such as ``DLL_FileName``. The method performs a simple
        key/value replacement in the targeted file.
        """

        module_file, module_path = self._resolve_child(module_field)
        module_file[parameter] = value
        module_file.write(module_path)

    def add_output_request(self, module_field: str, signal: str) -> None:
        """Ensure an output channel is present in the specified module.

        The method looks for an ``OutList`` or ``OutList(*)`` key, appends the
        requested signal if it is not already present, and writes the updated
        module back to disk.
        """

        module_file, module_path = self._resolve_child(module_field)
        data = getattr(module_file, "data", {})
        outlist_keys = ["OutList", "OutList(*)", "OutListDetail"]
        active_key = next((key for key in outlist_keys if key in data), None)
        if active_key is None:
            # If no list is present, start a new one using the common name
            data["OutList"] = [signal]
        else:
            outputs = data.get(active_key, [])
            if signal not in outputs:
                if isinstance(outputs, list):
                    outputs.append(signal)
                else:
                    outputs = [outputs, signal]
                data[active_key] = outputs
        module_file.write(module_path)

    def persist(self, target: Path | str | None = None) -> None:
        """Write the main ``.fst`` file back to disk.

        Parameters
        ----------
        target:
            Optional override for where to write the updated FAST file. If not
            provided, the original file is overwritten.
        """

        output_path = Path(target) if target else self.fst_path
        self.root.write(output_path)
