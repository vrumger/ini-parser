# ini-parser

> An ini format parser and serializer for Python.

Sections are treated as nested dictionaries. Items before the first heading are saved on the object directly.

## Usage

Consider an ini-file `config.ini` that looks like this:

```ini
; this comment is being ignored
scope = global

[database]
user = dbuser
password = dbpassword
database = use_this_database

[paths.default]
datadir = /var/lib/data
array[] = first value
array[] = second value
array[] = third value
```

You can read, manipulate and write the ini-file like so:

```python
import ini

config = ini.parse(open('config.ini').read(), preserve_comments=True)

config['scope'] = 'local'
config['database']['database'] = 'use_another_database'
config['paths']['default']['tmpdir'] = '/tmp'
del config['paths']['default']['datadir']
config['paths']['default']['array'].append('fourth value')

with open('config_modified.ini', 'w+') as f:
    f.write(ini.stringify(config, section='section'))
```

This will result in a file called `config_modified.ini` being written to the filesystem with the following content:

```ini
[section]
scope = local

[section.database]
user = dbuser
password = dbpassword
database = use_another_database

[section.paths.default]
array[] = first value
array[] = second value
array[] = third value
array[] = fourth value
tmpdir = /tmp
```

## API

### decode(inistring, on_empty_key=None, preserve_comments=True)

Decode the ini-style formatted `inistring` into a nested object.

-   `on_empty_key`: Value to use when a key with no value is encountered during parsing. If set, any key in the INI file that lacks a value will be assigned this value.
-   `preserve_comments`: Boolean to specify whether to preserve comments when parsing. If set to `True`, comments will be included in the output and parsed from the input. Default is `False`.

### parse(inistring, on_empty_key=None, preserve_comments=True)

Alias for `decode(inistring)`

### encode(object, section=None, whitespace=True)

Encode the object `object` into an ini-style formatted string. If the
optional parameter `section` is given, then all top-level properties
of the object are put into this section and the `section`-string is
prepended to all sub-sections, see the usage example above.

The `options` object may contain the following:

-   `section` - A string which will be the first section in the encoded ini data. Defaults to none.
-   `whitespace` - Boolean to specify whether to put whitespace around the `=` character. By default, whitespace is omitted, to be friendly to some older parsers. If set to `True`, whitespace will be added for readability.

### stringify(object, section=None, whitespace=True)

Alias for `encode(object, [options])`

### safe(val)

Escapes the string `val` such that it is safe to be used as a key or
value in an ini-file. Basically escapes quotes. For example

```python
ini.safe('"unsafe string"')
```

would result in

```python
"\"unsafe string\""
```

### unsafe(val)

Unescapes the string `val`
