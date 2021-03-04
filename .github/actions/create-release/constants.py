"""
  This file consists of all the constant attributes used in create-release github action.
"""

constants = {
  'VERSION_FILE_PATH': 'version.ini',
  'branch': 'combined',
  'draft_tag_name': 'draft-tag-name',
  'emoji_list': { 'features': '🚀', 'documentation': '📚', 'refactor': '♻️', 'bug fix': '🐛', 'others': '💡' },
  'categories_dct': { 'features': {}, 'documentation': {}, 'refactor': {}, 'bug fix': {}, 'others': {} },
  
  'REPO_NAME': '' # WIll be initialized during run time by main.py file
}
