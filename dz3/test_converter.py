import pytest
import xml.etree.ElementTree as ET
from main import convert_element, post_process_config

def clean_output(output):
    """
    Очистка вывода для тестов: удаление лишних запятых и пробелов в конце.
    """
    output = output.strip()
    # Удаление последней запятой перед закрывающей фигурной скобкой, если она есть
    output = output.replace(",\n}", "\n}")
    return output

def test_simple_struct():
    xml = """<person>
                <cnt>1.0</cnt>
                <age>30</age>
             </person>"""
    root = ET.fromstring(xml)
    config = post_process_config(convert_element(root))
    expected = '''struct @{
  cnt = 1.0,
  age = 30
}
'''
    assert clean_output(config) == clean_output(expected)


def test_constants():
    xml = """<root>
                <const name="PI" value="3.14"/>
             </root>"""
    root = ET.fromstring(xml)
    config = post_process_config(convert_element(root))
    expected = '''struct @{
  (define pi 3.14),
}
'''
    assert clean_output(config) == clean_output(expected)

def test_error_handling():
    xml = """<root>
                <compute name="UNKNOWN"/>
             </root>"""
    root = ET.fromstring(xml)
    with pytest.raises(ValueError):
      post_process_config(convert_element(root))

def test_operation():
    xml = """<root>
                <const name="a" value="3"/>
                <compute op="$(+ a -4.5)"/>
             </root>"""
    root = ET.fromstring(xml)
    config = post_process_config(convert_element(root))
    expected = '''struct @{
  (define a 3),
-1.5
}
'''
    assert clean_output(config) == clean_output(expected)