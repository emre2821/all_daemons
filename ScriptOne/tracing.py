"""Optional tracing initializer.

This module tries to initialize OpenTelemetry tracing. If OpenTelemetry is not
installed, it exposes a no-op tracer so the rest of the app can import
tracing.tracer safely without requiring the dependency.
"""
from typing import Any

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
import ConsoleSpanExporter

    trace.set_tracer_provider(TracerProvider())
    provider = trace.get_tracer_provider()
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    tracer = trace.get_tracer(__name__)
    tracing_enabled = True
except Exception:
    # Minimal no-op tracer replacement
    class _NoopSpan:
        def __enter__(self) -> Any:

            return self

        def __exit__(self, exc_type, exc, tb) -> None:

            return False

    class _NoopTracer:
        def start_as_current_span(self, name: str):

            return _NoopSpan()

    tracer = _NoopTracer()
    tracing_enabled = False

__all__ = ["tracer", "tracing_enabled"]
