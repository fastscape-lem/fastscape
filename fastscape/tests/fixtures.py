from contextlib import contextmanager

from fastscape.processes.context import FastscapelibContext


@contextmanager
def fastscape_context(shape=(3, 4), length=(10.0, 30.0)):
    p = FastscapelibContext(shape=shape, length=length)
    p.initialize()

    try:
        yield p.context
    finally:
        p.finalize()
