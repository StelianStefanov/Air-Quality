"""Best-effort resource release and graceful process termination."""

from contextlib import contextmanager
import signal


def close_resources(logger, *resources):
    """Attempt every close without hiding the error that caused shutdown."""
    for resource in resources:
        if resource is not None:
            try:
                resource.close()
            except Exception as error:
                logger.exception(error)


@contextmanager
def handle_sigterm():
    """Let service entry points unwind their finally blocks on SIGTERM."""
    def terminate(signum, frame):
        raise SystemExit(128 + signum)

    previous = signal.signal(signal.SIGTERM, terminate)
    try:
        yield
    finally:
        signal.signal(signal.SIGTERM, previous)
