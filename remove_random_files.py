import os
import random
import argparse
import unittest
import sys
import tempfile
import shutil


def remove_files(directories, n, seed):
    random.seed(seed)
    files = os.listdir(directories[0])
    indexes = range(len(files))
    for _ in range(n):
        i = random.choice(indexes)
        file = files[i]
        indexes = range(len(indexes) - 1)
        files.remove(file)
        for directory in directories:
            os.remove(os.path.join(directory, file))


class TestRemoveFiles(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        # Create three subdirectories with some files
        self.subdirs = []
        self.files = []
        for i in range(3):
            subdir = os.path.join(self.test_dir, f"subdir{i}")
            os.mkdir(subdir)
            self.subdirs.append(subdir)
            files = [f"file{j}" for j in range(10)]
            self.files.append(files)
            for file in files:
                with open(os.path.join(subdir, file), "w") as f:
                    f.write("some content")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_remove_files(self):
        remove_files(self.subdirs, 5, 0)
        for directory in self.subdirs:
            files = os.listdir(directory)
            self.assertEqual(len(files), 5)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remove the same n random files from all directories. '
                                     'Note this app assumes the directories all have the same files')
    parser.add_argument('--test', action='store_true',
                        help='Run tests on the app rather than running the app')
    # Only required if --test is not specified
    parser.add_argument('--directories', '-d', required='--test' not in sys.argv, type=str, nargs='+',
                        help='directories to remove files from')
    parser.add_argument('-n', '--num', type=int, required='--test' not in sys.argv,
                        help='the number of files to remove from each directory')
    parser.add_argument('--seed', metavar='s', type=int, default=0,
                        help='the seed for the random number generator')
    args, unknown = parser.parse_known_args()

    if args.test:
        unittest.main(argv=[sys.argv[0]] + unknown)
    else:
        remove_files(args.directories, args.num, args.seed)
