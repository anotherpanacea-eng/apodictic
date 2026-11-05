### Native validator worker lifecycle

Windows validator workers launch the interpreter image already running the coordinator, avoiding premature cancellation or timeout completion through a virtual-environment redirector. Interpreter-image resolution fails unavailable without a launcher fallback. Native protocol lifecycle checks observe actual worker exit through held Windows process handles and preserve POSIX signal/reaping coverage. The fixed leaf inventory and request protocol are unchanged; signed desktop availability and abrupt coordinator-death containment remain unqualified.
