import unittest

from fileclicker import pathlike_iter


class PathlikeIterTest(unittest.TestCase):
    def test_find_paths_from_tree_output(self):
        lines = """
.
├── fileclicker
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-38.pyc
│   │   └── file_url_finder.cpython-38.pyc
│   └── file_url_finder.py
├── setup.cfg
└── tests
    ├── __init__.py
    ├── __pycache__
    │   ├── __init__.cpython-38.pyc
    │   └── test_file_url_finder.cpython-38.pyc
    ├── test_file_url_finder.py
    └── test_pathlike_iter.py
"""[1:-1].split('\n')

        expected_items = [
            "fileclicker", "__init__.py", "__pycache__", "__init__.cpython-38.pyc", "file_url_finder.cpython-38.pyc",
            "file_url_finder.py", "setup.cfg", "tests", "__init__.py", "__pycache__", "__init__.cpython-38.pyc",
            "test_file_url_finder.cpython-38.pyc", "test_file_url_finder.py", "test_pathlike_iter.py"
        ]

        pathlikes = []
        for L in lines:
            pathlikes.extend(pathlike_iter(L))

        for i in expected_items:
            for pos, pathstr in pathlikes:
                if pathstr.startswith(i):
                    break  # for pos, pathstr
            else:
                self.assertTrue(False, "item not extracted: %s" % i)

    def test_find_paths_from_ls_r_output(self):
        lines = """
.:
fileclicker/  setup.cfg  tests/

./fileclicker:
__init__.py  __pycache__/  file_url_finder.py

./fileclicker/__pycache__:
__init__.cpython-38.pyc  file_url_finder.cpython-38.pyc

./tests:
__init__.py  __pycache__/  test_file_url_finder.py  test_pathlike_iter.py

./tests/__pycache__:
__init__.cpython-38.pyc  test_file_url_finder.cpython-38.pyc  test_pathlike_iter.cpython-38.pyc
"""[1:-1].split('\n')

        expected_items = [
            "setup.cfg", "__init__.py", "file_url_finder.py", "__init__.cpython-38.pyc", "file_url_finder.cpython-38.pyc",
            "__init__.py", "test_file_url_finder.py", "test_pathlike_iter.py",
            "__init__.cpython-38.pyc", "test_file_url_finder.cpython-38.pyc", "test_pathlike_iter.cpython-38.pyc"
        ]

        pathlikes = []
        for L in lines:
            pathlikes.extend(pathlike_iter(L))

        for i in expected_items:
            for pos, pathstr in pathlikes:
                if pathstr.startswith(i):
                    break  # for pos, pathstr
            else:
                self.assertTrue(False, "item not extracted: %s" % i)

    def test_find_paths_from_find_output(self):
        lines = """
.
./fileclicker
./fileclicker/file_url_finder.py
./fileclicker/__pycache__
./fileclicker/__pycache__/__init__.cpython-38.pyc
./fileclicker/__pycache__/file_url_finder.cpython-38.pyc
./fileclicker/__init__.py
./setup.cfg
./tests
./tests/__pycache__
./tests/__pycache__/test_file_url_finder.cpython-38.pyc
./tests/__pycache__/__init__.cpython-38.pyc
./tests/__pycache__/test_pathlike_iter.cpython-38.pyc
./tests/test_pathlike_iter.py
./tests/test_file_url_finder.py
./tests/__init__.py
"""[1:-1].split('\n')

        expected_items = lines[1:]  # '.' is not extracted as path

        pathlikes = []
        for L in lines:
            pathlikes.extend(pathlike_iter(L))

        for pos, pathstr in pathlikes:
            self.assertEqual(pos, 0)

        for i in expected_items:
            for pos, pathstr in pathlikes:
                if pathstr == i:
                    break  # for pos, pathstr
            else:
                self.assertTrue(False, "item not extracted: %s" % i)

    def test_find_paths_abspaths(self):
        lines = """
/home/toshihiro/hoge
The system-wide directory for log data is /var/log.
The user-specific config directory is ~/.config/.
The relative path to current directory such as ./hoge.sh or ../fuga.sh.
Many whitespace chars such as   c.txt   \t\td.txt
"""[1:-1].split('\n')

        expected_items = ['/home/toshihiro/hoge', '/var/log', '~/.config/', './hoge.sh', '../fuga.sh', 'c.txt', 'd.txt']

        pathlikes = []
        for L in lines:
            pathlikes.extend(pathlike_iter(L))

        for i in expected_items:
            for pos, pathstr in pathlikes:
                if pathstr.startswith(i):
                    break  # for pos, pathstr
            else:
                self.assertTrue(False, "item not extracted: %s" % i)

