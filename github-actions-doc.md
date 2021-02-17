# Github action enforces docstrings sanity, inline comments and improve documentation standards across repositories(PYTHON)

## Short Description
This github action is built on top of Pylint library which is a Python static code analysis tool which looks for programming errors, helps enforcing a coding standard, sniffs for code smells and offers simple refactoring suggestions. In workflow file, it installs the dependencies first and run the lint.py file with proper arguments, In lint.Py it executes the Pylint library functions and print the logs of its output. It uses customization file .pylintrc automatically.

## Trigger
This github action will be triggered when there is a push, with path as '**/py' or on pull request from master branch with path as '**.py'.

## Workflow
1. In Pylint github action workflow file.
2. Checkout branch
3. Install Dependencies
4. Run lint.py script which uses .pylintrc customization file.
5. Extract the arguments[path, threshold]
6. Print the logs of arguments.
7. Call Run function from pylint to get result[reports].
8. Extract the final score from results object.
9. If the final score is smaller than threshold then Raise exception and fail the github action with appropriate logs message.
10. Else Exit from the code with green tick of success and it's appropriate logs message.
11. Print the logs in output.
