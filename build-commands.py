"""Build the file commands/__init__.py."""

import os
import os.path
import re

command_match = re.compile(r'^class ([^(]+)\(([^)]+)\)\:')

header = """# commands/__init__.py: Command-related imports.
#
# This file is created by build-commands.py and should not be hand-edited.
"""

commands_dir = 'commands'
commands_file = '__init__.py'
ignored_files = ('base.py', '__init__.py')
stuff = {}

for filename in os.listdir(commands_dir):
    path = os.path.join(commands_dir, filename)
    if filename in ignored_files or not os.path.isfile(path):
        continue
    short = filename.split('.')[0]
    with open(path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            m = command_match.match(line)
            if m is None:
                continue
            command, bases = m.groups()
            if 'Command' not in bases:
                continue
            results = stuff.get(short, [])
            results.append(command)
            stuff[short] = results
if __name__ == '__main__':
    with open(os.path.join(commands_dir, commands_file), 'w') as f:
        f.write(header)
        command_names = []
        for module, names in stuff.items():
            for name in names:
                command_names.append(name)
                f.write(f'\nfrom .{module} import {name}')
        f.write('\n\n__all__ = [\n')
        for name in command_names:
            f.write(f"    '{name}',\n")
        f.write(']\n')
    print(f'Command names written to {commands_dir}\{commands_file}.')
