import numpy as np
import pytest

from fastscape.processes import BorderBoundary


def test_border_boundary_broadcast():
    p = BorderBoundary(status="fixed_value")

    p.initialize()
    np.testing.assert_equal(p.border, np.array(["left", "right", "top", "bottom"]))
    np.testing.assert_equal(p.border_status, ["fixed_value"] * 4)


@pytest.mark.parametrize(
    "status, expected_ibc",
    [
        (["fixed_value", "fixed_value", "fixed_value", "fixed_value"], 1111),
        (["core", "fixed_value", "fixed_value", "fixed_value"], 1110),
        (["fixed_value", "core", "fixed_value", "fixed_value"], 1011),
        (["fixed_value", "fixed_value", "core", "fixed_value"], 111),
        (["fixed_value", "fixed_value", "fixed_value", "core"], 1101),
        (["looped", "looped", "fixed_value", "fixed_value"], 1010),
        (["fixed_value", "fixed_value", "looped", "looped"], 101),
    ],
)
def test_border_boundary_ibc(status, expected_ibc):
    p = BorderBoundary(status=status)

    p.initialize()
    np.testing.assert_equal(p.ibc, expected_ibc)


@pytest.mark.parametrize(
    "status, error_msg",
    [
        (["fixed_value", "fixed_value", "core"], "Border status should be defined for all borders"),
        ("invalid_status", "Invalid border status"),
        (["looped", "looped", "core", "core"], "There must be at least one border with status"),
        (
            ["looped", "fixed_value", "looped", "fixed_value"],
            "Periodic boundary conditions must be symmetric",
        ),
    ],
)
def test_border_boundary_error(status, error_msg):
    with pytest.raises(ValueError, match=error_msg):
        BorderBoundary(status=status)


@pytest.mark.parametrize(
    "status, warning_msg",
    [
        (["core", "core", "fixed_value", "fixed_value"], "Left and right"),
        (["fixed_value", "fixed_value", "core", "core"], "Top and bottom"),
    ],
)
def test_border_boundary_warning(status, warning_msg):
    p = BorderBoundary(status=status)
    with pytest.warns(UserWarning, match=warning_msg):
        p.initialize()
