from fastscape.processes.context import FastscapelibContext


def test_fastscapelib_context():

    p = FastscapelibContext(shape=(3, 4), length=(10., 30.))

    p.initialize()

    assert p.context["nx"] == 4
    assert p.context["ny"] == 3
    assert p.context["xl"] == 30.
    assert p.context["yl"] == 10.
    assert p.context["h"].size == 3 * 4

    p.run_step(10.)

    assert p.context["dt"] == 10.

    p.finalize()

    assert p.context["h"] is None
