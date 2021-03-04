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

import os
import sys
from configparser import ConfigParser
from github import Github
from packaging import version

sys.path.append(os.path.abspath("./.github/actions/create-release"))
from alter_release import *
from get_pull_requests import *
from get_release_message import *
from constants import *



class VersionCompareException(Exception):
  """
    Exception raised for errors.
    Attributes:
        message -- explanation of the error
  """
  def __init__(self, message="Current version < last version, kindly update the version.ini(current version) file."):
        self.message = message
        super().__init__(self.message)
#---------------------------------------------------------------------------------------------------------

class ReleaseGithubAction:
  def __init__(self):
    self.repo_name = self.get_inputs('REPO_NAME')
    constants['REPO_NAME'] = self.repo_name
    self.access_token = self.get_inputs('ACCESS_TOKEN')
    self.user_name = self.get_inputs('USER_NAME')
    self.gh = Github(self.access_token)
    self.repo = self.gh.get_repo(self.user_name)
    self.all_branches = self.repo.get_branches()
    self.version_file_path = constants['VERSION_FILE_PATH']
    self.branch = constants['branch']
    self.draft_tag_name = constants['draft_tag_name']
    self.emoji_list = constants['emoji_list']
    self.categories_dct = constants['categories_dct']
    
    alter_release_obj = AlterRelease(self.repo)
    self.create_release = alter_release_obj.create_release
    self.remove_all_previous_draft_releases = alter_release_obj.remove_all_previous_draft_releases
    self.create_new_draft_release = alter_release_obj.create_new_draft_release
    get_pull_requests_obj = GetPullRequests(self.repo)
    self.get_pull_requests = get_pull_requests_obj.get_pull_requests
    get_release_message_obj = GetReleaseMessage(self.repo)
    self.get_release_message = get_release_message_obj.get_release_message
    self.get_release_name = get_release_message_obj.get_release_name
    self.get_release_message = get_release_message_obj.get_release_message
    
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

  def read_file_content(self, file_path):
    '''
      Parameters
      ----------
          file_path: String
              Path to file to read content from
      Return
      ----------
          content: String
    '''
    return self.repo.get_contents(file_path, self.branch).decoded_content.decode()

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
      latest_release = self.repo.get_latest_release()
      last_version = latest_release.tag_name
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
  
  def versions_are_equal_and_new_merges_since_last_release(self, last_version, current_version, start_date):
    '''
      Parameters
      ----------
          last_version: String
          current_version: String
          start_date: Date
      Return
      ----------
          Bool: Bool
    '''
    compare_versions = version.parse(last_version) == version.parse(current_version)
    check_pr_since_last_release = start_date is not None and len(self.get_pull_requests(start_date)) != 0
    return compare_versions and (check_pr_since_last_release)
  
  def versions_are_equal_and_no_new_merge_since_last_release(self, last_version, current_version, start_date):
    '''
      Parameters
      ----------
          last_version: String
          current_version: String
          start_date: Date
      Return
      ----------
          Bool: Bool
    '''
    compare_versions = version.parse(last_version) == version.parse(current_version)
    check_pr_since_last_release = start_date is not None and len(self.get_pull_requests(start_date)) != 0
    return compare_versions and not(check_pr_since_last_release)

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
    start_date = self.get_start_date_of_draft_release()
#   self.get_release_message(current_version) # for testing
#   Here 2 strings (last_version and current_version) are compared
    if version.parse(last_version) < version.parse(current_version):
      self.remove_all_previous_draft_releases()
      create_release_args = {
        'tag_name': current_version,
        'tag_message': 'Default',
        'release_name': self.get_release_name(current_version),
        'release_message': self.get_release_message(current_version),
        'is_draft': False,
        'is_prerelease': False,
      }
      release = self.create_release(create_release_args)
      print('New Release is successfuly created with tag name: ', release.tag_name)
    elif self.versions_are_equal_and_new_merges_since_last_release(last_version, current_version, start_date):
      print('last_version = current version and there is a new merge since last release')
      # there is a new merge since last release
      self.remove_all_previous_draft_releases()
      draft_release = self.create_new_draft_release()
      print('draft release is created successfully!', draft_release.tag_name)
    elif self.versions_are_equal_and_no_new_merge_since_last_release(last_version, current_version, start_date):
      print('The last_version is equal to the current version')
      print('There is no new merge since last release!!!!!, action terminates here onwards')
    else:
      print('The current_version is smaller than the last version, which is not allowed.')
      raise VersionCompareException()

def main():
  """
  Here class object is created and compute function is called.
  """
  release = ReleaseGithubAction()
  release.compute()
  
if __name__ == "__main__":
    main()
