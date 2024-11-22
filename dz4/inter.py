# -*- coding: cp1251 -*-
import struct
import random
#import yaml
import sys
import json
from random import randint

memory = [0] * 1024
#registers = [0] * 32

def rcl(value, bit_count):
    """
    ��������� ��������� ����������� ����� ����� �� 1 ���.
    ������� ��� ���������� �������, ��������� ���� ���������� �����.

    :param value: ����� ��� ������.
    :param bit_count: ���������� �������� ���.
    :return: ��������� ������������ ������.
    """
    # ��������� ������� ���
    msb = (value >> (bit_count - 1)) & 1  # ��������� ����� ����� ���
    # �������� ����� ����� � ��������� ������� ��� � ������� ������
    shifted = ((value << 1) & ((1 << bit_count) - 1)) | msb
    return shifted





def rcl_op(binary_file):
    """
    ��������� ������� RCL: ����������� ����� ������������� ����� (������ + ����).
    """
    # ��������� 2 ����� ���������
    arg_bytes = struct.unpack(">BB", binary_file.read(2))  # ������ ��� �����
    address = (arg_bytes[1] << 8) | arg_bytes[0]  # �������� ����� � ���������� �������

    # �������� ��������� ������
    if address >= len(memory):
        raise IndexError(f"����� {address} ������� �� ������� ������.")

    # �������� �������� �� ������ �� ���������� ������
    memory_value = memory[address]

    # ��������� �������� � ������� �����
    mem_value =  memory[0]

    # ���������� ���������� �������� ���
    def count_significant_bits(value):
        return max(1, len(bin(value)) - 2)  # ����������� ������� 1 ��� ���� ��� 0

    memory_bits = count_significant_bits(memory_value)
    stack_bits = count_significant_bits(mem_value)
    total_bits = memory_bits + stack_bits

    # ����������: �������� ������ ������, ���� �����
    combined_binary = (mem_value << memory_bits) | memory_value
   

    # ��������� ������ �������� ����
    combined_binary &= (1 << total_bits) - 1  # ����� ��� ������� �� total_bits
    print(f"RCL: ������������ ����: {combined_binary:b}")
  
    # ����������� ����� ������������� �����
    result = rcl(combined_binary, total_bits)
    print(f"RCL: ��������� ����� ������: {result:b} ({result})")




def load_const(binary_file):
    """
    ��������� ������� LOAD_CONST: ��������� �������� �� ����.
    """
    arg_byte = struct.unpack(">B", binary_file.read(1))[0]
    memory[0] = arg_byte

    print(f"LOAD_CONST: {arg_byte} �������� � ������ �� ������ {0}")

def read_mem(binary_file):
    """
    ��������� ������� READ_MEM: ��������� �������� �� ������.
    """
    arg_bytes = struct.unpack(">BB", binary_file.read(2))[::-1]  # ������ � ������ ������� ������
    addr = (arg_bytes[0] << 8) | arg_bytes[1]
    memory[0] = memory[addr]
    print(f"READ_MEM: �������� {memory[addr]} ��������� �� ������ �� ������ {addr}")

def write_mem(binary_file):
    """
    ��������� ������� WRITE_MEM: ���������� �������� � ������.
    """
    arg_bytes = struct.unpack(">BB", binary_file.read(2))[::-1]  # ������ � ������ ������� ������
    addr = (arg_bytes[0] << 8) | arg_bytes[1]

    memory[addr] = memory[0]
   
    print(f"WRITE_MEM: �������� {memory[0]} �������� � ������ �� ������ {addr}")



COMMAND_EXECUTORS = {
    164: load_const,   # LOAD_CONST
    144: read_mem,     # READ_MEM
    29: write_mem,     # WRITE_MEM
    74: rcl_op     # RCL
}


def get_memory_dump(memory):
    """���������� ���������� ������ � ���� �������."""
    return {f"address_{i}": value for i, value in enumerate(memory)}

def interpret(binary_path, result_path, start, end):
    """
    �������������� ������� �� ��������� �����.
    """
    for i in range(start, end):
        memory[i] = randint(start, end)
    with open(binary_path, 'rb') as binary_file:
        print("������ �������������:")

        while True:
            opcode_byte = binary_file.read(1)
            if not opcode_byte:
                break  # ����� �����

            opcode = struct.unpack(">B", opcode_byte)[0]
            print(f"������ opcode: {opcode}")

            executor = COMMAND_EXECUTORS.get(opcode)
            if executor:
                executor(binary_file)
            else:
                raise ValueError(f"����������� ������� � �����: {opcode}")

    with open(result_path, "w") as f:
        json.dump(get_memory_dump(memory), f, indent=4)
    print(f"Memory dump saved to {result_path}")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("�������������: python inter.py <binary_path> <result_path> <start> <end>")
        sys.exit(1)
    
    binary_path = sys.argv[1]
    result_path = sys.argv[2]
    start = int(sys.argv[3])
    end = int(sys.argv[4])

    interpret(binary_path, result_path, start, end)
