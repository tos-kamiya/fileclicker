from typing import Iterable, List, Optional
from dataclasses import dataclass, field

import re
import shlex
import subprocess
import sys

from docopt import docopt

from .file_finder import existing_file_iter


def read_lines(files: Iterable[str]) -> List[str]:
    lines = []
    for f in files:
        if f == "-":
            lines.extend(sys.stdin.readlines())
        else:
            with open(f) as inp:
                lines.extend(inp.readlines())
    lines = [L.rstrip() for L in lines]
    return lines


def build_command_line(
    command: str, file_name: str, pattern: Optional[re.Pattern], max_capture_number: int
) -> List[str]:
    cmd = shlex.split(command)
    if max_capture_number < 0:
        cmd.append(file_name)
    elif pattern is None:
        if max_capture_number != 0:
            sys.exit("Error: no capture in pattern")
        for i, c in enumerate(cmd):
            cmd[i] = c.replace("{0}", file_name)
    else:
        m = pattern.match(file_name)
        if not m:
            assert False, "pattern match/unmatch inconsistent."
        if m.lastindex is None:
            if max_capture_number > 0:
                sys.exit("Error: not enough captures in pattern")
        elif m.lastindex < max_capture_number:
            sys.exit("Error: not enough captures in pattern")
        for i, c in enumerate(cmd):
            for j in range(max_capture_number + 1):
                c = c.replace("{%d}" % j, m.group(j))
            cmd[i] = c
    return cmd


@dataclass
class AppConfig:
    lines: List[str] = field(default_factory=list)
    pattern: Optional[re.Pattern] = None
    dry_run: bool = False
    command: Optional[str] = None
    toggle: bool = False
    max_capture_number: int = -1


app_config = AppConfig()


app_state = {
    "item_selection": dict(),  # filename -> bool
}


def setup_config(
    lines: Iterable[str],
    pattern: Optional[re.Pattern] = None,
    command: Optional[str] = None,
    toggle: bool = False,
    dry_run: bool = False,
) -> None:
    app_config.lines = list(lines)
    app_config.pattern = pattern
    app_config.dry_run = dry_run
    app_config.command = command
    app_config.toggle = toggle

    max_capture_number = -1
    if command:
        for m in re.finditer(r"{(\d+)}", command):
            n = int(m.group(1))
            if n < 0:
                sys.exit("Error: capture number should be zero or positive: `{%s}`" % m.group(1))
            max_capture_number = max(max_capture_number, n)
    app_config.max_capture_number = max_capture_number


def exec_for_file(file_name: str) -> None:
    A = app_config
    if A.command is None:
        print("%s" % file_name)
    else:
        cmd = build_command_line(A.command, file_name, A.pattern, A.max_capture_number)

        if A.dry_run:
            print(shlex.join(cmd))
        else:
            exit_code = subprocess.call(cmd)
            if exit_code != 0:
                sys.exit(exit_code)


ROW_CLASSES = "p-1 font-mono"
FILE_SPAN_CLASSES = "p-1 bg-gray-200 hover:bg-gray-400 text-black rounded-full"
FILE_SELECTED_SPAN_CLASSES = "p-1 bg-gray-600 hover:bg-gray-700 border-1 border-black text-white rounded-full"
FILE_UNSELECTED_MARK = "\u2610"
FILE_SELECTED_MARK = "\u2611"


def page_builder():
    import justpy as jp

    def add_span(dest, text):
        for p in re.split(r"( )", text):
            if not p:
                continue
            if p[0] == " ":
                jp.Space(a=dest, num=len(p))
            else:
                jp.Span(a=dest, text=p)

    A = app_config
    if A.toggle:
        item_selection = app_state["item_selection"]
    else:
        item_selection = dict()  # dummy

    wp = jp.WebPage()
    for L in A.lines:
        d = jp.Div(a=wp, classes=ROW_CLASSES)
        last_p = 0
        for p, k, s in existing_file_iter(L):
            if k == "file" and (A.pattern is None or A.pattern.match(s)):
                if last_p < p:
                    add_span(d, L[last_p:p])
                if A.toggle:
                    b = jp.Span(a=d, text=FILE_UNSELECTED_MARK + s, classes=FILE_SPAN_CLASSES)
                    item_selection[s] = False
                    b.on("click", file_action_toggle)
                else:
                    b = jp.Span(a=d, text=s, classes=FILE_SPAN_CLASSES)
                    b.on("click", file_action)
                last_p = p + len(s)
            else:
                if last_p < p + len(s):
                    add_span(d, L[last_p : p + len(s)])
                last_p = p + len(s)
        else:
            if last_p < len(L):
                add_span(d, L[last_p:])
    return wp


def file_action(item, msg):
    assert not app_config.toggle

    file_name = item.text
    exec_for_file(file_name)


def file_action_toggle(item, msg):
    assert app_config.toggle

    item_selection = app_state["item_selection"]

    text = item.text
    file_check, file_name = text[0], text[1:]

    checked = file_check == FILE_SELECTED_MARK
    checked = not checked

    item_selection[file_name] = checked
    if checked:
        file_check = FILE_SELECTED_MARK
        item.classes = FILE_SELECTED_SPAN_CLASSES
    else:
        file_check = FILE_UNSELECTED_MARK
        item.classes = FILE_SPAN_CLASSES
    item.text = file_check + file_name


def html_builder(lines: List[str], pattern: Optional[re.Pattern] = None):
    import html
    import htmlBuilder.tags as ht
    from htmlBuilder.attributes import Href, Style

    def span_iter(text):
        for p in re.split(r"( )", text):
            if not p:
                continue
            if p[0] == " ":
                yield ht.Span([], "&nbsp;" * len(p))
            else:
                yield ht.Span([], html.escape(p))

    divs = []
    for L in lines:
        spans = []
        last_p = 0
        for p, k, s in existing_file_iter(L):
            if k == "file" and (pattern is None or pattern.match(s)):
                if last_p < p:
                    spans.extend(span_iter(L[last_p:p]))
                spans.append(ht.A([Href(s)], html.escape(s)))
                last_p = p + len(s)
            else:
                if last_p < p + len(s):
                    spans.extend(span_iter(L[last_p : p + len(s)]))
                last_p = p + len(s)
        else:
            if last_p < len(L):
                spans.extend(span_iter(L[last_p:]))
        divs.append(ht.Div([], *spans))

    return ht.Html([Style(font='monospace')], *divs).render(doctype=True, pretty=True)


def markdown_builder(lines: List[str], pattern: Optional[re.Pattern] = None):
    divs = []
    for L in lines:
        spans = []
        last_p = 0
        for p, k, s in existing_file_iter(L):
            if k == "file" and (pattern is None or pattern.match(s)):
                if last_p < p:
                    spans.extend(L[last_p:p])
                spans.append("[%s](%s)" % (s, s))
                last_p = p + len(s)
            else:
                if last_p < p + len(s):
                    spans.extend(L[last_p : p + len(s)])
                last_p = p + len(s)
        else:
            if last_p < len(L):
                spans.extend(L[last_p:])
        divs.append(''.join(spans) + '  ')

    return '\n'.join(divs)


__doc__ = """Identify filenames in text and show the text as a clickable page.

Usage:
  fileclicker [-p PATTERN|-c COMMAND|-n|-x] <file>...
  fileclicker [-M|-H|-p PATTERN] <file>...

Options:
  -p PATTERN        Pattern to filter / capture files.
  -c COMMAND        Command line for the clicked file. `{0}` is argument.
  -n --dry-run      Print commands without running.
  -x --check        Check mode. Select files with check box.
  -M --markdown     Markdown mode. Output markdown text.
  -H --html         HTML mode. Output html text.
"""


def main():
    args = docopt(__doc__)
    pattern_str = args["-p"]
    pattern = re.compile(pattern_str) if pattern_str is not None else None

    lines = read_lines(args["<file>"])

    if args['--markdown']:
        print(markdown_builder(lines, pattern=pattern))
        return
    elif args['--html']:
        print(html_builder(lines, pattern=pattern))
        return

    setup_config(lines, pattern=pattern, command=args["-c"], toggle=args["--check"], dry_run=args["--dry-run"])

    from .justpy_with_browser import justpy_with_browser
    import portpicker

    justpy_with_browser(page_builder, port=portpicker.pick_unused_port())

    if app_config.toggle:
        item_selection = app_state["item_selection"]
        for file_name, selected in item_selection.items():
            if selected:
                exec_for_file(file_name)
