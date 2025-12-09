"""Validation utilities for OpenFAST parameter ranges."""
from __future__ import annotations

from typing import Tuple

VALID_TURBINE_CLASSES = {f"{wind_class}{category}" for wind_class in ("1", "2", "3") for category in ("A", "B")}


def validate_rotor_diameter(rotor_diameter: float) -> float:
    """Validate that the rotor diameter is within the supported range."""
    if not isinstance(rotor_diameter, (int, float)):
        raise ValueError("Rotor diameter must be a numeric value")
    if not (0.5 <= float(rotor_diameter) <= 20.0):
        raise ValueError("Rotor diameter must be between 0.5 m and 20 m")
    return float(rotor_diameter)


def validate_hub_height(hub_height: float) -> float:
    """Validate that the hub height is within the supported range."""
    if not isinstance(hub_height, (int, float)):
        raise ValueError("Hub height must be a numeric value")
    if not (10.0 <= float(hub_height) <= 150.0):
        raise ValueError("Hub height must be between 10 m and 150 m")
    return float(hub_height)


def validate_turbine_class(turbine_class: str) -> str:
    """Validate that the turbine class matches supported IEC categories."""
    if not isinstance(turbine_class, str) or not turbine_class.strip():
        raise ValueError("IEC turbine class must be a non-empty string")
    normalized = turbine_class.strip().upper()
    if normalized not in VALID_TURBINE_CLASSES:
        raise ValueError(f"IEC turbine class must be one of: {', '.join(sorted(VALID_TURBINE_CLASSES))}")
    return normalized


def validate_openfast_parameters(rotor_diameter: float, hub_height: float, turbine_class: str) -> Tuple[float, float, str]:
    """Validate and normalize common OpenFAST parameters.

    Returns
    -------
    Tuple[float, float, str]
        Normalized (rotor_diameter, hub_height, turbine_class)
    """

    validated_rotor = validate_rotor_diameter(rotor_diameter)
    validated_hub = validate_hub_height(hub_height)
    validated_class = validate_turbine_class(turbine_class)
    return validated_rotor, validated_hub, validated_class
