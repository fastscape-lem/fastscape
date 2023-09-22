from fastscape.processes.context import FastscapelibContext


def test_fastscapelib_context():
    p = FastscapelibContext(shape=(3, 4), length=(10.0, 30.0), ibc=1111)

    p.initialize()

    assert p.context["nx"] == 4
    assert p.context["ny"] == 3
    assert p.context["xl"] == 30.0
    assert p.context["yl"] == 10.0
    assert p.context["h"].size == 3 * 4
    assert p.context["bounds_ibc"] == 1111

    p.run_step(10.0)

    assert p.context["dt"] == 10.0

    p.finalize()

    assert p.context["h"] is None
