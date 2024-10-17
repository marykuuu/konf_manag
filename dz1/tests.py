import unittest
from dz1.emulator import ShellEmulator

class Test(unittest.TestCase):

    def setUp(self):
        self.emul = ShellEmulator("dz1/file_system.tar")

#----------------------test ls function--------------------------------
    def test_ls_1(self):
        output = self.emul.ls()
        self.assertIn("home", output)
        self.assertIn("etc", output)
        self.assertIn("empty", output)

    def test_ls_2(self):
        output = self.emul.ls("home/user")
        self.assertIn("file.txt", output)
        self.assertIn("file2.txt", output)

    def test_ls_3(self):
        output = self.emul.ls("empty")
        self.assertEqual(output, "")

    # ----------------------test cd function--------------------------------

    def test_cd_1(self):
        self.emul.cd("home")
        self.assertEqual(self.emul.path, "./file_system/home/")

    def test_cd_2(self):
        output = self.emul.cd("dir")
        self.assertEqual(output, "cd: ./file_system/dir: No such directory")

    def test_cd_3(self):
        self.emul.cd("home")
        self.emul.cd("../")
        self.assertEqual(self.emul.path, "./file_system/")

    # ----------------------test mv function--------------------------------

    def test_mv_1(self):
        self.emul.cd("home")
        self.emul.mv("user/file.txt", "new_file.txt")
        output = self.emul.ls()
        self.assertTrue(output== "user\nnew_file.txt" or "new_file.txt\nuser")


    def test_mv_2(self):
        self.emul.cd("home")
        self.emul.mv("new_file.txt", "user/file.txt")
        output = self.emul.ls()
        self.assertTrue(output == "user")

    def test_mv_3(self):
        self.emul.cd("home")
        output = self.emul.mv("no_file.txt", "data")
        self.assertEqual(output, "mv: cannot stat './file_system/home/no_file.txt': No such file or directory")

    # --------------test rev function------------------

    def test_rev_1(self):
        self.emul.cd("home/user")
        res = self.emul.rev("file.txt")
        self.assertEqual(res, "1 акортС\n2 акортС\n3 акортС")

    def test_rev_2(self):
        self.emul.cd("home/user")
        res = self.emul.rev("user")
        self.assertEqual(res, "rev: 'user': no such file")

    def test_rev_3(self):
        res = self.emul.rev("home/user/file2.txt")
        self.assertEqual(res, "muspi meroL\n2 enil\n321")

    # --------------test tac function------------------

    def test_tac_1(self):
        self.emul.cd("home/user")
        res = self.emul.tac("file.txt")
        self.assertEqual(res, "Строка 3\nСтрока 2\nСтрока 1")

    def test_tac_2(self):
        res = self.emul.tac("home/user/file2.txt")
        self.assertEqual(res, "123\nline 2\nLorem ipsum")

    def test_tac_3(self):
        res = self.emul.tac("not_file.txt")
        self.assertEqual(res, "tac: 'not_file.txt': No such file")


    if __name__ == "__main__":
        unittest.main()