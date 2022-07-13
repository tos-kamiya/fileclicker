from typing import Iterable, List, Optional

import re
import shlex
import subprocess
import sys

from docopt import docopt
import portpicker

from . import existing_file_iter
from . import justpy_with_browser


def read_lines(files: Iterable[str]) -> List[str]:
    lines = []
    for f in files:
        if f == '-':
            lines.extend(sys.stdin.readlines())
        else:
            with open(f) as inp:
                lines.extend(inp.readlines())
    lines = [L.rstrip() for L in lines]
    return lines


def build_command_line(command: str, file_name: str, pattern: Optional[re.Pattern], max_capture_number: int) -> List[str]:
    cmd = shlex.split(command)
    if max_capture_number < 0:
        cmd.append(file_name)
    elif pattern is None:
        if max_capture_number != 0:
            sys.exit("Error: no capture in pattern")
        for i, c in enumerate(cmd):
            cmd[i] = c.replace('{0}', file_name)
    else:
        m = pattern.match(file_name)
        if not m:
            assert False, 'pattern match/unmatch inconsistent.'
        if m.lastindex is None:
            if max_capture_number > 0:
                sys.exit("Error: not enough captures in pattern")
        elif m.lastindex < max_capture_number:
            sys.exit("Error: not enough captures in pattern")
        for i, c in enumerate(cmd):
            for j in range(max_capture_number + 1):
                c = c.replace('{%d}' % j, m.group(j))
            cmd[i] = c
    return cmd


ROW_CLASSES = 'p-1 font-mono'
FILE_SPAN_CLASSES = 'p-1 bg-gray-200 hover:bg-gray-400 text-black rounded-full'
FILE_SELECTED_SPAN_CLASSES = 'p-1 bg-gray-600 hover:bg-gray-700 border-1 border-black text-white rounded-full'
FILE_UNSELECTED_MARK = '\u2610'
FILE_SELECTED_MARK = '\u2611'

app_config = {
    'lines': None,
    'pattern': None,
    'dry_run': False,
    'command': None,
    'toggle': False,
}

app_state = {
    'max_caputure_number': -1,
    'item_selection': dict(),  # filename -> bool
}


def setup_config(
        lines: Iterable[str],
        pattern: Optional[re.Pattern] = None,
        command: Optional[str] = None,
        toggle: bool = False,
        dry_run: bool = False) -> None:
    app_config['lines'] = list(lines)
    app_config['pattern'] = pattern
    app_config['dry_run'] = dry_run
    app_config['command'] = command
    app_config['toggle'] = toggle

    max_capture_number = -1
    if command:
        for m in re.finditer(r'{(\d+)}', command):
            n = int(m.group(1))
            if n < 0:
                sys.exit("Error: capture number should be zero or positive: `{%s}`" % m.group(1))
            max_capture_number = max(max_capture_number, n)
    app_state['max_caputure_number'] = max_capture_number


def page_builder():
    import justpy as jp

    def add_span(dest, text):
        for p in re.split(r'( )', text):
            if not p:
                continue
            if p[0] == ' ':
                jp.Space(a=dest, num=len(p))
            else:
                jp.Span(a=dest, text=p)

    pattern = app_config['pattern']
    toggle = app_config['toggle']
    if toggle:
        item_selection = app_state['item_selection']
    else:
        item_selection = dict()  # dummy

    wp = jp.WebPage()
    for L in app_config['lines']:
        d = jp.Div(a=wp, classes=ROW_CLASSES)
        last_p = 0
        for p, k, s in existing_file_iter(L):
            if k == 'file' and (pattern is None or pattern.match(s)):
                if last_p < p:
                    add_span(d, L[last_p:p])
                if toggle:
                    b = jp.Span(a=d, text=FILE_UNSELECTED_MARK + s, classes=FILE_SPAN_CLASSES)
                    item_selection[s] = False
                    b.on('click', file_action_toggle)
                else:
                    b = jp.Span(a=d, text=s, classes=FILE_SPAN_CLASSES)
                    b.on('click', file_action)
                last_p = p + len(s)
            else:
                if last_p < p + len(s):
                    add_span(d, L[last_p:p + len(s)])
                last_p = p + len(s)
        else:
            if last_p < len(L):
                add_span(d, L[last_p:])
    return wp


def file_action(item, msg):
    assert not app_config['toggle']

    command = app_config['command']
    pattern = app_config['pattern']
    dry_run = app_config['dry_run']
    max_capture_number = app_state['max_caputure_number']

    file_name = item.text
    if command is None:
        print("%s" % file_name)
    else:
        cmd = build_command_line(command, file_name, pattern, max_capture_number)

        if dry_run:
            print(shlex.join(cmd))
        else:
            exit_code = subprocess.call(cmd)
            if exit_code != 0:
                sys.exit(exit_code)


def file_action_toggle(item, msg):
    assert app_config['toggle']

    item_selection = app_state['item_selection']

    text = item.text
    file_check, file_name = text[0], text[1:]
    checked = file_check == FILE_SELECTED_MARK
    checked = not checked
    if checked:
        file_check = FILE_SELECTED_MARK
        item_selection[file_name] = True
        item.classes = FILE_SELECTED_SPAN_CLASSES
    else:
        file_check = FILE_UNSELECTED_MARK
        item_selection[file_name] = False
        item.classes = FILE_SPAN_CLASSES
    item.text = file_check + file_name


__doc__ = """Let filenames clickable.

Usage:
  fileclicker [options] <file>...

Options:
  -p PATTERN    Pattern to filter / capture files.
  -c COMMAND    Command line for the clicked file. `{0}` is argument.
  -n            Dry-run. Print commands without running.
  -t            Toggle selection mode.
"""


def main():
    args = docopt(__doc__)
    files = args['<file>']
    pattern_str = args['-p']
    pattern = re.compile(pattern_str) if pattern_str is not None else None
    command = args['-c']
    dry_run = args['-n']
    toggle = args['-t']

    lines = read_lines(files)
    setup_config(lines, pattern=pattern, command=command, toggle=toggle, dry_run=dry_run)

    justpy_with_browser(page_builder, port=portpicker.pick_unused_port())

    if toggle:
        max_capture_number = app_state['max_caputure_number']
        item_selection = app_state['item_selection']

        for file_name, selected in item_selection.items():
            if not selected:
                continue

            if command is None:
                print("%s" % file_name)
            else:
                cmd = build_command_line(command, file_name, pattern, max_capture_number)

                if dry_run:
                    print(shlex.join(cmd))
                else:
                    exit_code = subprocess.call(cmd)
                    if exit_code != 0:
                        sys.exit(exit_code)
