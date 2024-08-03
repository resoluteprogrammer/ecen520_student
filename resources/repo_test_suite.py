#!/usr/bin/python3

import pathlib
import argparse
import shutil
import subprocess
import sys
import re
import os
import git

class repo_test_suite():
    ''' This class is used to manage the execution of "tests" within a specific directories
    of a GitHub repository for the purpose of evaluating code within github repositories.

    A key function of this class is to manage the output of the test suite.
    There are two kinds of output generated during the test suite:
    - Command output: The actual output of commands executed as part of a test
    - Test summary: Text that summarizes the test status and results.
    There are three three output targets for this text:
    - stdout: The console output of the test suite. 
    - summary log file: A file that contains the summary of the test output.
    - Command specific log files: Files for a specific test output to isolate the output from other tests

    repo: This is the git.Repo object that represents the local repository being tested.
          This class is not involved in preparing or changing the repository and an existing
          valid repository is assumed. The repository is used to find the repo directory
          (repo.working_tree_dir) and find individual files within the repo.
    tests_to_perform: A list of "repo_test" objects that represent a specific test to perform.
    working_dir: The directory in which the tests should be executed. Note that the execution
                 directory can be anywhere and not necessarily within the repository.
    log_dir: the directory where logs generated during the test will be generated.
            This can be None if no output file logging is wanted.
    summary_log_filename: The name of the file where a summary of the test output will be written.

    '''

    def __init__(self, repo, working_dir = None, print_to_stdout = True, verbose = False, summary_log_filename = None, log_dir = None, ):
        # Reference to the Git repository
        self.repo = repo
        self.repo_root_path = pathlib.Path(repo.git.rev_parse('--show-toplevel'))
        # The path to the directory where the top-level script has been run
        self.script_path = os.getcwd()
        # Directory where tests should be completed. This may be different from the script_path
        self.working_path = pathlib.Path(working_dir)
        if working_dir is None:
            self.working_path = self.script_path
        # Relative repo path
        self.relative_repo_path = self.working_path.relative_to(self.repo_root_path)        
        # Directory of the logs
        self.log_dir = log_dir
        self.tests_to_perform = [] # list of test_module objects
        self.print_to_stdout = print_to_stdout
        self.verbose = verbose
        self.test_log_fp = None
        if summary_log_filename:
            summary_log_filepath = self.log_dir + '/' + summary_log_filename
            self.test_log_fp = open(summary_log_filepath, "w")
            if not self.test_log_fp:
                self.print_error("Error opening file for writing:", summary_log_filepath)

    def add_test_module(self, test_module):
        ''' Add a test module. '''
        self.tests_to_perform.append(test_module)

    def print(self, message, verbose_message = False):
        """ Prints a string to the appropriate locations. """
        # Print to std_out?
        if not verbose_message or self.verbose:
            if self.print_to_stdout:
                print(message)
            if self.test_log_fp:
                self.test_log_fp.write(message + '\n')

    def print_error(self, message):
        """ Prints a string to the appropriate locations. """
        # Print to std_out?
        print(message)

    def print_test_status(self, message):
        self.print(message)

    def run_tests(self):
        ''' Run all the registered tests '''
        for idx, test in enumerate(self.tests_to_perform):
            self.print_test_status(f"Step {idx+1}.")
            #self.print_step_message(test.module_name())
            self.execute_test_module(test)
        # Wrap up
        #self.print_message_summary()
        #self.clean_up_test()

    def execute_test_module(self, test_module):
        ''' Executes the 'perform_test' function of the tester_module and logs its result in the log file '''

        # Check to see if the test should proceed
        # if not self.proceed_with_tests:
        #     print("Skipping test",test_module.module_name(),"due to previous errors")
        #     return False

        module_name = test_module.module_name()
        result = test_module.perform_test()
        if result:
            self.print(str.format("Success:{}\n",module_name))
        else:
            self.print_error(str.format("Failed:{}\n",module_name))
        return result

# Static methods
def create_from_path(path = None):
    ''' Create a repo_test_suite object from a path. If no path is given,
    the current directory is used. '''
    if path is None:
        path = os.getcwd()
    repo = git.Repo(path, search_parent_directories=True)
    return repo_test_suite(repo, path)

