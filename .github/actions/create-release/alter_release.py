"""
  This mudule consists of AlterRelease Class,
    constructor attributes :: Repo
  
  This module consists of following functions:
  - remove_all_previous_draft_releases
  - create_new_draft_release
  - create_release
"""

import sys
import os
sys.path.append(os.path.abspath("./.github/actions/create-release"))
from constants import * # pylint: disable=wrong-import-position, wildcard-import
from get_release_message import GetReleaseMessage # pylint: disable=wrong-import-position


class AlterRelease:
  """
  AlterRelease Class,
    constructor attributes :: Repo
  
  This module consists of following functions:
  - remove_all_previous_draft_releases
  - create_new_draft_release
  - create_release
  
  """
  def __init__(self, repo):
    self.repo = repo
    self.branch = constants['branch']
    self.draft_tag_name = constants['draft_tag_name']
    
    get_release_message_obj = GetReleaseMessage(self.repo)
    self.get_release_message = get_release_message_obj.get_release_message
  
  def remove_all_previous_draft_releases(self):
    """
    LOGIC
    --------
          1. Fetch all the releases
          2. Iterate them
              if release is draft and draft release is created by GH Actions
                then remove that release
    """
    all_releases = self.repo.get_releases()
    for release in all_releases:
      if release.draft and release.author.login == 'github-actions[bot]':
        release.delete_release()
        print('---Removed draft release tag_name:', release.tag_name)

  def create_new_draft_release(self):
    """
    LOGIC
    --------
          1. It create new draft release with tag_name as specified
    Returns
    --------
          draft_release : Object
            Draft release object
    """
    tag_name = self.draft_tag_name
    release_name = 'Draft release'
    release_message = self.get_release_message(self.draft_tag_name)
    is_draft = True
    is_prerelease = False
    draft_release = self.repo.create_git_release(tag_name, release_name, release_message, is_draft, is_prerelease) # pylint: disable=line-too-long
    return draft_release
  
  def create_release(self, create_release_args):  
    # https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html#github.Repository.Repository.create_git_tag_and_release # pylint: disable=line-too-long
    """
        Parameters
        ----------
            create_release_args : dictionary
              dictionary of arguments includes
                tag_name : String(v0.0.1)
                  tag name
                tag_message : String
                  tag message
                release_name : String
                  release name
                release_message : String
                  release message
                is_draft : Boolean
                  is draft
                is_prerelease : Boolean
                  is prerelease
        Logic
        --------
            1. A branch reference is fetched for commit SHA
            2. A tag is created with respective parameters
            3. A reference to tag is created using tag SHA
            4. A release is created with respective tag

        Returns
        --------
          release : Object
              Reference to the new release created
    """
    tag_name = create_release_args['tag_name']
    tag_message = create_release_args['tag_message']
    release_name = create_release_args['release_name']
    release_message = create_release_args['release_message']
    is_draft = create_release_args['is_draft']
    is_prerelease = create_release_args['is_prerelease']
    
    branch = self.repo.get_branch(self.branch)
    tag = self.repo.create_git_tag(tag_name, tag_message, branch.commit.sha, 'commit')
    self.repo.create_git_ref('refs/tags/' + tag_name, tag.sha)
    release = self.repo.create_git_release(tag.tag, release_name, release_message, is_draft, is_prerelease) # pylint: disable=line-too-long
    return release
