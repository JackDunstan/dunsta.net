"""JSON-valued YAML frontmatter, including indented multiline flow values."""
import json
import re


def field(key, value):
    encoded = json.dumps(value, ensure_ascii=False, indent=2 if key == 'artifacts' else None)
    return key + ': ' + encoded.replace('\n', '\n  ')


def parse(raw):
    front, separator, body = raw.partition('\n---\n')
    if not separator or not front.startswith('---\n'):
        raise ValueError('Expected YAML frontmatter delimited by ---')
    lines = iter(front.splitlines()[1:])
    metadata = {}
    for line in lines:
        if not line.strip():
            continue
        key, separator, value = line.partition(': ')
        if not separator or not re.fullmatch(r'[A-Za-z_][\w-]*', key):
            raise ValueError('Invalid frontmatter field: ' + line)
        while True:
            try:
                metadata[key] = json.loads(value)
                break
            except json.JSONDecodeError as error:
                continuation = next(lines, None)
                if continuation is None or not continuation.startswith((' ', '\t')):
                    raise ValueError('Invalid JSON value for frontmatter field ' + key) from error
                value += '\n' + continuation
    return metadata, body


def replace_field(raw, key, value):
    front, separator, body = raw.partition('\n---\n')
    pattern = r'(?m)^' + re.escape(key) + r':[^\n]*(?:\n[ \t]+[^\n]*)*'
    if re.search(pattern, front):
        front = re.sub(pattern, lambda _: field(key, value), front, count=1)
    else:
        front += '\n' + field(key, value)
    return front + separator + body
