import unittest
import contextlib
import os
import tempfile

from fileclicker.file_finder import existing_file_iter


@contextlib.contextmanager
def back_to_curdir():
    curdir = os.getcwd()
    try:
        yield
    finally:
        os.chdir(curdir)


def touch(file_name: str):
    with open(file_name, "w") as outp:
        print("", end="", file=outp)


class FindItemIterTest(unittest.TestCase):
    def test_files(self):
        with tempfile.TemporaryDirectory() as tempdir:
            with back_to_curdir():
                os.chdir(tempdir)

                touch("a.txt")
                touch("b.txt")

                L = "hoge hoge a.txt hoge b.txt hoge c.txt hoge hoge"
                items = list(pks for pks in existing_file_iter(L) if pks[1] is not None)
                self.assertEqual(len(items), 2)
                self.assertEqual(items[0][2], 'a.txt')
                self.assertEqual(items[1][2], 'b.txt')

    def test_dirs(self):
        with tempfile.TemporaryDirectory() as tempdir:
            with back_to_curdir():
                os.chdir(tempdir)

                os.mkdir('d')

                touch("a.txt")
                touch("d/a.txt")

                L = "hoge hoge b.txt hoge d/a.txt"
                items = list(pks for pks in existing_file_iter(L) if pks[1] is not None)
                self.assertEqual(len(items), 1)
                self.assertEqual(items[0][2], 'd/a.txt')
