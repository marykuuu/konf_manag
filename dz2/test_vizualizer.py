import unittest
from main import (
    generate_dot_graph
)

class TestPackageManager(unittest.TestCase):

    def test_generate_dot_graph(self):
        package_name = "TestPackage"
        dependencies = {"Dep1", "Dep2"}
        dot_graph = generate_dot_graph(package_name, dependencies)

        expected_dot = (
            'digraph G {\n'
            '    graph [layout=neato, overlap=scale, splines=true];\n'
            '    "TestPackage"\n'
            '    "TestPackage" -> "Dep2";\n'
            '    "TestPackage" -> "Dep1";\n'
            '}'
        )
        self.assertEqual(dot_graph, expected_dot)

if __name__ == '__main__':
    unittest.main()