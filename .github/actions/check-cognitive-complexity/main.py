"""
	Logic:
	It wil compute cognitice complexities of every functions/module.
	Then it will create review messages on the pull request.
"""
import os
import os.path
import ast
import json
from github import Github
from cognitive_complexity.api import get_cognitive_complexity
import requests
#---------------------------------------------------------------------------------------------------------
class CognitiveReport:
  """
  It generates cognitive complexity report using compute function.
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
    self._gh = Github(self.access_token)
    self.repo = self._gh.get_repo(self.user_name)
    if self.pr_number:
      self.current_branch = self.repo.get_pull(int(self.pr_number)).head.ref
    self.branch = self.repo.get_branch(self.current_branch)
    self.header = {'Authorization': f'token {self.access_token}'}
    self.max_cognitive_complexity = 5
    self.label = '[COGNITIVE COMPLEXITY]'
    
  def get_inputs(self, input_name):
    """
      Parameters
      ----------
          input_name : String
            Input name
      Logic
      ----------
          Extract the inputs from the YML file of GITHUB ACTION
      Returns
      -------
          Input : String
            Input string
    """
    return os.getenv('INPUT_{}'.format(input_name).upper())
  
  def delete_all_previous_bot_generated_review_comments(self, pull_number):
    """
      Parameters
      ----------
          pull_number : Int
            Pull number of the current pull request
      Logic
      ----------
          Delete all the review comments generated by github action bot
    """
    _pr = self.repo.get_pull(int(pull_number))
    review_comments = _pr.get_review_comments()
    for review_comment in review_comments:
      comment_desc_label = review_comment.body.split('\n', 1)[0].strip()
      if review_comment.user.type == 'Bot' and comment_desc_label == self.label:
        review_comment.delete()

  def get_branch_commit_sha(self):
    """
      Logic
      ----------
          Return the commit sha of current branch
      Returns
      -------
          SHA : string
            Commit SHA
    """
    commit = self.branch.commit
    return commit.sha

  def create_review_comments(self, user_name, pull_number, body, file_path, position):
    """
      Parameters
      ----------
          user_name : string
            User name
          pull_number : int
            Pull Number
          body : string
            Body of message
          file_path : string
            Path to file
          position : int
            Line number
      Logic
      ----------
          Then it will create new review comments.
    """
    query_url = f"https://api.github.com/repos/{user_name}/pulls/{pull_number}/comments"
    data = {
        "body": body,
        'position': position,
        'path': file_path,
        'commit_id': self.get_branch_commit_sha()
    }
    requests.post(query_url, headers=self.header, data=json.dumps(data))
#     print(_r.json())
    
  def get_tree(self, file_path):
    """
      Parameters
      ----------
          file_path : string
            Path to file
      Logic
      ----------
          Return tree structure from file_path
      Returns
      -------
          Tree : Object
            Tree of file structure
    """
    with open(file_path, 'r') as file_handler:
      raw_content = file_handler.read()
    tree = ast.parse(raw_content)
    return tree
  
  def get_single_cognitive_report(self, funcdefs, file_path):
    """
      Parameters
      ----------
          funcdefs : string
            Function statement
          file_path : string
            File Path
      Logic
      ----------
          Compute congnitive report and return it.
      Returns
      -------
          cognitive_report : list
            Cognitive Report
    """
    cognitive_report = []
    for funcdef in funcdefs:
        complexity = get_cognitive_complexity(funcdef)
        if complexity > self.max_cognitive_complexity:
          cognitive_report.append(f'--{file_path} | {funcdef.lineno}:{funcdef.col_offset} | Cognitive Complexity is greater then threshold {complexity} > {self.max_cognitive_complexity}') # pylint: disable=line-too-long
          desc_ = f'Function has a Cognitive Complexity of {complexity} (exceeds {self.max_cognitive_complexity} allowed). Consider refactoring.'
          desc_ = f'{self.label} \n {desc_}'
          self.create_review_comments(self.user_name, self.pr_number, desc_, file_path, funcdef.lineno)
        else:
          cognitive_report.append(f'++{file_path} | {funcdef.lineno}:{funcdef.col_offset} | Cognitive Complexity is less then threshold {complexity} <= {self.max_cognitive_complexity}') # pylint: disable=line-too-long
    return cognitive_report

  def get_cognitive_report(self, file_paths):
    """
      Parameters
      ----------
          file_paths : string
            File path
      Logic
      ----------
          Return combined cognitive report.
      Return
      ----------
          cognitive_report : list
            Cognitive Report
    """
    cognitive_report = []	
    for file_path in file_paths:
      tree = self.get_tree(file_path)
      funcdefs = (
          n for n in ast.walk(tree)
          if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
      )
      cognitive_report = cognitive_report + self.get_single_cognitive_report(funcdefs, file_path)
    return cognitive_report
	
  def compute(self):
    """
      Logic
      ----------
          It will first remove all the previous review comments generated by github action bot.
          Fetch all the python files and compute individual congnitive complexities then create there review comments on pull request.
    """
    pull_number = inr(self.pr_number)
    self.delete_all_previous_bot_generated_review_comments(pull_number)
    pull_request = self.repo.get_pull(pull_number)
    pr_files = pull_request.get_files()
    file_paths = []
    for _f in pr_files:
      file_path = _f.filename
      file_extension = os.path.splitext(file_path)[1]
      if file_extension == '.py':
          file_paths.append(file_path)
    cognitive_report = self.get_cognitive_report(file_paths)
    print(*cognitive_report, sep = "\n")
            
def main():
  """
  Class object is created and compute method is called
  """
  print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
  obj = CognitiveReport()
  obj.compute()
 
if __name__ == "__main__":
    main()
