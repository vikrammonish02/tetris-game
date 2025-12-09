from pathlib import Path
import sys

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from openfast_validation import (
    VALID_TURBINE_CLASSES,
    validate_hub_height,
    validate_openfast_parameters,
    validate_rotor_diameter,
    validate_turbine_class,
)


@pytest.mark.parametrize("diameter", [0.5, 1.0, 10.0, 20.0])
def test_validate_rotor_diameter_accepts_bounds(diameter):
    assert validate_rotor_diameter(diameter) == float(diameter)


@pytest.mark.parametrize("diameter", [0.49, 0, -1, 20.1])
def test_validate_rotor_diameter_rejects_out_of_bounds(diameter):
    with pytest.raises(ValueError):
        validate_rotor_diameter(diameter)


@pytest.mark.parametrize("value", ["not-a-number", None, []])
def test_validate_rotor_diameter_type_errors(value):
    with pytest.raises(ValueError):
        validate_rotor_diameter(value)


@pytest.mark.parametrize("height", [10, 75.5, 150])
def test_validate_hub_height_accepts_bounds(height):
    assert validate_hub_height(height) == float(height)


@pytest.mark.parametrize("height", [9.99, 0, -5, 150.1])
def test_validate_hub_height_rejects_out_of_bounds(height):
    with pytest.raises(ValueError):
        validate_hub_height(height)


@pytest.mark.parametrize("value", ["ten", None, {}])
def test_validate_hub_height_type_errors(value):
    with pytest.raises(ValueError):
        validate_hub_height(value)


@pytest.mark.parametrize("iec_class", sorted(VALID_TURBINE_CLASSES))
def test_validate_turbine_class_accepts_all_supported_classes(iec_class):
    # verify normalization is applied (lowercase input still passes)
    assert validate_turbine_class(iec_class.lower()) == iec_class


@pytest.mark.parametrize("invalid_class", ["0A", "4A", "2C", "3D", "", "abc", None])
def test_validate_turbine_class_rejects_invalid_values(invalid_class):
    with pytest.raises(ValueError):
        validate_turbine_class(invalid_class)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "rotor_diameter, hub_height, turbine_class",
    [
        (0.5, 10, "1A"),
        (20, 150, "3B"),
        (15.25, 120, "2B"),
    ],
)
def test_validate_openfast_parameters_success(rotor_diameter, hub_height, turbine_class):
    validated = validate_openfast_parameters(rotor_diameter, hub_height, turbine_class)
    assert validated == (
        float(rotor_diameter),
        float(hub_height),
        turbine_class.upper(),
    )


@pytest.mark.parametrize(
    "rotor_diameter, hub_height, turbine_class",
    [
        (0.1, 50, "1A"),
        (2.0, 9.9, "1A"),
        (2.0, 50, "4A"),
    ],
)
def test_validate_openfast_parameters_errors(rotor_diameter, hub_height, turbine_class):
    with pytest.raises(ValueError):
        validate_openfast_parameters(rotor_diameter, hub_height, turbine_class)
