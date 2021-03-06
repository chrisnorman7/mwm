"""Provides the Intercept class."""

from attr import attrs, attrib, Factory


@attrs
class Intercept:
    """Allows text to be gathered from the user, bypassing normal command
    processing."""

    func = attrib()
    args = attrib(default=Factory(tuple))
    kwargs = attrib(default=Factory(dict))
    multiline = attrib(default=Factory(bool))
    lines = attrib(default=Factory(list))
    end = attrib(default=Factory(lambda: '.'))
    abort = attrib(default=Factory(lambda: '@abort'))
    connection = attrib(default=Factory(lambda: None))

    def feed(self, line):
        """Add text to self.text."""
        if line == self.abort:
            self.connection.notify('Aborted.')
            self.connection.intercept = None
        self.lines.append(line)
        if not self.multiline or line == self.end:
            if self.multiline:
                # We don't want the end character in the buffer.
                self.lines.pop()
            self.connection.intercept = None
            self.func('\n'.join(self.lines), *self.args, **self.kwargs)
