# -*- coding: cp1251 -*-
#python assem.py assembl.txt prog.bin log.json
import struct
import json  # Используем JSON вместо YAML
import sys

COMMANDS = {
    'LOAD_CONST': 164,  # 0x2C
    'READ_MEM': 144,    # 0x3B
    'WRITE_MEM': 29,   # 0x30
    'RCL': 74      # 0x4A
}

def parse_instruction(line):
    """
    Разбирает строку исходного кода на команду и аргументы.
    """
    line = line.split('#', 1)[0].strip()
    if not line:
        return None, None

    parts = line.split()
    command = parts[0]
    args = [int(part) for part in parts[1:]]
    return command, args

def encode_instruction(command, args):
    """
    Кодирует команду в бинарный формат (1 байт для команды, 2 байта для аргумента).
    """
    opcode = COMMANDS.get(command)
    if opcode is None:
        raise ValueError(f"Неизвестная команда: {command}")

    if command in { 'READ_MEM', 'WRITE_MEM', 'RCL'} and len(args) == 1:
        arg_bytes = struct.pack(">H", args[0])[::-1]  # 2 байта аргумента в обратном порядке
        return struct.pack(">B", opcode) + arg_bytes
    elif command == 'LOAD_CONST' and len(args) == 1:
        # 8 бит команды + 8 бит аргумента
        arg_byte = args[0] & 0xFF  # Учитываем только младшие 8 бит аргумента
        return struct.pack(">BB", opcode, arg_byte)


    raise ValueError(f"Неверные аргументы для команды {command}: {args}")

def assemble(source_path, binary_path, log_path):
    """
    Считывает исходный файл, создаёт бинарный файл и логирует инструкции в формате JSON.
    """
    log_data = []
    with open(source_path, 'r') as source_file, open(binary_path, 'wb') as binary_file:
        for line in source_file:
            command, args = parse_instruction(line)
            if command:
                binary_instruction = encode_instruction(command, args)
                binary_file.write(binary_instruction)
                
                # Логируем бинарные данные в правильном порядке
                log_data.append({
                    "command": command,
                    "args": args,
                    "hex": " ".join(f"{byte:02X}" for byte in binary_instruction)
                })

    with open(log_path, 'w') as log_file:
        json.dump(log_data, log_file, indent=4)  # Используем JSON вместо YAML

def hex_dump(file_path):
    """
    Печатает содержимое бинарного файла в шестнадцатеричном формате.
    """
    with open(file_path, "rb") as f:
        data = f.read()
        print("Байты в program.bin:")
        print(" ".join(f"{byte:02X}" for byte in data))
        print("Работа ассемблера успешно завершена")

if __name__ == "__main__":
    source_path = sys.argv[1]
    binary_path = sys.argv[2]
    log_path = sys.argv[3]
    assemble(source_path, binary_path, log_path)
    hex_dump(binary_path)
