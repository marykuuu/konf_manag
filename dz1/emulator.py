import os
import tarfile
import argparse
import io


class ShellEmulator:
    def __init__(self, fs_path):
        self.fs_path = fs_path
        self.current_path = './file_system'
        self.path = './' + fs_path.split('/')[-1].replace(".tar", "") + "/"


    def get_path(self, path):
        path = path.split("/")
        result_path = self.path
        if path[0] == "" and len(path) > 1:
            result_path = "./file_system/"
            path = path[1:]
        for elem in path:
            if elem == "..":
                result_path = "/".join(result_path.split("/")[:-2]) + "/"
            elif elem == ".":
                continue
            else:
                result_path += elem + "/"
            result_path = result_path.replace("//", "/")
        return result_path


    def ls(self, append_path=""):
        path = self.get_path(append_path)
        elems = set()
        with tarfile.open(self.fs_path, "r") as tar:
            for member in tar.getmembers():
                if not member.name.startswith(path):
                    continue
                elems.add(member.name.split("/")[path.count("/")])

        return "\n".join(elems)


    def cd(self, path):
        self.path = self.path.replace("//", "/")
        if type(path) != list:
            path = path.split("/")
        if path[0] == "" and len(path) > 1:
            self.path = "/".join(self.path.split("/")[:2]) + "/"
            return self.cd(path[1:])
        if path[0] == "":
            return

        if path[0] == "..":
            if self.path == "./file_system/":
                return self.cd(path[1:])
            self.path = "/".join(self.path.split("/")[:-2]) + "/"
            return self.cd(path[1:])
        elif path[0] == ".":
            return self.cd(path[1:])
        else:
            with tarfile.open(self.fs_path, "r") as tar:
                for member in tar.getmembers():
                    if member.name == self.path + "/".join(path) and \
                            member.isdir():
                        break
                else:
                    return f"cd: {self.path + "/".join(path)}: No such directory"

            self.path += "/".join(path) + "/"
            self.path = self.path.replace("//", "/")


    def mv(self, source, destination):
        source_path = self.get_path(source)[:-1]
        dest_path = self.get_path(destination)[:-1]
        flag = 0

        with tarfile.open(self.fs_path, 'r') as tar:
            new_tar_stream = io.BytesIO()
            with tarfile.open(fileobj=new_tar_stream, mode='w') as new_tar:
                for member in tar.getmembers():
                    if member.name == source_path:
                        member.name = dest_path
                        flag=1
                    new_tar.addfile(member, tar.extractfile(member))
                if flag == 0:
                    return(f"mv: cannot stat '{source_path}': No such file or directory")

        with open(self.fs_path, 'wb') as f:
            f.write(new_tar_stream.getvalue())


    def rev(self, filename):
        path = self.get_path(filename)[:-1]
        with tarfile.open(self.fs_path, "r") as tar:
            for member in tar.getmembers():
                if member.name == path and member.isfile():
                    break
            else:
                return f"rev: '{filename}': no such file"

            with tar.extractfile(member) as f:
                lines = f.readlines()
                lines = [line.decode("utf-8").rstrip('\n')[::-1] for line in lines]
                return '\n'.join(lines)

    def tac(self, filename):
        path = self.get_path(filename)[:-1]
        with tarfile.open(self.fs_path, "r") as tar:
            for member in tar.getmembers():
                if member.name == path and member.isfile():
                    break
            else:
                return f"tac: '{filename}': No such file"

            with tar.extractfile(member) as f:
                content = f.readlines()
                lines = [line.decode("utf-8").rstrip('\n') for line in reversed(content)]
                return '\n'.join(lines)

    def execute(self, command):
        args = command.split()
        if not args:
            return

        cmd = args[0]
        if cmd == 'exit':
            print("Exiting shell emulator...")
            return True
        elif cmd == 'ls':
            print(self.ls(args[1] if len(args) > 1 else ""))
        elif cmd == 'cd':
            error = self.cd(args[1])
            if error:
                print(error)
            self.current_path = self.path
        elif cmd == 'mv':
            if len(args) > 2:
                print(self.mv(args[1], args[2]))
            else:
                print("mv: missing operand")
        elif cmd == 'rev':
            if len(args) > 1:
                print(self.rev(args[1]))
            else:
                print("rev: missing operand")
        elif cmd == 'tac':
            if len(args) > 1:
                print(self.tac(args[1]))
            else:
                print("tac: missing operand")
        else:
            print(f"{cmd}: command not found")


def main(archive, start_script):
    if not os.path.exists(archive):
        print(f"Ошибка: Архив '{archive}' не найден.")
        return
    if not os.path.exists(start_script):
        print(f"Ошибка: Скрипт '{start_script}' не найден.")
        return

    shell = ShellEmulator(archive)

    # Выполнение стартового скрипта
    if os.path.exists(start_script):
        with open(start_script, 'r') as file:
            for line in file:
                exit_status = shell.execute(line.strip())
                if exit_status:
                    break

    # Интерфейс командной строки
    while True:
        command = input(f"{shell.current_path}$ ")
        exit_status = shell.execute(command)
        if exit_status:
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Запуск виртуальной файловой системы с указанным скриптом.')
    parser.add_argument('archive', help='Путь к архиву виртуальной файловой системы')
    parser.add_argument('start_script', help='Путь к стартовому скрипту')

    args = parser.parse_args()
    main(args.archive, args.start_script)