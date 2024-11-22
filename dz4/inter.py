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
    Выполняет побитовый циклический сдвиг влево на 1 бит.
    Старший бит становится младшим, остальные биты сдвигаются влево.

    :param value: Число для сдвига.
    :param bit_count: Количество значащих бит.
    :return: Результат циклического сдвига.
    """
    # Извлекаем старший бит
    msb = (value >> (bit_count - 1)) & 1  # Извлекаем самый левый бит
    # Сдвигаем число влево и добавляем старший бит в младший разряд
    shifted = ((value << 1) & ((1 << bit_count) - 1)) | msb
    return shifted





def rcl_op(binary_file):
    """
    Выполняет команду RCL: циклический сдвиг объединенного числа (память + стек).
    """
    # Считываем 2 байта аргумента
    arg_bytes = struct.unpack(">BB", binary_file.read(2))  # Читаем два байта
    address = (arg_bytes[1] << 8) | arg_bytes[0]  # Собираем адрес в правильном порядке

    # Проверка диапазона адреса
    if address >= len(memory):
        raise IndexError(f"Адрес {address} выходит за пределы памяти.")

    # Получаем значение из памяти по указанному адресу
    memory_value = memory[address]

    # Извлекаем значение с вершины стека
    mem_value =  memory[0]

    # Определяем количество значащих бит
    def count_significant_bits(value):
        return max(1, len(bin(value)) - 2)  # Гарантируем минимум 1 бит даже для 0

    memory_bits = count_significant_bits(memory_value)
    stack_bits = count_significant_bits(mem_value)
    total_bits = memory_bits + stack_bits

    # Объединяем: значение памяти справа, стек слева
    combined_binary = (mem_value << memory_bits) | memory_value
   

    # Оставляем только значащие биты
    combined_binary &= (1 << total_bits) - 1  # Маска для обрезки до total_bits
    print(f"RCL: объединенные биты: {combined_binary:b}")
  
    # Циклический сдвиг объединенного числа
    result = rcl(combined_binary, total_bits)
    print(f"RCL: результат после сдвига: {result:b} ({result})")




def load_const(binary_file):
    """
    Выполняет команду LOAD_CONST: добавляет значение на стек.
    """
    arg_byte = struct.unpack(">B", binary_file.read(1))[0]
    memory[0] = arg_byte

    print(f"LOAD_CONST: {arg_byte} записано в память по адресу {0}")

def read_mem(binary_file):
    """
    Выполняет команду READ_MEM: считывает значение из памяти.
    """
    arg_bytes = struct.unpack(">BB", binary_file.read(2))[::-1]  # Читаем и меняем порядок байтов
    addr = (arg_bytes[0] << 8) | arg_bytes[1]
    memory[0] = memory[addr]
    print(f"READ_MEM: значение {memory[addr]} прочитано из памяти по адресу {addr}")

def write_mem(binary_file):
    """
    Выполняет команду WRITE_MEM: записывает значение в память.
    """
    arg_bytes = struct.unpack(">BB", binary_file.read(2))[::-1]  # Читаем и меняем порядок байтов
    addr = (arg_bytes[0] << 8) | arg_bytes[1]

    memory[addr] = memory[0]
   
    print(f"WRITE_MEM: значение {memory[0]} записано в память по адресу {addr}")



COMMAND_EXECUTORS = {
    164: load_const,   # LOAD_CONST
    144: read_mem,     # READ_MEM
    29: write_mem,     # WRITE_MEM
    74: rcl_op     # RCL
}


def get_memory_dump(memory):
    """Возвращает содержимое памяти в виде словаря."""
    return {f"address_{i}": value for i, value in enumerate(memory)}

def interpret(binary_path, result_path, start, end):
    """
    Интерпретирует команды из бинарного файла.
    """
    for i in range(start, end):
        memory[i] = randint(start, end)
    with open(binary_path, 'rb') as binary_file:
        print("Начало интерпретации:")

        while True:
            opcode_byte = binary_file.read(1)
            if not opcode_byte:
                break  # Конец файла

            opcode = struct.unpack(">B", opcode_byte)[0]
            print(f"Считан opcode: {opcode}")

            executor = COMMAND_EXECUTORS.get(opcode)
            if executor:
                executor(binary_file)
            else:
                raise ValueError(f"Неизвестная команда с кодом: {opcode}")

    with open(result_path, "w") as f:
        json.dump(get_memory_dump(memory), f, indent=4)
    print(f"Memory dump saved to {result_path}")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Использование: python inter.py <binary_path> <result_path> <start> <end>")
        sys.exit(1)
    
    binary_path = sys.argv[1]
    result_path = sys.argv[2]
    start = int(sys.argv[3])
    end = int(sys.argv[4])

    interpret(binary_path, result_path, start, end)
