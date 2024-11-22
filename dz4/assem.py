# -*- coding: cp1251 -*-
#python assem.py assembl.txt prog.bin log.json
import struct
import json  # ���������� JSON ������ YAML
import sys

COMMANDS = {
    'LOAD_CONST': 164,  # 0x2C
    'READ_MEM': 144,    # 0x3B
    'WRITE_MEM': 29,   # 0x30
    'RCL': 74      # 0x4A
}

def parse_instruction(line):
    """
    ��������� ������ ��������� ���� �� ������� � ���������.
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
    �������� ������� � �������� ������ (1 ���� ��� �������, 2 ����� ��� ���������).
    """
    opcode = COMMANDS.get(command)
    if opcode is None:
        raise ValueError(f"����������� �������: {command}")

    if command in { 'READ_MEM', 'WRITE_MEM', 'RCL'} and len(args) == 1:
        arg_bytes = struct.pack(">H", args[0])[::-1]  # 2 ����� ��������� � �������� �������
        return struct.pack(">B", opcode) + arg_bytes
    elif command == 'LOAD_CONST' and len(args) == 1:
        # 8 ��� ������� + 8 ��� ���������
        arg_byte = args[0] & 0xFF  # ��������� ������ ������� 8 ��� ���������
        return struct.pack(">BB", opcode, arg_byte)


    raise ValueError(f"�������� ��������� ��� ������� {command}: {args}")

def assemble(source_path, binary_path, log_path):
    """
    ��������� �������� ����, ������ �������� ���� � �������� ���������� � ������� JSON.
    """
    log_data = []
    with open(source_path, 'r') as source_file, open(binary_path, 'wb') as binary_file:
        for line in source_file:
            command, args = parse_instruction(line)
            if command:
                binary_instruction = encode_instruction(command, args)
                binary_file.write(binary_instruction)
                
                # �������� �������� ������ � ���������� �������
                log_data.append({
                    "command": command,
                    "args": args,
                    "hex": " ".join(f"{byte:02X}" for byte in binary_instruction)
                })

    with open(log_path, 'w') as log_file:
        json.dump(log_data, log_file, indent=4)  # ���������� JSON ������ YAML

def hex_dump(file_path):
    """
    �������� ���������� ��������� ����� � ����������������� �������.
    """
    with open(file_path, "rb") as f:
        data = f.read()
        print("����� � program.bin:")
        print(" ".join(f"{byte:02X}" for byte in data))
        print("������ ���������� ������� ���������")

if __name__ == "__main__":
    source_path = sys.argv[1]
    binary_path = sys.argv[2]
    log_path = sys.argv[3]
    assemble(source_path, binary_path, log_path)
    hex_dump(binary_path)
