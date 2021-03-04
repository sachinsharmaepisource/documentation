"""
	Logic:
	It wil check docstring format as per standards.
	Then it will create review messages on the pull request.
"""
import os
import os.path
import sys
import json
from pprint import pprint
import requests
from github import Github
from pylint.lint import Run
from pylint.reporters.text import TextReporter
from pylint import epylint as lint
#-------------------------------------------------------------------
class WritableObject(object):
    "dummy output stream for pylint"
    def __init__(self):
        self.content = []
    def write(self, st):
        "dummy write"
        self.content.append(st)
    def read(self):
        "dummy read"
        return self.content

class CheckDocstrings:
  """
  CheckDocstrings
  Logic:
	It wil check docstring format as per standards.
	Then it will create review messages on the pull request.
  """
  def __init__(self):
#     Initialization of following variables
    self.repo_name = self.get_inputs('REPO_NAME')
    self.pr_title = self.get_inputs('PR_TITLE')
    self.pr_number = self.get_inputs('PR_NUMBER')
    self.access_token = self.get_inputs('ACCESS_TOKEN')
    self.user_name = self.get_inputs('USER_NAME')
    self.action_type = self.get_inputs('ACTION_TYPE')
    self.current_branch = self.get_inputs('CURRENT_BRANCH')
    self.gh_ = Github(self.access_token)
    self.repo = self.gh_.get_repo(self.user_name)
    if self.pr_number:
      self.current_branch = self.repo.get_pull(int(self.pr_number)).head.ref
    self.branch = self.repo.get_branch(self.current_branch)
    self.header = {'Authorization': f'token {self.access_token}'}
    self.report_dct = { 'errors': [], 'convention': [], 'refactor': [], 'warning': [] }
    self.report_dct_in_pr_rev_cmnt = { 'convention': [] }
    self.label = '[CHECK DOCSTRINGS]'
    self.help_link = 'https://numpydoc.readthedocs.io/en/latest/example.html'

    
  def get_inputs(self, input_name):
    """
      Parameters
      ----------
          input_name: String
          
      Logic
      ----------
          Extract the inputs from the YML file of GITHUB ACTION
      Return
      ----------
          Input: String
    """
    return os.getenv('INPUT_{}'.format(input_name).upper())
  
  def delete_all_previous_bot_generated_review_comments(self, pull_number):
    """
      Parameters
      ----------
          pull_number: Int
            Pull number of the current pull request
      Logic
      ----------
          Delete all the review comments generated by github action bot
      Return
      ----------
          None
    """
    pr_ = self.repo.get_pull(int(pull_number))
    review_comments = pr_.get_review_comments()
    for review_comment in review_comments:
      comment_desc_label = review_comment.body.split('\n', 1)[0].strip()
      if review_comment.user.type == 'Bot' and comment_desc_label == self.label:
        review_comment.delete()

  def get_branch_commit_sha(self):
    """
      Parameters
      ----------
          None
      Logic
      ----------
          Return the commit sha of current branch
      Return
      ----------
          commit.sha : string
    """
    commit = self.branch.commit
    return commit.sha

  def post_create_review_comment(self, user_name, pull_number, body, file_path, position):
    """
      Parameters
      ----------
          user_name: string
          pull_number: string
          body: string
          file_path: string
          position: int
      Logic
      ----------
          It will first remove all the previous review comments generated by github action bot.
          Then it will create new review comments.
      Return
      ----------
          None
    """
    query_url = f"https://api.github.com/repos/{user_name}/pulls/{pull_number}/comments"
    commit_id = self.get_branch_commit_sha()
    data = {
        "body": body,
        'position': position,
        'path': file_path,
        'commit_id': commit_id
    }
    _r = requests.post(query_url, headers=self.header, data=json.dumps(data))
    # pprint(_r.json())
  
  def create_review_comments(self, report_dct_):
    """
      Parameters
      ----------
          report_dct_: string
      Logic
      ----------
          It will create new review comments.
      Return
      ----------
          None
    """
    for report_section in self.report_dct_in_pr_rev_cmnt:
      for lst in report_dct_[report_section]:
        print(lst)
        path = lst[0]
        desc_ = lst[1]
        desc_ = f'{self.label} \n {desc_} \n {self.help_link}'
        splt = path.split(':', 2)
        file_path = splt[0]
        line_no_ = int(splt[1])
        self.post_create_review_comment(self.user_name, self.pr_number, desc_, file_path, line_no_)

  def get_params_from_pylint_stdout(self, splt):
    """
      Parameters
      ----------
          splt: list
      Logic
      ----------
          Format the pylint stdout splt
      Return
      ----------
          None
    """
    if not splt[0]:
      splt.pop(0)
    path_ = splt[0]
    type_ = splt[1] if len(splt) >= 2 else 'DEFAULT_TYPE'
    desc_ = splt[2] if len(splt) >= 3 else 'DEFAULT_DESC'
    return path_, type_, desc_

  def format_pylint_stdout(self, report_dct_, pylint_stdout):
    """
      Parameters
      ----------
          report_dct_: string
          pylint_stdout: string
      Logic
      ----------
          Format the pylint stdout stream
      Return
      ----------
          None
    """
    for line in pylint_stdout:  # Iterate through the cStringIO file-like object.
      line.strip()
      splt = line.split(' ', 3)
      path_, type_, desc_ = self.get_params_from_pylint_stdout(splt)
      if type_ in report_dct_.keys():
        print([path_, desc_])
        report_dct_[type_].append([path_, desc_])
    # self.create_review_comments(report_dct_)

  def check_docstrings(self, file_paths):
    """
      Parameters
      ----------
          file_paths: String
          
      Logic
      ----------
          execute lint on all the files and then call create review comment on the current pull request.
      Return
      ----------
          None
    """
    for file_path in file_paths:
      ARGS = ["-r","n", "--rcfile=.github/actions/check-docstrings/.pylintrc"]
      pylint_output = WritableObject()
      Run([file_path]+ARGS, reporter=TextReporter(pylint_output), exit=False)
      for l in pylint_output.read():
        print(l)
      # (pylint_stdout, pylint_stderr) = lint.py_run(file_path , return_std=True)
      # pylint_stdout.seek(0)
      report_dct_ = self.report_dct
      self.format_pylint_stdout(report_dct_, pylint_stdout)

  def compute(self):
    """
      Parameters
      ----------
          None
      Logic
      ----------
          First fetch all the python files and check individual docstrings 
          then create there review comments on pull request.
      Return
      ----------
          None
    """
    pull_number = int(self.pr_number)
    self.delete_all_previous_bot_generated_review_comments(pull_number)
    pull_request = self.repo.get_pull(pull_number)
    pr_files = pull_request.get_files()
    file_paths = []
    for _f in pr_files:
      file_path = _f.filename
      file_extension = os.path.splitext(file_path)[1]
      if file_extension == '.py':
          file_paths.append(file_path)
    self.check_docstrings(file_paths)

def main():
  """
  Create object of class
  and call compute function
  """
  print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
  obj = CheckDocstrings()
  obj.compute()
 
if __name__ == "__main__":
    main()
