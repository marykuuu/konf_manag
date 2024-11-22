import argparse
import os
import json
import subprocess
import shutil

#Пример использования
#cd dz2
#python main.py C:/Users/user/Graphviz/bin/dot.exe express https://github.com/expressjs/express
#Путь к программе для визуализации графов
visualizer_path = "C:/Users/user/Graphviz/bin/dot.exe"
#Имя анализируемого пакета
package_name = "express"
#URL-адрес репозитория.
repository_url = "https://github.com/expressjs/express"

def get_dependencies(package_name, repo_url):
    # Клонируем репозиторий
    subprocess.run(['git', 'clone', repo_url])

    # Путь к директории с пакетом
    package_dir = os.path.join(os.getcwd(), package_name)

    # Получаем файл package.json
    with open(os.path.join(package_dir, 'package.json')) as f:
        data = json.load(f)

    dependencies = data.get('dependencies', {})

    return dependencies


def build_graph(dependencies, graph):
    for package, version in dependencies.items():
        # Добавляем узлы
        graph.node(package, package)
        # Задает зависимости от пакета
        if 'devDependencies' in dependencies:
            for dep in dependencies['devDependencies']:
                graph.edge(package, dep)

def download_and_get_deps(url, package_name):
    dependencies = get_dependencies(package_name, url)
    return dependencies

def generate_dot_graph(package_name, dependencies):
    dot = 'digraph G {\n'
    dot += '    graph [layout=neato, overlap=scale, splines=true];\n'
    dot += f'    "{package_name}"\n'
    for dep in dependencies:
        dot += f'    "{package_name}" -> "{dep}";\n'
    dot += '}'
    return dot

def visualize_graph(visualizer_path, dot_graph):
    file_path = os.path.join(os.getcwd(), 'graph.dot')
    with open(file_path, 'w', encoding='utf-8') as dot_file:
        dot_file.write(dot_graph)

    output_png = os.path.join(os.getcwd(), 'graph.png')
    subprocess.run([visualizer_path, '-Tpng', file_path, '-o', output_png], check=True)

    print(f"Граф зависимостей сохранен в: {output_png}")


def main():
    parser = argparse.ArgumentParser(description="Visualize JavaScript package dependencies.")
    parser.add_argument('visualizer_path', type=str, help='Path to a visualizer program')
    parser.add_argument('package_name', type=str, help='Name of the package to analyze')
    parser.add_argument('repo_url', type=str, help='URL of the repository')

    args = parser.parse_args()

    print("Визуализация графа зависимостей для пакета: ", args.package_name)
    dependencies = download_and_get_deps(args.repo_url, args.package_name)
    print("[i] Построение графа ...")
    dot_graph = generate_dot_graph(args.package_name, dependencies)
    visualize_graph(args.visualizer_path, dot_graph)


if __name__ == "__main__":
    main()
