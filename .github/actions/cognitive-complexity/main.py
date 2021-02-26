import os
import os.path
import sys
from github import Github
import ast
from cognitive_complexity.api import get_cognitive_complexity
import json
import requests
from pprint import pprint
#  https://github.com/Melevir/flake8-cognitive-complexity
#---------------------------------------------------------------------------------------------------------

class DocstringCheck:

  def __init__(self):
#     Initialization of following variables
    self.REPO_NAME = self.get_inputs('REPO_NAME')
    self.PR_TITLE = self.get_inputs('PR_TITLE')
    self.PR_NUMBER = self.get_inputs('PR_NUMBER')
    self.ACCESS_TOKEN = self.get_inputs('ACCESS_TOKEN')
    self.USER_NAME = self.get_inputs('USER_NAME')
    self.ACTION_TYPE = self.get_inputs('ACTION_TYPE')
    self.CURRENT_BRANCH = self.get_inputs('CURRENT_BRANCH')
#     Github action, Repo, Pull request objects are defined
    self.GH = Github(self.ACCESS_TOKEN)
    self.repo = self.GH.get_repo(self.USER_NAME)
    self.branch = self.repo.get_branch(self.CURRENT_BRANCH)
    self.header = {'Authorization': f'token {self.ACCESS_TOKEN}'}
    self.max_cognitive_complexity = 5
    
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
  
  def get_branch_commit_sha(self):
    commit = self.branch.commit
    return commit.sha

  def create_review_comments(self, user_name, pull_number, body, file_path, position):
    query_url = f"https://api.github.com/repos/{user_name}/pulls/{pull_number}/comments"
    data = {
        "body": 'body',
        'position': position,
        'path': file_path,
        'commit_id': self.get_branch_commit_sha()
    }
    pprint(data)
    r = requests.post(query_url, headers=self.header, data=json.dumps(data))
    pprint(r.json())
    
  def get_tree(self, file_path):
    with open(file_path, 'r') as file_handler:
      raw_content = file_handler.read()
    tree = ast.parse(raw_content)
    return tree
  
  def get_single_cognitive_report(self, funcdefs, file_path):
    cognitive_report = []
    for funcdef in funcdefs:
        complexity = get_cognitive_complexity(funcdef)
        if complexity > self.max_cognitive_complexity:
          cognitive_report.append(f'--{file_path} | {funcdef.lineno}:{funcdef.col_offset} | Cognitive Complexity is greater then threshold {complexity} > {self.max_cognitive_complexity}')
        else:
          cognitive_report.append(f'++{file_path} | {funcdef.lineno}:{funcdef.col_offset} | Cognitive Complexity is less then threshold {complexity} <= {self.max_cognitive_complexity}')
        self.create_review_comments(self.USER_NAME, self.PR_NUMBER, cognitive_report[-1], file_path, funcdef.lineno)
    return cognitive_report

  def get_cognitive_score(self, file_paths):
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
    contents = self.repo.get_contents("", self.branch.name)
    file_paths = []
    while contents:
        file_content = contents.pop(0)
        file_extension = os.path.splitext(file_content.path)[1]
        if file_content.type == "dir":
            contents.extend(self.repo.get_contents(file_content.path, self.branch.name))
        elif file_extension == '.py':
          print(file_content.path)
          file_paths.append(file_content.path)
    cognitive_report = self.get_cognitive_score(file_paths)
    print(*cognitive_report, sep = "\n")
            
#             print(file_content.decoded_content)
   
def main():
  print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
  obj = DocstringCheck()
  obj.compute()
 
if __name__ == "__main__":
    main()
