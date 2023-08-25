import tempfile
import shutil
import unittest
import sys
import argparse
import os
from tqdm import tqdm


def check_directories(directories, remove=False, verbose=False):
    """
    Check if all directories have the same files.
    :param directories: list of directories to check
    :param remove: remove files that do not exist in all directories
    """

    if len(directories) < 2:
        print("only 1 directory specified, nothing to do")
        return

    if verbose:
        print('Processing', len(directories), 'directories.')
        print('Finding all unique files in each directory...')

    # Get a set of all files in each directory
    file_sets = []
    itr = directories
    if verbose:
        itr = tqdm(directories)
    for directory in itr:
        file_set = set(os.listdir(directory))
        file_sets.append(file_set)

    if verbose:
        print("Found all sets, finding set intersection of all files...")
    intersection = set.intersection(*file_sets)

    # Check to see if all the files in all directories are the same
    all_same_files = True
    itr = file_sets
    if verbose:
        print('Checking to make sure all directories contain only files in set intersect...')
        itr = tqdm(file_sets)
    for file_set in itr:
        if len(file_set) != len(intersection):
            all_same_files = False
            break
        for file in file_set:
            if not file in intersection:
                all_same_files = False
                break
        if not all_same_files:
            break

    if all_same_files:
        print('All directories have the same files.')
        return True
    else:
        print('Not all directories have the same files.')
        # Remove files that do not exist in all directories
        if remove:
            itr = directories
            if verbose:
                itr = tqdm(directories)
            for i, directory in enumerate(itr):
                file_set = file_sets[i]
                for file in file_set:
                    if file not in intersection:
                        os.remove(os.path.join(directory, file))
        return False


# Test class for your function
class TestCheckDirectories(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()

        # Create three subdirectories with some files
        self.subdirs = []
        self.files = []
        for i in range(3):
            subdir = os.path.join(self.test_dir, f"subdir{i}")
            os.mkdir(subdir)
            self.subdirs.append(subdir)
            files = [f"file{j}" for j in range(3)]
            self.files.append(files)
            for file in files:
                with open(os.path.join(subdir, file), "w") as f:
                    f.write("some content")
        # Remove one file from the first subdirectory
        os.remove(os.path.join(self.subdirs[0], self.files[0][0]))

    def tearDown(self):
        # Remove the temporary directory after the test
        shutil.rmtree(self.test_dir)

    def test_check_directories_same(self):
        # Test if the function correctly detects that all directories have the same files
        self.assertTrue(check_directories(self.subdirs[1:]))

    def test_check_directories_different(self):
        # Test if the function correctly detects that not all directories have the same files
        self.assertFalse(check_directories(self.subdirs))

    def test_check_directories_remove(self):
        # Test if the function correctly removes files that do not exist in all directories
        self.assertFalse(check_directories(self.subdirs, remove=True))
        self.assertEqual(len(os.listdir(self.subdirs[0])), 2)
        self.assertEqual(len(os.listdir(self.subdirs[1])), 2)
        self.assertEqual(len(os.listdir(self.subdirs[2])), 2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check if all directories have the same files.')
    parser.add_argument('--test', action='store_true',
                        help='Run tests on the app rather than running the app')
    # Only required if --test is not specified
    parser.add_argument('--directories', '-d', required='--test' not in sys.argv, type=str, nargs='+',
                        help='directories to check')
    parser.add_argument('--remove', '-r', action='store_true',
                        help='remove files that do not exist in all directories')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output and loading bars')
    #args = parser.parse_args()
    args, unknown = parser.parse_known_args()
    if args.test:
        unittest.main(argv=[sys.argv[0]] + unknown)
    else:
        check_directories(args.directories, args.remove, args.verbose)
