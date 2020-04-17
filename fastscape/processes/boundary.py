import warnings

import numpy as np
import xsimlab as xs

from .context import FastscapelibContext


@xs.process
class BorderBoundary:
    """Sets boundary conditions at grid borders.

    Borders are defined in the following order:

    left, right, top, bottom

    Border status can be one of:

    - "core" (open boundary)
    - "fixed_value" (closed boundary)
    - "looped" (periodic boundary)

    "fixed_value" must be set for at least one border. This is the minimal
    constraint in order to make the numerical model solvable.

    "looped" must be symmetric, i.e., defined for (left, right)
    or (top, bottom).

    Note that currently if "core" is set for two opposed borders these
    will have periodic conditions (this comes from a current limitation in
    fastscapelib-fortran which will be solved in a next release).

    """
    status = xs.variable(
        dims=[(), 'border'],
        default="fixed_value",
        description='node status at borders',
        static=True
    )

    border = xs.index(
        dims='border', description='4-border boundaries coordinate'
    )
    border_status = xs.variable(
        dims='border',
        intent='out',
        description='node status at the 4-border boundaries'
    )

    fs_context = xs.foreign(FastscapelibContext, 'context')

    ibc = xs.variable(
        intent='out',
        description='boundary code used by fastscapelib-fortran'
    )

    @status.validator
    def _check_status(self, attribute, value):
        if not np.isscalar(value) and len(value) != 4:
            raise ValueError(
                "Border status should be defined for all borders "
                f"(left, right, top, bottom), found {value}"
            )

        valid = ["fixed_value", "core", "looped"]
        bs = list(np.broadcast_to(value, 4))

        for s in bs:
            if s not in valid:
                raise ValueError(f"Invalid border status {s!r}, must be one of {valid}")

        if "fixed_value" not in bs:
            raise ValueError(
                f"There must be at least one border with status 'fixed_value', found {bs}"
            )

        def invalid_looped(s):
            return bool(s[0] == "looped") ^ bool(s[1] == "looped")

        if invalid_looped(bs[:2]) or invalid_looped(bs[2:]):
            raise ValueError(f"Periodic boundary conditions must be symmetric, found {bs}")

    def initialize(self):
        self.border = np.array(['left', 'right', 'top', 'bottom'])

        bstatus = np.array(np.broadcast_to(self.status, 4))

        # TODO: remove when solved in fastscapelib-fortran
        w_msg_common = (
            "borders have both 'core' status but periodic conditions "
            "are used due to current behavior in fastscapelib-fortran"
        )

        if (bstatus[0] == "core" and bstatus[1] == "core"):
            w_msg = "Left and right " + w_msg_common
            warnings.warn(w_msg, UserWarning)

        if (bstatus[2] == "core" and bstatus[3] == "core"):
            w_msg = "Top and bottom " + w_msg_common
            warnings.warn(w_msg, UserWarning)

        self.border_status = bstatus

        # convert to fastscapelib-fortran ibc code
        arr_bc = np.array([1 if st == 'fixed_value' else 0
                           for st in self.border_status])

        # different border order
        self.ibc = sum(arr_bc * np.array([1, 100, 10, 1000]))

        self.fs_context["ibc"] = self.ibc
