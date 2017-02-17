# encoding: utf-8
import re

def _process_context(match):
    ''' Обработка захваченного контекста (``${context}``) '''
    if not match:
        return ''
    s = match.group(0)
    s = re.sub(r'(.*){(.*?)\.([^\s]*)(.*)}(.*)', r"\1{\2['\3']\4}\5", s)
    return s

_regexps = \
    [(re.compile(r'\s*{if ([^}]+)}\s*'), '% if \\1:'),          # if
     (re.compile(r'\s*{else}\s*'), '% else:'),                  # else
     (re.compile(r'\s*{elseif ([^}]+)}\s*'), '% elif \\1:'),    # elif
     (re.compile(r'\s*{/if}\s*'), '% endif'),                   # endif
     (re.compile(r'\$\{.*?\}'), _process_context),              # ${...}
     (re.compile(r' \|\| '), ' or '),                           # or
     (re.compile(r' \&\& '), ' and '),                          # and
     (re.compile(r'\s*{var ([^}]+)}\s*'), '<% \\1 %>'),         # var
    ]

def js2mako(template):
    ''' Конвертация шаблона Javascript в Mako template '''
    lines = []
    for line in template.splitlines():
        for r, replace in _regexps:
            line = r.sub(replace, line)
        lines.append(line)
    return '\n'.join(lines)


