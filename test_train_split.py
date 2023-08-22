import argparse
from glob import glob
import os
import random
import unittest
import shutil
import tempfile
import sys


def test_train_split(input_directory, output_test, verbose=False,
                     file_extension='', pattern_expansion='*',
                     num_test=-1, percent_test=-1.0):

    random.seed(123)

    if num_test != -1 and percent_test != -1:
        er_str = "num_test and percent_test cannot be specified at the same"
        er_str += " time, pick one or the other"
        raise RuntimeError(er_str)

    glob_input = os.path.join(input_directory, pattern_expansion
                              + file_extension)

    filenames = glob(glob_input)

    if verbose:
        print('Found', len(filenames), 'files, randomly splitting...')

    # Get number of files to move to test
    if num_test != -1:
        num_test = num_test
    elif percent_test != -1:
        num_test = int((percent_test/100) * len(filenames))
    else:
        er_str = "Either percent_test or num_test must be specified"
        raise RuntimeError(er_str)

    if num_test > len(filenames):
        er_str = "Number of test files exceeds total number of files"
        raise RuntimeError(er_str)

    # Randomly shuffle files
    random.shuffle(filenames)
    # Move files to specified folders
    verbose_print_freq = 10000
    for i in range(num_test):
        if verbose and i % verbose_print_freq == 0:
            print('.', end='')
        f = filenames[i]
        f_bn = os.path.basename(f)
        f_out = os.path.join(output_test, f_bn)
        if os.path.exists(f_out):
            er_str = "Output file " + f_out + " already exists"
            raise RuntimeError(er_str)
        os.rename(f, f_out)

    if verbose:
        print()


class TestSplitFiles(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        # Create three subdirectories with some files
        self.subdirs = []
        self.files = []
        for i in range(2):
            subdir = os.path.join(self.test_dir, f"subdir{i}")
            os.mkdir(subdir)
            self.subdirs.append(subdir)
            files = [f"file{j}" for j in range(10)]
            self.files.append(files)
            # Make files only in first subdir
            if i == 0:
                for file in files:
                    with open(os.path.join(subdir, file), "w") as f:
                        f.write("some content")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_split_files(self):
        test_train_split(self.subdirs[0], self.subdirs[1],
                         file_extension='', pattern_expansion='*',
                         num_test=5)
        for directory in self.subdirs:
            files = os.listdir(directory)
            self.assertEqual(len(files), 5)


if __name__ == "__main__":  # pragma: no cover

    parser = argparse.ArgumentParser()

    parser.add_argument('--test', action='store_true',
                        help='Run tests on the app rather than running the app')
    # Only required if --test is not specified
    parser.add_argument('--input_directory', '-i', required='--test' not in sys.argv, type=str,
                        help='Directory to move files from')
    parser.add_argument('--output_test', '-o', required='--test' not in sys.argv, type=str,
                        help='directory to move files to')
    # Verbose flag
    parser.add_argument("-v", "--verbose", action="store_true",
                        default=False, help="Verbose output")

    parser.add_argument('-e', '--file_extension', default='', type=str,
                        help='Type of file to look for in the input directory')

    parser.add_argument('-p', '--pattern_expansion', default='*',
                        help=('Unix style pattern expansion like *., used' +
                        ' before file extension, i.e. if file_extension is ' +
                        'tif, and pattern_expansion is *., it will look ' +
                        'for input_directory/*.tif'))

    parser.add_argument("-n", "--num_test", type=int, default=-1,
                        help="Number of files to move to test directory")

    parser.add_argument("-r", "--percent_test", type=float, default=-1.0,
                        help="Percent of files to move to test directory")

    args, unknown = parser.parse_known_args()

    if args.test:
        unittest.main(argv=[sys.argv[0]] + unknown)
    else:
        test_train_split(args.input_directory,
                         args.output_test,
                         args.verbose,
                         args.file_extension,
                         args.pattern_expansion,
                         args.num_test,
                         args.percent_test)
