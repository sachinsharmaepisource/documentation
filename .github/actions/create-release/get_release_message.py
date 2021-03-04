"""
  This mudule consists of GetReleaseMessage Class,
    constructor attributes :: Repo
  
  This module consists of following functions:
  - get_last_version
  - get_start_date_of_latest_release
  - is_merge_commit_msg_format_correct
  - get_release_name
  - get_merge_commits_message
  - get_pull_requests_message
  - get_release_message
"""
import sys
import os
sys.path.append(os.path.abspath("./.github/actions/create-release"))
from constants import *
from get_pull_requests import GetPullRequests

class GetReleaseMessage:
  '''
  GetReleaseMessage Class,
    constructor attributes :: Repo
  
  This module consists of following functions:
  - get_last_version
  - get_start_date_of_latest_release
  - is_merge_commit_msg_format_correct
  - get_release_name
  - get_merge_commits_message
  - get_pull_requests_message
  - get_release_message
  '''
  def __init__(self, repo):
    self.repo = repo
    self.branch = constants['branch']
    self.repo_name = constants['REPO_NAME']
    self.emoji_list = constants['emoji_list']
    self.categories_dct = constants['categories_dct']
    
    get_pull_requests_obj = GetPullRequests(self.repo)
    self.get_pull_requests = get_pull_requests_obj.get_pull_requests
  
  def get_last_version(self):
    '''
      Logic
      ----------
          Defualt last_version = v0.0.0
          1. Chack is there is any old release exists, by checking the totalCount of all the releases
          2. Set latest version as tag name of the latest release

      Return
      ----------
          last_version: String
    '''
    last_version = 'v0.0.0' 
    # default first version
    non_draft_releases_count = 0
    releases = self.repo.get_releases()
    for release in releases:
      if not release.draft:
        non_draft_releases_count+=1
    if non_draft_releases_count != 0:
      latestRelease = self.repo.get_latest_release()
      last_version = latestRelease.tag_name
    return last_version
  
  def get_start_date_of_latest_release(self):
    '''
      Logic
      ----------
      The start_date will store the date from
        If the latest release exists:
          start date will be the creation date of repositiory
        Else:
          start date will be the creation date of latest release

      Return
      ----------
      start_date: Datetime
    '''
    if self.repo.get_releases().totalCount == 0:
      return self.repo.created_at
    else:
      return self.repo.get_latest_release().created_at
    
  def is_merge_commit_msg_format_correct(self, msg):
    '''
      Parameters
      ----------
          msg: String
              Commit message in the format as :(seperated bt \n\n)
                <--  Merge pull request #105 from episource_repo/develop_branch
                  
                     Merge commit optional description -->

      Return
      ----------
          is format correct: Bool
    '''
#     Sample structure of correct merge commit message
#     Merge pull request #105 from episource_repo/develop_branch
    msg_split = msg.split('\n\n', 1)[0].split(' ')
    return msg_split[0] == "Merge" and msg_split[1] == "pull" and msg_split[2] == "request" and msg_split[3][0] == "#" and msg_split[4] == "from"
  
  def get_release_name(self, tag_name):
    '''
      Parameters
      ----------
          tag_name: String
              Name of the tag (v1.1.1)

      Return
      ----------
          release_name: String
              As per the release name format
    '''
    return tag_name + ' of ' + self.repo_name
  
  def get_merge_commits_message(self, start_date):
    '''
      Parameters
      ----------
          start_date: Date
          
      Logic
      --------
        1. All the merged commits are stored in merge_commits_str with corresponding format.
        2. The merge_commits_str will store its merge commits messages with proper sections.

        Return
        --------
        merge_commits_str: String
              Merge commits message 
    '''
    merge_commits_str = ''
#   Prepare the merge commit section
    commit_sha_list = []
#   Get all the commits from branch since start_date of last release
    commits = self.repo.get_commits(self.branch , since = start_date)
    for commit in commits:
      commit_sha = commit.commit.sha
#       Only merge commits and conflict resolve commits have 2 parents :: using this point to filter merge commit and conflict resolve than rest of the commits
#       In order to filter merge commits from conflict resolve commits :: is_merge_commit_msg_format_correct function is used to differentiate the structure of merge commit than a conflict resolve commit
#       commit_sha_list confirms unique commits and avoid duplicacy of commits by storing the SHA
      if len(commit.commit.parents) == 2 and commit_sha not in commit_sha_list and self.is_merge_commit_msg_format_correct(commit.commit.message):
#       Formatting the commit message and extract the main title (By default it is PR title) and PR number using basic splitting
        commit_sha_list.append(commit_sha)
        cmt_msg_splt = commit.commit.message.split('\n\n', 1)
        cmt_msg = cmt_msg_splt[1]
        cmt_number = cmt_msg_splt[0].split(' ')[3]
        merge_commits_str += '\n' + commit_sha + '\t' + cmt_msg.replace('\n', '\n &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&nbsp;') + '   (' + cmt_number + ')'
    return merge_commits_str  
  
  def get_sorted_formatted_pull_requests_messages(self, cat, new_release_message_dct, new_release_message_str):
    '''
      Parameters
      ----------
          cat: string
          new_release_message_dct: Dictionary
          new_release_message_str: string
          
      Logic
      --------
          SORTING to arrange the Pull requests according to there keys(PR number)

      Return
      --------
          new_release_message_str: String
    '''
    emoji = self.emoji_list
    new_release_message_str += '\n\n' + '### ' + cat.capitalize() + emoji[cat]
    # SORTING to arrange the Pull requests according to there keys(PR number)
    for key in sorted(new_release_message_dct[cat].keys(), reverse = True):
      new_release_message_str += '\n *  ' + new_release_message_dct[cat][key] + '\t (#' + str(key) + ')'
    return new_release_message_str
      
  def get_formatted_pull_requests_message(self, new_release_message_dct):
    '''
      Parameters
      ----------
          new_release_message_dct: Dictionary
          
      Logic
      --------
        Create pull request message from new_release_message_dct

        Return
        --------
        new_release_message_str: String
    '''
    new_release_message_str = ''
    for cat in new_release_message_dct:
      if len(new_release_message_dct[cat]) != 0:
        new_release_message_str = self.get_sorted_formatted_pull_requests_messages(cat, new_release_message_dct, new_release_message_str)
    return new_release_message_str
  
  def check_pr_title(self, pr_title_splt, pr_title_category, new_release_message_dct):
    '''
      Parameters
      ----------
             pr_title_splt: list
             pr_title_category: string
             new_release_message_dct: Dictionary
      Return
      --------
            Bool: Bool
    '''
    return len(pr_title_splt) >= 2  and pr_title_category in new_release_message_dct.keys()
  
  def get_pull_requests_message(self, start_date, last_version):
    '''
      Parameters
      ----------
            start_date: Date 
            last_version: String
      Logic
      --------
        1. All the pull requests are stored in new_release_message_str with corresponding format.
        2. The new_release_message_str will store its merge commits messages with proper sections.

      Return
      --------
        new_release_message_str: String
              PR message 
    '''
    emoji = self.emoji_list
    new_release_message_dct = self.categories_dct
    new_release_message_str = ''
    merge_commits_str = ''
    pulls = self.get_pull_requests(start_date)
    for pull in pulls:
      pr_title = pull.title
      pr_title_splt = pr_title.split(':', 1)
      pr_title_category = pr_title_splt[0].lower().strip()
      if self.check_pr_title(pr_title_splt, pr_title_category, new_release_message_dct):
        pr_title_body = pr_title_splt[1].strip()
        new_release_message_dct[pr_title_category][int(pull.number)] = pr_title_body
      else:
        new_release_message_dct['others'][int(pull.number)] = pull.title
    new_release_message_str = self.get_formatted_pull_requests_message(new_release_message_dct)
    return new_release_message_str
      
  def get_release_message(self, tag_name):
    '''
      Parameters
      ----------
          tag_name: String(v0.0.1)
          
      Logic
      --------
        1. All the merged PRs are stored in new_release_message_dct.
        2. Along with corresponding categories with proper format.
        2. The format_release_message will store its release message with proper sections.

      Return
      --------
        format_release_message: String
              Release message format
    '''
    start_date = self.get_start_date_of_latest_release()
    last_version = self.get_last_version()
    new_release_message_str = self.get_pull_requests_message(start_date, last_version)
    merge_commits_str = self.get_merge_commits_message(start_date)
#     Append and format the final release message including following sections as
#     1. Pull requests titles
#     2. Merge commits
    release_msg_title = f'# {str(self.repo_name)} {str(tag_name)}'
    release_msg_subtitle = f' Release notes\n ## Changes since   ``` {str(last_version)}'
    release_msg_title_cmb = f'{release_msg_title} {release_msg_subtitle}'
    release_msg_pr_section = f'``` \n\n {str(new_release_message_str)} \n\n '
    release_msg_merge_commit = f'## Commits since  ```  {str(last_version)}'
    release_msg_merge_commit +=  f'  ```  \n  {str(merge_commits_str)}'
    frmt_release_message = f'{release_msg_title_cmb} {release_msg_pr_section}'
    frmt_release_message += f' {release_msg_merge_commit}'
    print('release msg', frmt_release_message)
    return  frmt_release_message
