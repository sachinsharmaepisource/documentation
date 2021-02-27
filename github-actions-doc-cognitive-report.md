# Check Docstrings and improve documentation standards across repositories(PYTHON)

## Short Description :file_folder:
This github action is built on top of Pylint library which is a Python static code analysis tool which looks for programming errors, helps enforcing a coding standard, sniffs for code smells and offers simple refactoring suggestions.This github action check the docstrings format and conventions, it these are not correct as per format, it will create review comment on the pull request.
  
## Workflows
  1. Fetch all the files from current reposity/branch.
  2. Filter files and keep only python files.
  3. Check docstring format of individual python files.
  4. Remove all previous review comments created by github action bot with label - [CHECK DOCSTRINGS].
  5. Create new review comments(annotations).
  
## Folder Structure
  1. .github/workflows/check-docstrings.yml (represents github action file)
  2. .github/actions/check-docstrings/action.yml (represents action file for github action)
  3. .github/actions/check-docstrings/Dockerfile.yml (represents Dockerfile)
  4. .github/actions/check-docstrings/requirements (represents requirements to be installed)
  5. .github/actions/check-docstrings/main.py (represents Python script)
  6. .github/actions/check-docstrings/entrypoint.sh (represents bash commands for dockerfile)
  7. .github/actions/check-docstrings/.pylintrc (represents bash commands for dockerfile)

