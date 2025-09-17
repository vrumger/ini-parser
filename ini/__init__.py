import json
import re

__version__ = '2.0.1'


class ini_dict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._comments = {}


def _parse_value(value):
    if isinstance(value, str):
        if value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
            return int(value)
        if re.match(r'^\d*\.\d+$', value):
            return float(value)
    return value


def encode(obj, section=None, whitespace=True):
    children = []
    out = ''
    separator = ' = ' if whitespace else '='
    comments = dict(obj._comments) if isinstance(obj, ini_dict) else {}

    for i, (k, v) in enumerate(obj.items()):
        if i in comments:
            for comment in comments[i]:
                out += comment + '\n'
            del comments[i]

        if isinstance(v, list):
            if len(v) == 0:
                out += safe(k) + separator + "'[]'" + '\n'
            for item in v:
                out += safe(k + '[]') + separator + safe(item) + '\n'
        elif isinstance(v, dict):
            children.append(k)
        else:
            out += safe(k) + separator + safe(v) + '\n'

    for comments in comments.values():
        for comment in comments:
            out += comment + '\n'

    if section:
        out = '[' + safe(section) + ']' + '\n' + out

    for k in children:
        nk = '.'.join(_dot_split(k))
        child_section = (section + '.' if section else '') + nk
        child = encode(obj[k], section=child_section, whitespace=whitespace)
        if len(out) and len(child):
            out += '\n'
        out += child

    return out


def _dot_split(string):
    return re.sub(r'\\\.', '\u0001', string).split('.')


EMPTY_KEY_SENTINEL = object()


def decode(string, on_empty_key=EMPTY_KEY_SENTINEL, preserve_comments=False):
    out = ini_dict() if preserve_comments else {}
    p = out
    section = None
    regex = re.compile(
        r'^(\s*[;#])|^\[([^\]]*)\]$|^([^=]+)(=(.*))?$', re.IGNORECASE,
    )
    lines = re.split(r'[\r\n]+', string)

    for line in lines:
        if not line:
            continue
        match = regex.match(line)
        if not match:
            continue
        if match[1]:
            if preserve_comments:
                p._comments[len(p)] = p._comments.get(len(p), [])
                p._comments[len(p)].append(line)
            continue
        if match[2]:
            section = unsafe(match[2])
            p = out[section] = out.get(
                section, ini_dict() if preserve_comments else {},
            )
            continue
        key = unsafe(match[3])
        if match[4]:
            if match[5].strip():
                value = _parse_value(unsafe(match[5]))
            elif on_empty_key is EMPTY_KEY_SENTINEL:
                raise ValueError(key)
            else:
                value = on_empty_key
        else:
            value = True
        if value in ('true', 'True'):
            value = True
        elif value in ('false', 'False'):
            value = False
        elif value in ('null', 'None'):
            value = None

        # Convert keys with '[]' suffix to an array
        if len(key) > 2 and key[-2:] == '[]':
            key = key[:-2]
            if key not in p:
                p[key] = []
            elif not isinstance(p[key], list):
                p[key] = [p[key]]

        # safeguard against resetting a previously defined
        # array by accidentally forgetting the brackets
        if isinstance(p.get(key), list):
            p[key].append(value)
        else:
            p[key] = value

    # {a:{y:1},"a.b":{x:2}} --> {a:{y:1,b:{x:2}}}
    # use a filter to return the keys that have to be deleted.
    _out = ini_dict(out) if preserve_comments else dict(out)
    if preserve_comments:
        _out._comments = out._comments
    for k in _out.keys():
        if (
            not out[k] or
            not isinstance(out[k], dict) or
            isinstance(out[k], list)
        ):
            continue
        # see if the parent section is also an object.
        # if so, add it to that, and mark this one for deletion
        parts = _dot_split(k)
        p = out
        l = parts.pop()  # noqa: E741
        nl = re.sub(r'\\\.', '.', l)
        for part in parts:
            if part not in p or not isinstance(p[part], dict):
                p[part] = {}
            p = p[part]
        if p == out and nl == l:
            continue
        p[nl] = out[k]
        del out[k]

    return out


def _is_quoted(val):
    return (
        (val[0] == '"' and val[-1] == '"') or
        (val[0] == "'" and val[-1] == "'")
    )


def safe(val):
    if (
        not isinstance(val, str) or
        re.match(r'[=\r\n]', val) or
        re.match(r'^\[', val) or
        (len(val) > 1 and _is_quoted(val)) or
        val != val.strip()
    ):
        return json.dumps(val)

    return val.replace(';', '\\;').replace('#', '\\#')


def unsafe(val):
    val = (val or '').strip()
    if _is_quoted(val):
        # remove the single quotes before calling JSON.parse
        if val[0] == "'":
            val = val[1:-1]
        try:
            val = json.loads(val)
        except json.JSONDecodeError:
            pass
    else:
        # walk the val to find the first not-escaped ; character
        esc = False
        unesc = ''
        for i in range(len(val)):
            c = val[i]
            if esc:
                if c in '\\;#':
                    unesc += c
                else:
                    unesc += '\\' + c
                esc = False
            elif c in ';#':
                break
            elif c == '\\':
                esc = True
            else:
                unesc += c
        if esc:
            unesc += '\\'
        return unesc.strip()
    return val


parse = decode
stringify = encode
