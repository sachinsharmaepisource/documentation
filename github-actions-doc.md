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
9. [FINAL SCORE] Evaluation = 10.0 - ((float(5 * error + warning + refactor + convention) / statement) * 10)
10. If the final score is smaller than threshold then Raise exception and fail the github action with appropriate logs message.
11. Else Exit from the code with green tick of success and it's appropriate logs message.
12. Print the logs in output.



## CHECKS
### This list contains major checks from .pylintrc file.
1. The docstring must contains respective parameters, Exceptions and return documentations as per format. [Added with pylint.extensions.docparams and pylint.extensions.docstyle extensions in MASTER section of .pylintrc file].
2. max-nested-blocks=5 ::  Maximum number of nested blocks for function / method body
3. argument-naming-style=snake_case :: Naming style matching correct argument names.
4. attr-naming-style=snake_case :: Naming style matching correct attribute names.
5. const-naming-style=UPPER_CASE :: Naming style matching correct constant names.
6. method-naming-style=snake_case :: Naming style matching correct method names.
7. module-naming-style=snake_case :: Naming style matching correct module names.
8. variable-naming-style=snake_case :: Naming style matching correct variable names.
9. ignore-comments=yes :: # Ignore comments when computing similarities.
10. ignore-docstrings=yes :: # Ignore docstrings when computing similarities.
11. min-similarity-lines=4 :: # Minimum lines number of a similarity.
12. max-args=5 :: # Maximum number of arguments for function / method.
13. max-attributes=7 :: # Maximum number of attributes for a class (see R0902).
14. max-bool-expr=5 :: # Maximum number of boolean expressions in an if statement.
15. max-branches=12 :: # Maximum number of branch for function / method body.
16. max-returns=6 :: # Maximum number of return / yield for function / method body.
17. max-statements=50 :: # Maximum number of statements in function / method body.
18. min-public-methods=2 :: # Minimum number of public methods for a class (see R0903).
19. docstring-min-length=-1 :: Minimum line length for functions/classes that require docstrings, shorter ones are exempt.
