# Cognitive Report

## Short Description :file_folder:
  This github action computes cognitive complexity and create review comments on pull request with proper comments.
  
## Workflows
  1. Fetch all the files from current pull request that have been updated.
  2. Filter files and keep only python files.
  3. Compute cognitive complexity of individual python files.
  4. Remove all previous review comments created by github action bot.
  5. Create new review comments(annotations).
  
## Folder Structure
  1. .github/workflows/cognitive-complexity.yml (represents github action file)
  2. .github/actions/cognitive-complexity/action.yml (represents action file for github action)
  3. .github/actions/cognitive-complexity/Dockerfile.yml (represents Dockerfile)
  4. .github/actions/cognitive-complexity/requirements (represents requirements to be installed)
  5. .github/actions/cognitive-complexity/main.py (represents Python script)
  6. .github/actions/cognitive-complexity/entrypoint.sh (represents bash commands for dockerfile)
