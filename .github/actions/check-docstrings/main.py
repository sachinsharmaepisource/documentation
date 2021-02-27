import os
import os.path
import sys
from github import Github

from pylint.lint import Run
import json
import requests
from pprint import pprint
#  https://github.com/Melevir/flake8-cognitive-complexity
#---------------------------------------------------------------------------------------------------------
'''
	Logic:
	It wil check docstring format as per standards.
	Then it will create review messages on the pull request.
'''
class CheckDocstrings:

  def __init__(self):
#     Initialization of following variables
    self.REPO_NAME = self.get_inputs('REPO_NAME')
    self.PR_TITLE = self.get_inputs('PR_TITLE')
    self.PR_NUMBER = self.get_inputs('PR_NUMBER')
    self.ACCESS_TOKEN = self.get_inputs('ACCESS_TOKEN')
    self.USER_NAME = self.get_inputs('USER_NAME')
    self.ACTION_TYPE = self.get_inputs('ACTION_TYPE')
    self.CURRENT_BRANCH = self.get_inputs('CURRENT_BRANCH')
    self.GH = Github(self.ACCESS_TOKEN)
    self.repo = self.GH.get_repo(self.USER_NAME)
    if self.PR_NUMBER:
      self.CURRENT_BRANCH = self.repo.get_pull(int(self.PR_NUMBER)).head.ref
    self.branch = self.repo.get_branch(self.CURRENT_BRANCH)
    self.header = {'Authorization': f'token {self.ACCESS_TOKEN}'}
    self.threshold = 5
    self.RCFILE_PATH = './.github/actions/check-docstrings/.pylintrc'
    
  def get_inputs(self, input_name):
    '''
      Parameters
      ----------
          input_name: String
          
      Logic
      ----------
          Extract the inputs from the YML file of GITHUB ACTION
      Return
      ----------
          Input: String
    '''
    return os.getenv('INPUT_{}'.format(input_name).upper())
  
  def delete_all_previous_bot_generated_review_comments(self, pull_number):
    '''
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
    '''
    pr = self.repo.get_pull(int(pull_number))
    review_comments = pr.get_review_comments()
    for review_comment in review_comments:
      if review_comment.user.type == 'Bot':
        review_comment.delete()

  def get_branch_commit_sha(self):
    '''
      Parameters
      ----------
          None
      Logic
      ----------
          Return the commit sha of current branch
      Return
      ----------
          commit.sha : string
    '''
    commit = self.branch.commit
    return commit.sha

  def create_review_comments(self, user_name, pull_number, body, file_path, position):
    '''
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
    '''
    self.delete_all_previous_bot_generated_review_comments(pull_number)
    query_url = f"https://api.github.com/repos/{user_name}/pulls/{pull_number}/comments"
    data = {
        "body": body,
        'position': position,
        'path': file_path,
        'commit_id': self.get_branch_commit_sha()
    }
    r = requests.post(query_url, headers=self.header, data=json.dumps(data))
#     pprint(r.json())
    
  def get_tree(self, file_path):
    '''
      Parameters
      ----------
          file_path: string
      Logic
      ----------
          Return tree structure from file_path
      Return
      ----------
          Tree: Object
    '''
    with open(file_path, 'r') as file_handler:
      raw_content = file_handler.read()
    tree = ast.parse(raw_content)
    return tree
  
  def get_single_cognitive_report(self, funcdefs, file_path):
    '''
      Parameters
      ----------
          funcdefs: string
          file_path: string
      Logic
      ----------
          Compute congnitive report and return it.
      Return
      ----------
          cognitive_report : list
    '''
    cognitive_report = []
    for funcdef in funcdefs:
        complexity = get_cognitive_complexity(funcdef)
        if complexity > self.max_cognitive_complexity:
          cognitive_report.append(f'--{file_path} | {funcdef.lineno}:{funcdef.col_offset} | Cognitive Complexity is greater then threshold {complexity} > {self.max_cognitive_complexity}')
          self.create_review_comments(self.USER_NAME, self.PR_NUMBER, cognitive_report[-1], file_path, funcdef.lineno)
        else:
          cognitive_report.append(f'++{file_path} | {funcdef.lineno}:{funcdef.col_offset} | Cognitive Complexity is less then threshold {complexity} <= {self.max_cognitive_complexity}')
    return cognitive_report

  def get_cognitive_report(self, file_paths):
    '''
      Parameters
      ----------
          file_paths: string
      Logic
      ----------
          Return combined cognitive report.
      Return
      ----------
          cognitive_report:list
    '''
    cognitive_report = []	
    for file_path in file_paths:
      tree = self.get_tree(file_path)
      funcdefs = (
          n for n in ast.walk(tree)
          if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
      )
      cognitive_report = cognitive_report + self.get_single_cognitive_report(funcdefs, file_path)
    return cognitive_report
	
  def get_docstring_report(self, file_paths):
    
    for file_path in file_paths:
      path = file_path
      pylint_opts = [ path, f'--rcfile={self.RCFILE_PATH}']
      results = Run(pylint_opts, do_exit=False)
      final_score = results.linter.stats['global_note']
      pprint('----------results.linter.stats', results.linter.stats)
      print('final_score', final_score)


  def compute(self):
    '''
      Parameters
      ----------
          None
      Logic
      ----------
          First fetch all the python files and compute individual congnitive complexities then create there review comments on pull request.
      Return
      ----------
          None
    '''
    contents = self.repo.get_contents("", self.branch.name)
    file_paths = []
    while contents:
        file_content = contents.pop(0)
        file_extension = os.path.splitext(file_content.path)[1]
        if file_content.type == "dir":
            contents.extend(self.repo.get_contents(file_content.path, self.branch.name))
        elif file_extension == '.py':
          file_paths.append(file_content.path)
    self.get_docstring_report(file_paths)
    # print(*docstring_report, sep = "\n")
    
            
def main():
  print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
  obj = CheckDocstrings()
  obj.compute()
 
if __name__ == "__main__":
    main()
