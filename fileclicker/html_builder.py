from typing import List, Optional
import re

from .file_finder import existing_file_iter


def html_builder(lines: List[str], pattern: Optional[re.Pattern] = None) -> str:
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


def markdown_builder(lines: List[str], pattern: Optional[re.Pattern] = None) -> str:
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


