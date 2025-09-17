from ini import _parse_value
from ini import decode
from ini import encode
from ini import ini_dict
from ini import safe
from ini import unsafe


def test_encode_simple_dict():
    data = {'key': 'value', 'num': 42}
    result = encode(data)
    assert 'key = value' in result
    assert 'num = 42' in result


def test_encode_with_section():
    data = {'section': {'key': 'value'}}
    result = encode(data)
    assert '[section]' in result
    assert 'key = value' in result


def test_encode_list():
    data = {'arr': [1, 2, 3]}
    result = encode(data)
    assert 'arr[] = 1' in result
    assert 'arr[] = 2' in result
    assert 'arr[] = 3' in result


def test_decode_simple():
    ini_str = 'key = value\nnum = 42'
    result = decode(ini_str)
    assert result['key'] == 'value'
    assert result['num'] == 42


def test_decode_section():
    ini_str = '[section]\nkey = value'
    result = decode(ini_str)
    assert 'section' in result
    assert result['section']['key'] == 'value'


def test_decode_list():
    ini_str = 'arr[] = 1\narr[] = 2\narr[] = 3'
    result = decode(ini_str)
    assert result['arr'] == [1, 2, 3]


def test_decode_boolean_and_null():
    ini_str = 'flag = true\nnoneval = null'
    result = decode(ini_str)
    assert result['flag'] is True
    assert result['noneval'] is None


def test_safe_and_unsafe():
    val = 'some;value'
    safe_val = safe(val)
    assert '\\;' in safe_val
    assert unsafe(safe_val) == val


def test_parse_value():
    assert _parse_value('42') == 42
    assert _parse_value('-42') == -42
    assert _parse_value('3.14') == 3.14
    assert _parse_value('text') == 'text'


def test_preserve_comments():
    ini_str = '; comment\nkey = value'
    result = decode(ini_str, preserve_comments=True)
    assert isinstance(result, ini_dict)
    assert 0 in result._comments


def test_decode_multisection_with_comments():
    ini_str = (
        '; root comment\n\n'
        '[asd]\n'
        '; comment\n'
        'one = two\n'
        '\n'
        '[asd.dfg]\n'
        '; comment1\n'
        'three = four\n'
        '; comment2\n'
        'five = six\n'
        'seven = eight\n'
        '; comment 4\n'
        '; comment 3\n'
    )

    result = decode(ini_str, preserve_comments=True)
    assert 'asd' in result
    assert 'dfg' in result['asd']
    assert result['asd']['one'] == 'two'
    assert result['asd']['dfg']['three'] == 'four'
    assert result['asd']['dfg']['five'] == 'six'
    assert result['asd']['dfg']['seven'] == 'eight'

    encoded = encode(result)
    assert encoded == ini_str
