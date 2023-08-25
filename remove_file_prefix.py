from glob import glob
import os
import argparse
import sys
import unittest
import tempfile


def remove_file_prefix (dir, glob_str, delim='_', len=1):
    files = glob(os.path.join(dir, glob_str))
    for file in files:
        parts = os.path.basename(file).split(delim)
        fn = ''
        for part in parts[len:]:
            fn += part + delim
        fn = fn[0:-1]
        os.rename(file, os.path.join(dir, fn))


class TestRemoveFilePrefix(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.TemporaryDirectory()
        # Create some files with prefixes in the directory
        self.files = ['a_b_c.txt', 'a_d_e.txt', 'a_f_g.txt']
        for file in self.files:
            open(os.path.join(self.test_dir.name, file), 'a').close()

    def tearDown(self):
        # Remove the directory after the test
        self.test_dir.cleanup()

    def test_remove_file_prefix(self):
        # Call the function with the directory and glob pattern
        remove_file_prefix(self.test_dir.name, '*.txt')
        # Check if the files have been renamed correctly
        expected_files = ['b_c.txt', 'd_e.txt', 'f_g.txt']
        actual_files = os.listdir(self.test_dir.name)
        self.assertCountEqual(actual_files, expected_files)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true',
                        help='Run tests on the app rather than running the app')
    parser.add_argument('--dir', '-d', required='--test' not in sys.argv, type=str,
                        help='the directory where the files are located')
    parser.add_argument('--glob-str', '-g', type=str, help='The glob pattern to match the files')
    parser.add_argument('--delim', '-e', type=str, default='_', help='The delimiter to split the file name')
    parser.add_argument('--len', '-l', type=int, default=1, help='The number of parts to remove from the file name')
    args, unknown = parser.parse_known_args()
    if args.test:
        unittest.main(argv=[sys.argv[0]] + unknown)
    else:
        remove_file_prefix(args.dir, args.glob_str, args.delim, args.len)
