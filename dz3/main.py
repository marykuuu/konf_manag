import argparse
import sys
import re
import xml.etree.ElementTree as ET


def convert_element(element, indent=0, constants=None):
    if constants is None:
        constants = {}

    indent_str = '  ' * indent  # Отступ на текущем уровне
    items = []

    # Обработка объявления констант
    if element.tag == 'const':
        name = element.get('name')
        value = element.get('value')
        if name and value:
            sanitized_name = sanitize_name(name)
            constants[sanitized_name] = value
            result = f"{indent_str}(define {sanitized_name} {convert_value(value)})"
            return result
        else:
            raise ValueError(f"Const element должен иметь атрибуты 'name' и 'value'.")

    # Обработка вычисления констант
    elif element.tag == 'compute':
        operation = element.get('op')
        if operation:
            if check_operation(operation):
                splited_operation = operation.split()
                if len(splited_operation) == 2:
                    op = splited_operation[0][2:]
                    const_name = sanitize_name(splited_operation[1][:-1])
                else:
                    op = splited_operation[0][2:]
                    const_name = sanitize_name(splited_operation[1])
                    value = convert_value(splited_operation[2][:-1])
                if const_name in constants:
                    if op == 'abs':
                        print(constants[const_name])
                        result = abs(float(constants[const_name]))
                    else:
                        result = eval(str(constants[const_name]) + op + str(value))
                    return result
                else:
                    raise ValueError(f"Константа '{const_name}' не найдена.")

            else:
                raise ValueError(f"Неверный синтаксис атрибута 'op'.")
        else:
            raise ValueError(f"Элемент 'compute' должен иметь атрибут 'op'.")

    else:
        # Открывающая скобка структуры с правильным отступом
        result = indent_str + "struct @{\n"

        # Обработка атрибутов элемента
        for attr_name, attr_value in element.attrib.items():
            name = sanitize_name(attr_name)
            value = convert_value(attr_value)
            items.append(f"{indent_str}  {name} = {value},")

        # Обработка дочерних элементов
        children = list(element)
        if children:
            # Группировка дочерних элементов по тегам
            child_groups = {}
            for child in children:
                tag = sanitize_name(child.tag)
                if tag not in child_groups:
                    child_groups[tag] = []
                child_groups[tag].append(child)

            for tag, group in child_groups.items():
                if len(group) == 1:
                    # Обработка одного дочернего элемента
                    value = convert_element(group[0], indent + 1, constants)
                    if type(value) == int or type(value) == float:
                        items.append(f"{indent_str}{value},")
                    elif "define" in value:
                        items.append(f"{indent_str}{value},")
                    else:
                        items.append(f"{indent_str}  {tag} = {value},")
                # else:
                #     # Обработка списка (несколько элементов с одинаковыми тегами)
                #     list_items = []
                #     for elem in group:
                #         item = convert_element(elem, indent + 2, constants)
                #         list_items.append(item)
                #     # Формирование списка
                #     list_str = "(list\n" + '\n'.join(list_items) + f"\n{indent_str}  )"
                #     items.append(f"{indent_str}  {tag} = {list_str},")
        else:
            # Обработка текста в элементе
            text = element.text.strip() if element.text else ''
            if text:
                value = convert_value(text)
                return value  # Если это просто текст, возвращаем его напрямую

        result += '\n'.join(items).rstrip(',')  # Убираем лишние запятые
        result += f"\n{indent_str}}}"  # Закрывающая скобка на уровне структуры
        return result


def sanitize_name(name):
    return re.sub(r'[^a-zA-Z0-9]', '_', name.lower())

def check_operation(op):
    pattern1 = r'^\$\(+(\+|\-) [A-Za-z]+ -?[0-9]+(.[0-9]+)?\)$'
    pattern2 = r'^\$\(abs [A-Za-z]+\)$'
    return bool(re.match(pattern1, op)) or bool(re.match(pattern2, op))

def convert_value(value):
    value = value.strip()
    if is_number(value):
        return value
    else:
        return f'"{value}"'


def post_process_config(config_str):
    # Убираем лишние пробелы перед struct, если перед ней стоит знак =
    config_str = re.sub(r'=\s+struct', '= struct', config_str)

    # Убираем лишние пробелы после знака = (делаем один пробел)
    config_str = re.sub(r'=\s+', '= ', config_str)

    return config_str


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def main():
    parser = argparse.ArgumentParser(description='XML to Configuration Language Converter')
    parser.add_argument('-f', '--file', required=True, help='Path to input XML file')
    args = parser.parse_args()

    try:
        tree = ET.parse(args.file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"XML Parse Error: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"File not found: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        config_str = convert_element(root)

        # Выполняем постобработку
        processed_config_str = post_process_config(config_str)

        # Выводим результат
        print(processed_config_str)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()