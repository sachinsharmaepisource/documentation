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
# import os
# import sys
# from github import Github
    
# #---------------------------------------------------------------------------------------------------------

# class DocstringCheck:

#   def __init__(self):
# #     Initialization of following variables
#     self.REPO_NAME = self.get_inputs('REPO_NAME')
#     self.PR_TITLE = self.get_inputs('PR_TITLE')
#     self.PR_NUMBER = self.get_inputs('PR_NUMBER')
#     self.ACCESS_TOKEN = self.get_inputs('ACCESS_TOKEN')
#     self.USER_NAME = self.get_inputs('USER_NAME')
#     self.ACTION_TYPE = self.get_inputs('ACTION_TYPE')
# #     Github action, Repo, Pull request objects are defined
#     self.GH = Github(self.ACCESS_TOKEN)
#     self.repo = self.GH.get_repo(self.USER_NAME + '/' + self.REPO_NAME)
#     self.branch = "main"
#     print("hello")
    
#   def get_inputs(self, input_name):
#     '''
#       Parameters
#       ----------
#           input_name: String
          
#       Logic
#       ----------
#           Extract the inputs from the YML file of GITHUB ACTION
#       Return
#       ----------
#           Input: String
#     '''
#     return os.getenv('INPUT_{}'.format(input_name).upper())
  
#   def compute(self):
#     contents = self.repo.get_contents("", self.branch)
#     while contents:
#         file_content = contents.pop(0)
#         if file_content.type == "dir":
#             contents.extend(self.repo.get_contents(file_content.path, self.branch))
#         else:
#             print(file_content.path)
#             print(file_content.decoded_content)
  
# def main():
#   print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
#   obj = DocstringCheck()
#   obj.compute()
 
# if __name__ == "__main__":
#     main()

    
