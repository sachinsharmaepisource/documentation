import os
import sys
from github import Github

class IncorrectTitleFormatError(Exception):
  """
    Exception raised for errors.

    Attributes:
        message -- explanation of the error
  """
  def __init__(self, message="The Pull request title format is incorrect!\nPlease correct the format."):
        self.message = message
        super().__init__(self.message)

        
#---------------------------------------------------------------------------------------------------------

class PullRequestTitleCheck:
#   list of categories allowed in PR title
  category_list = ['FEATURES', 'DOCUMENTATION', 'REFACTOR', 'BUG FIX', 'OTHERS']

  def __init__(self):
#     Initialization of following variables
    self.REPO_NAME = self.get_inputs('REPO_NAME')
    self.PR_TITLE = self.get_inputs('PR_TITLE')
    self.PR_NUMBER = self.get_inputs('PR_NUMBER')
    self.ACCESS_TOKEN = self.get_inputs('ACCESS_TOKEN')
    self.USER_NAME = self.get_inputs('USER_NAME')
    self.ACTION_TYPE = self.get_inputs('ACTION_TYPE')
#     Github action, Repo, Pull request objects are defined
    self.GH = Github(self.ACCESS_TOKEN)
    self.repo = self.GH.get_repo(self.USER_NAME)
    self.pr = self.repo.get_pull(int(self.PR_NUMBER))
  

  def check_pull_request_title(self):
    '''
      Prameters
      ---------
            pr_title:: String
      Return
      ---------
            Boolean:: Bool
                Is the first word of pr_title, among the category list format.
    '''
    splt = self.PR_TITLE.split(':')
    if len(splt) > 1:
      category = splt[0].upper().strip()
      return category in self.category_list
    return False
  
  
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

  def compute(self):
    '''          
      Logic
      ----------
          If the PR title is of correct format than the check will be passed
          ELSE: the PR title is of incorrect format
            IF the PR is closed than the GH action will override and pass the gh action, even if the pr title format is incorrect.
            ELSE Create a new issue comment with proper comment of correct PR title format and raise custom exception error.
    '''
    if self.check_pull_request_title():
      print('the pr title is of correct format')
      pass
    else:
      if self.ACTION_TYPE == 'closed':
        print('The pull request is closed, so the pr title check github action will override and pass the github action, even the pr title format is incorrect')
        pass
      else:
        print('the pr title is of inccorrect format\n now we will create an issue comment in pull request')
        self.pr_issue_comment = 'Please update the PR title with following format:\n A pr title must contains a colon(:) seperated category name and title body.\n\n The Category must be among following: \n1. Features\n2. Documentation\n3. Refactor\n4. Bug Fix\n5. Others\n\nFor example:\n > Fixed key error in tracker then check should be failed - ❌\n > Bug fix: Fixed key error in tracker then check should be passed - ✅\n'
        self.pr.create_issue_comment(self.pr_issue_comment)
#       Now we will raise a custom exception
        raise IncorrectTitleFormatError()
      


  
def main():
  print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
  release = PullRequestTitleCheck()
  release.compute()
 
if __name__ == "__main__":
    main()
