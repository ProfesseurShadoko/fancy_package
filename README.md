
# fancy_package

A small collection of lightweight, opinionated utilities for printing "fancy" console output in Python: colored strings, pretty messages, simple progress bars, task context managers, and tiny system/status helpers.

This package is designed for developer convenience when running short scripts or CLI-style tasks. It provides a few cooperating classes that make it easy to print colored, indented, and optionally muted output, plus a couple of helpers for memory and time display.

## Features

- Colored strings with convenient format specifiers (`cstr`) — easy ANSI coloring and simple format shortcuts.
- `Message` class for categorized, pretty messages (info, warning, error, success).
- `Task` context manager to wrap and time operations, with neat completion/abort output.
- `ProgressBar` iterator wrapper with estimated remaining time and non-intrusive whisper messages.
- `MutableClass` base with global mute/tab behavior so multiple components coordinate console output.
- Small status helpers: `MemoryView`, `TODO` and `DateTime` for quick runtime info.

## Installation

You can downlaod the package from my GitHub repository with this command:
```bash
pip install git+https://github.com/ProfesseurShadoko/fancy_package.git
```

## Quick examples

Colored strings

```python
from fancy_package import cstr
print(cstr('hello world').green().bold())
print(f"Progress: {cstr('ok'):g}")  # short color spec
```

Pretty messages

```python
from fancy_package import Message
Message("Build succeeded", "#")       # green success prefix
Message("Something might be wrong", "?")
```

Tasks and timing

```python
from fancy_package import Task
import time

with Task("Compute important thing"):
	time.sleep(1.2)

with Task("Quiet task", new_line=False):
	time.sleep(0.3)
```

Progress bar

```python
from fancy_package import ProgressBar
import time

for i in ProgressBar(range(50), size=50):
	time.sleep(0.02)
	if i == 25:
		ProgressBar.whisper("Halfway there!")
```

Status helpers

```python
from fancy_package import MemoryView, TODO
MemoryView()              # prints a short memory usage line (requires psutil)
TODO("Refactor the parser")
```

Mute and indentation

```python
from fancy_package import MutableClass, Message

MutableClass.mute()       # globally mute printing
MutableClass.unmute()

with Message("The following messages will be indented"):   # increase indentation for nested prints
	Message.print("This will be indented")
    MemoryView() # also indented
Message("This won't be indented")
```

## Examples

Run the command:
```bash
python -m fancy_package.<filename_without_dot_py>
```
to see examples of what can be done with this package!


## Development notes

- The package is intentionally tiny and uses ANSI escape sequences for coloring; compatibility is best on UNIX-like terminals.
- `MemoryView` depends on `psutil` — consider making that optional or guarding import-time behavior in environments where `psutil` is not available.
- There are simple demo blocks in each module under `if __name__ == '__main__'` for manual testing.
