"""
  This mudule consists of GetPullRequests Class,
    constructor attributes :: Repo
  
  This module consists of following functions:
  - apply_bfs_with_pull_requests
  - filter_pulls
  - get_pull_requests
"""
import sys
import os
sys.path.append(os.path.abspath("./.github/actions/create-release"))
from constants import *

class GetPullRequests:
  """
  GetPullRequests Class,
    constructor attributes :: Repo
  
  This module consists of following functions:
  - apply_bfs_with_pull_requests
  - filter_pulls
  - get_pull_requests
  """
  def __init__(self, repo):
    self.repo = repo
    self.branch = constants['branch']
  
  def bfs_util(self, pull, base_branches_dct, queue, pulls_visited_list):
    """
      Parameters
      ----------
          pull:  Pull Request
          base_branches_dct: Dict
          queue: List
          pulls_visited_list: list
      Logic
      ----------
          Inner structure of BFS, iterate all the nodes.
      Return
      -----------
            queue: List
            pulls_visited_list: List
    """
    for pull_nested in base_branches_dct[pull.head.ref]:
      if pull_nested.number not in pulls_visited_list:
        queue.append(pull_nested)
        pulls_visited_list.append(pull_nested.number)
    return queue, pulls_visited_list
          
  def apply_bfs_with_pull_requests(self, base_branches_dct):
    """
      Parameters
      ----------
          base_branches_dct:  Dictionary
                  Stores base branches
      
      Logic
      ----------
              Filter the pull requests recursively, using BFS.
              Store the pull request objects and base ref in filtered_pulls
       Return
       -----------
            filtered_pulls :: list     - stores the list of pull requests
    """
    filtered_pulls = []
#   BFS Algo for recursive branch fetch
    queue = []
#  pulls_visited_list :: To prevent infinite loop in cycle, used in BFS
    pulls_visited_list = []
    for pull in base_branches_dct[self.branch]:
      queue.append(pull)
    while queue:
      pull = queue.pop(0)
      filtered_pulls.append(pull)
      if pull.head.ref in base_branches_dct.keys():
        queue, pulls_visited_list = self.bfs_util(pull, base_branches_dct, queue, pulls_visited_list)
    return filtered_pulls
  
  def get_init_branches_dct(self, pull, base_branches_dct, head_branches_dct):
    """
      Parameters
      ----------
          pull:  Pull Request
          base_branches_dct: Dict
          head_branches_dct: Dict
      Logic
      ----------
          Initialize the dictionary.
      Return
      -----------
            base_branches_dct: Dictionary
            head_branches_dct: Dictionary
    """
    if pull.base.ref in base_branches_dct.keys():
      base_branches_dct[pull.base.ref].append(pull)
    else:
      base_branches_dct[pull.base.ref] = []
      base_branches_dct[pull.base.ref].append(pull)
    if pull.head.ref in head_branches_dct.keys():
      head_branches_dct[pull.head.ref].append(pull)
    else:
      head_branches_dct[pull.head.ref] = []
      head_branches_dct[pull.head.ref].append(pull)
    return base_branches_dct, head_branches_dct
  
  def filter_pulls(self, pulls):
    """
      Parameters
      ----------
          pulls:  Object
                  The list of pull requests
      Logic
      ----------
            For filtering the pull requests:
              First all the Branches are fetched and initialise the base_branches_dct and head_branches_dct with empty lists with branch name as key
              Iterate to all the pulls:
                if the pull request base is among the base_branches_dct keys(), then append this PR in the base_branches_dct
                if the pull request base is among the head_branches_dct keys(), then append this PR in the head_branches_dct
              
              Filter the pull requests recursively, using BFS.
              Store the pull request objects and base ref in filtered_pulls
       Return
       -----------
            filtered_pulls :: list     - stores the list of pull requests
    """
    branches = self.repo.get_branches()
    base_branches_dct = {}
    head_branches_dct = {}
    filtered_branches_st = set()
    for branch in branches:
      base_branches_dct[branch.name] = []
      head_branches_dct[branch.name] = []
    for pull in pulls:
      
#       If the base/head branch name is not present in the branch list fetched with Pygithub function, that implies the corresponding base/head branch have been removed
#       In oreder to consider those PRs, whose head/base branch have been deleted, I inserted them in them in the else condition of both head and base dictionary
      base_branches_dct, head_branches_dct = self.get_init_branches_dct(pull, base_branches_dct, head_branches_dct)
        
    filtered_pulls = self.apply_bfs_with_pull_requests(base_branches_dct)
    return filtered_pulls
  
  def get_pull_requests(self, start_date):
    """
      Parameters
      ----------
          start_date:  Datetime
                  The start date from where the pull requests will be filtered
      Logic
      ----------
          First all the pull requests are fetched which are closed and sorted with there updated(datetime) in descending order
            Iterate on all the PRs
              If a PR have does not valid merged_at(datetime when PR was merged) parameter then,
                continue
              If merge_dt >= start_dt then,
                store it in list
       Return
       -----------
            filtered_pulls :: list     - stores the list of pull requests
    """
    pulls: List[PullRequest.PullRequest] = []
    for pull in self.repo.get_pulls(state='closed', sort='updated', direction='desc'):
      if not pull.merged_at:
        continue
      merged_dt = pull.merged_at
      if merged_dt >= start_date:
        pulls.append(pull)
        
    filtered_pulls = self.filter_pulls(pulls)
    return filtered_pulls
