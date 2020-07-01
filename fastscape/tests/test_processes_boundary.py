import numpy as np

import pytest
import warnings

from fastscape.processes import BorderBoundary

@pytest.mark.parametrize('input_status, expected', [
    (['fixed_value', 'fixed_value', 'fixed_value', 'fixed_value'],
    {'border_status': np.array(['fixed_value', 'fixed_value', 'fixed_value', 'fixed_value']),
     'ibc': 1111}),
    (['fixed_value', 'core', 'fixed_value', 'fixed_value'],
    {'border_status': np.array(['fixed_value', 'core', 'fixed_value', 'fixed_value']),
     'ibc': 1011}),
    (['looped', 'looped', 'fixed_value', 'fixed_value'],
    {'border_status': np.array(['looped', 'looped', 'fixed_value', 'fixed_value']),
     'ibc': 1010})
])
def test_border_boundary(input_status, expected):
    p = BorderBoundary(status=input_status)

    p.initialize()
    np.testing.assert_equal(p.border_status, expected['border_status'])
    np.testing.assert_equal(p.ibc, expected['ibc'])


@pytest.mark.parametrize('inputs, errors', [
    (['fixed_value', 'fixed_value', 'core'], 'Border status should be defined for all borders'),
    (5, 'Invalid border status'),
    (['looped', 'looped', 'core', 'core'], 'There must be at least one border with status'),
    (['looped', 'fixed_value', 'looped', 'fixed_value'], 'Periodic boundary conditions must be symmetric')
])
def test_border_boundary_warnings(inputs, errors):
    with pytest.raises(ValueError) as excinfo:
        p = BorderBoundary(status=inputs)

    assert errors in str(excinfo.value)


@pytest.mark.parametrize('inputs', [
    (['core', 'core', 'fixed_value', 'fixed_value']),
    (['fixed_value', 'fixed_value', 'core', 'core'])
])
def test_border_boundary_warnings(inputs):
    p = BorderBoundary(status=inputs)
    with pytest.warns(UserWarning):
        p.initialize()


@pytest.mark.parametrize('inputs, warning_msg', [
    (['core', 'core', 'fixed_value', 'fixed_value'], 'Left and right'),
    (['fixed_value', 'fixed_value', 'core', 'core'], 'Top and bottom')
])
def test_border_boundary_warnings2(inputs, warning_msg):
    p = BorderBoundary(status=inputs)
    with warnings.catch_warnings(record=True) as w:

        warnings.simplefilter("always")

        p.initialize()

        assert len(w) == 1
        assert issubclass(w[-1].category, UserWarning)
        assert warning_msg in str(w[-1].message)
