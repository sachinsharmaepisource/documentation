import os
import sys
import datetime
from github import Github
from packaging import version
from configparser import ConfigParser

'''
  Requirements:
    There must be a valid version.ini file:
      - Have content in the format of v0.0.1
      - Content must start atleast from v0.0.1 (not v0.0.0)
  
  The streamline of release creation is as follows:
      - Multiple feature PRs -(merge)> develop branch -(merge)> master branch
  
  Logic:
    DRAFT RELEASE - TAG NAME - 'draft-tag-name' (Reserved)
    Only one draft release is allowed
    we capture the current version and last version:
      if current_version > last_version:
        remove_all_previous_draft_releases()
        create_new release()
      elif current_version == last_version:
        if is_new_merge_with_master_branch and no_version_change():
          remove_all_previous_draft_releases()
          create_new_draft_release
      else:
        the current_version is smaller to last version, INVALID no new release.
'''


class VersionCompareException(Exception):
  """
    Exception raised for errors.
    Attributes:
        message -- explanation of the error
  """
  def __init__(self, message="The current version is smaller than the last version, which is not allowed, kindly modify the version.ini(current version) file with at least last version."):
        self.message = message
        super().__init__(self.message)

#---------------------------------------------------------------------------------------------------------

class CreateNewRelease:
  def __init__(self):
    self.VERSION_FILE_PATH = 'version.ini'
    self.REPO_NAME = self.get_inputs('REPO_NAME')
    self.ACCESS_TOKEN = self.get_inputs('ACCESS_TOKEN')
    self.USER_NAME = self.get_inputs('USER_NAME')
    self.GH = Github(self.ACCESS_TOKEN)
    self.repo = self.GH.get_repo(self.USER_NAME)
    self.all_branches = self.repo.get_branches()
    self.branch = 'master'
    self.draft_tag_name = 'draft-tag-name'
    self.emoji_list = { 'features': '🚀', 'documentation': '📚', 'refactor': '♻️', 'bug fix': '🐛', 'others': '💡' }
    self.categories_dct = { 'features': {}, 'documentation': {}, 'refactor': {}, 'bug fix': {}, 'others': {} }
  
  def get_id(self, tag_name):
    '''
      Parameters
      ----------
          tag_name: String
          
      Logic
      ----------
          1. Fetch all the releases
          2. Iterate them and compare the tag_name
            2.1 Return ID when mathc found
            2.2 else return None
      Return
      ----------
          ID: String  | None
    '''
    all_releases = self.repo.get_releases()
    for release in all_releases:
      if release.tag_name == tag_name:
        return release.id
    return None
  
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

  def read_file_content(self, filePath):
    '''
      Parameters
      ----------
          filePath: String
              Path to file to read content from

      Return
      ----------
          content: String
    '''
    return self.repo.get_contents(filePath, self.branch).decoded_content.decode()

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

  def get_current_version(self):
    '''
      Logic
      ----------
        1. Read the file version.ini
        2. Extract the Version from version section

      Return
      ----------
      current_version: String
    '''
    content = self.read_file_content(self.VERSION_FILE_PATH)
    config_parser = ConfigParser()
    config_parser.read_string(content)
    current_version = config_parser.get('VERSION', 'Version')
    return current_version
    
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
  
  def get_start_date_of_draft_release(self):
    '''
      Logic
      ----------
          1. Fetch the id of draft tag_name
            1.1 Return if the draft_is is valid
          2. Return the start date of latest release()
          
      Return
      ----------
          start_date: Datetime
    '''
    draft_id = self.get_id(self.draft_tag_name)
    if draft_id is not None:
      return self.repo.get_release(draft_id).created_at
    return self.get_start_date_of_latest_release()
  
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
    return tag_name + ' of ' + self.REPO_NAME

  def get_release_message(self, tag_name):
    '''
      Parameters
      ----------
          tag_name: String(v0.0.1)
          
      Logic
      --------
        1. All the merged PRs are stored in new_release_message_dct with corresponding categories with proper format
        2. The format_release_message will store its release message with proper sections.

        Return
        --------
        format_release_message: String
              Release message format 
    '''
    emoji = self.emoji_list
    new_release_message_dct = self.categories_dct
    new_release_message_str = ''
    merge_commits_str = ''
    last_version = self.get_last_version()
    start_date = self.get_start_date_of_latest_release()
    pulls = self.get_pull_requests(start_date)
   
    for pull in pulls:
      pr_title = pull.title
      pr_title_splt = pr_title.split(':', 1)
      pr_title_category = pr_title_splt[0].lower().strip()
      if len(pr_title_splt) >= 2  and pr_title_category in new_release_message_dct.keys():
        pr_title_body = pr_title_splt[1].strip()
        new_release_message_dct[pr_title_category][int(pull.number)] = pr_title_body
      else:
        new_release_message_dct['others'][int(pull.number)] = pull.title
    
    for cat in new_release_message_dct:
      if len(new_release_message_dct[cat]) != 0:
            new_release_message_str += '\n\n' + '### ' + cat.capitalize() + emoji[cat]
#         SORTING to arrange the Pull requests according to there keys(PR number)
            for key in sorted(new_release_message_dct[cat].keys(), reverse = True):
              new_release_message_str += '\n *  ' + new_release_message_dct[cat][key] + '\t (#' + str(key) + ')'
    
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
     
#     Append and format the final release message including following sections as
#     1. Pull requests titles
#     2. Merge commits
    format_release_message = '# ' + self.REPO_NAME + ' ' + tag_name + ' ' + 'Release notes\n' + '## Changes since ' + '``` ' + last_version + ' ```' + '\n\n' + new_release_message_str + '\n\n ## Commits since ' + '``` ' + last_version + ' ```' + '\n' + merge_commits_str
    print('release msg', format_release_message)
    return  format_release_message

  def create_release(self, tag_name, tag_message, release_name, release_message, is_draft, is_prerelease):  
    # https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html#github.Repository.Repository.create_git_tag_and_release
    '''
        Parameters
        ----------
            tag_name: String(v0.0.1)
            tag_message: String
            release_name: String
            release_message: String
            is_draft: Boolean
            is_prerelease: Boolean
        Logic
        --------
            1. A branch reference is fetched for commit SHA
            2. A tag is created with respective parameters
            3. A reference to tag is created using tag SHA
            4. A release is created with respective tag

        Return
        --------
        release: Object
              Reference to the new release created
    '''
    branch = self.repo.get_branch(self.branch)
    tag = self.repo.create_git_tag(tag_name, tag_message, branch.commit.sha, 'commit')
    ref = self.repo.create_git_ref('refs/tags/' + tag_name, tag.sha)
    release = self.repo.create_git_release(tag.tag, release_name, release_message, is_draft, is_prerelease)
    return release

  def get_pull_requests(self, start_date):
    '''
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
    '''
    pulls: List[PullRequest.PullRequest] = []
    try:
      for pull in self.repo.get_pulls(state='closed', sort='updated', direction='desc'):
        if not pull.merged_at:
          continue
        merged_dt = pull.merged_at
        if merged_dt >= start_date:
          pulls.append(pull)
    except Exception as e:
        print('Github pulls error (request)', e)
        
    branches = self.all_branches
    base_branches_dct = {}
    head_branches_dct = {}
    filtered_pulls = []
    filtered_branches_st = set()
    for branch in branches:
      base_branches_dct[branch.name] = []
      head_branches_dct[branch.name] = []
    for pull in pulls:
#       If the base/head branch name is not present in the branch list fetched with Pygithub function, that implies the corresponding base/head branch have been removed
#       In oreder to consider those PRs, whose head/base branch have been deleted, I inserted them in them in the else condition of both head and base dictionary
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
        for pull_nested in base_branches_dct[pull.head.ref]:
          if pull_nested.number not in pulls_visited_list:
            queue.append(pull_nested)
            pulls_visited_list.append(pull_nested.number)

    return filtered_pulls

  def compute(self):
    '''
        Logic:
        ---------- 
            Here the current_version and last_version are computed then,
              if the last_version is less than current_version then,
                a new release is created
              else if last_version is equal to current_version then,
                If there is a new merge between master and develop, since last release then,
                  remove the draft release
                  (remove only those draft release which are generated by GH Actions)
                  create a new draft release
                  (AVoids ambiguity, if some real human have changed the draft release)
              else
                NO CHANGE
    '''
    current_version = self.get_current_version()
    last_version = self.get_last_version()
#   self.get_release_message(current_version) # for testing
#   Here 2 strings (last_version and current_version) are compared
    if version.parse(last_version) < version.parse(current_version):
      self.remove_all_previous_draft_releases()
      tag_name = current_version
      tag_message = 'Default'
      release_name = self.get_release_name(tag_name)
      release_message = self.get_release_message(tag_name)
      is_draft = False
      is_prerelease = False
      release = self.create_release(tag_name, tag_message, release_name, release_message, is_draft, is_prerelease)
      print('New Release is successfuly created with tag name: ', release.tag_name)
      exit
    elif version.parse(last_version) == version.parse(current_version):
      print('The last_version is equal to the current version, So now we will create a draft release only if there is any merge since last release.')
      start_date = self.get_start_date_of_draft_release()
      if start_date is not None and len(self.get_pull_requests(start_date)) != 0: # there is a new merge since last release
        self.remove_all_previous_draft_releases()
        draft_release = self.create_new_draft_release()
        print('draft release is created successfully!', draft_release.tag_name)
        exit
      else:
        print('There is no new merge since last release!!!!!, action terminates here onwards')
        exit
    else:
      print('The current_version is smaller than the last version, which is not allowed, So the action terminates here onwards.')
      raise VersionCompareException()
  
  def remove_all_previous_draft_releases(self):
    '''
    LOGIC
    --------
          1. Fetch all the releases
          2. Iterate them
              if release is draft and draft release is created by GH Actions
                then remove that release
    '''
    all_releases = self.repo.get_releases()
    for release in all_releases:
      if release.draft and release.author.login == 'github-actions[bot]':
        release.delete_release()
        print('---Removed draft release tag_name:', release.tag_name)

  def create_new_draft_release(self):
    '''
    LOGIC
    --------
          1. It create new draft release with tag_name as specified
    
    Return
    --------
          draft_release:: OBJECT
    '''
    tag_name = self.draft_tag_name
    release_name = 'Draft release'
    release_message = self.get_release_message(self.draft_tag_name)
    is_draft = True
    is_prerelease = False
    draft_release = self.repo.create_git_release(tag_name, release_name, release_message, is_draft, is_prerelease)
    return draft_release


  
def main():
  print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
  release = CreateNewRelease()
  release.compute()
 
if __name__ == "__main__":
    main()
    
