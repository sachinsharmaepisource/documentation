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

## List of docstring checks(convention)
non-ascii-name (C0144):
 	%s name "%s" contains a non-ASCII unicode character Used when the name contains at least one non-ASCII unicode character.
invalid-name (C0103):
 	%s name "%s" doesn't conform to %s Used when the name doesn't conform to naming rules associated to its type (constant, variable, class...).
blacklisted-name (C0102):
 	Black listed name "%s" Used when the name is listed in the black list (unauthorized names).
singleton-comparison (C0121):
 	Comparison %s should be %s Used when an expression is compared to singleton values like True, False or None.
misplaced-comparison-constant (C0122):
 	Comparison should be %s Used when the constant is placed on the left side of a comparison. It is usually clearer in intent to place it in the right hand side of the comparison.
empty-docstring (C0112):
 	Empty %s docstring Used when a module, function, class or method has an empty docstring (it would be too easy ;).
missing-class-docstring (C0115):
 	Missing class docstring Used when a class has no docstring.Even an empty class must have a docstring.
missing-function-docstring (C0116):
 	Missing function or method docstring Used when a function or method has no docstring.Some special methods like __init__ do not require a docstring.
missing-module-docstring (C0114):
 	Missing module docstring Used when a module has no docstring.Empty modules do not require a docstring.
unidiomatic-typecheck (C0123):
 	Using type() instead of isinstance() for a typecheck. The idiomatic way to perform an explicit typecheck in Python is to use isinstance(x, Y) rather than type(x) == Y, type(x) is Y. Though there are unusual situations where these give different results.
single-string-used-for-slots (C0205):
 	Class __slots__ should be a non-string iterable Used when a class __slots__ is a simple string, rather than an iterable.
bad-classmethod-argument (C0202):
 	Class method %s should have %s as first argument Used when a class method has a first argument named differently than the value specified in valid-classmethod-first-arg option (default to "cls"), recommended to easily differentiate them from regular instance methods.
bad-mcs-classmethod-argument (C0204):
 	Metaclass class method %s should have %s as first argument Used when a metaclass class method has a first argument named differently than the value specified in valid-metaclass-classmethod-first-arg option (default to "mcs"), recommended to easily differentiate them from regular instance methods.
bad-mcs-method-argument (C0203):
 	Metaclass method %s should have %s as first argument Used when a metaclass method has a first argument named differently than the value specified in valid-classmethod-first-arg option (default to "cls"), recommended to easily differentiate them from regular instance methods.
missing-final-newline (C0304):
 	Final newline missing Used when the last line in a file is missing a newline.
line-too-long (C0301):
 	Line too long (%s/%s) Used when a line is longer than a given number of characters.
mixed-line-endings (C0327):
 	Mixed line endings LF and CRLF Used when there are mixed (LF and CRLF) newline signs in a file.
multiple-statements (C0321):
 	More than one statement on a single line Used when more than on statement are found on the same line.
too-many-lines (C0302):
 	Too many lines in module (%s/%s) Used when a module has too many lines, reducing its readability.
trailing-newlines (C0305):
 	Trailing newlines Used when there are trailing blank lines in a file.
trailing-whitespace (C0303):
 	Trailing whitespace Used when there is whitespace between the end of a line and the newline.
unexpected-line-ending-format (C0328):
 	Unexpected line ending format. There is '%s' while it should be '%s'. Used when there is different newline than expected.
superfluous-parens (C0325):
 	Unnecessary parens after %r keyword Used when a single item in parentheses follows an if, for, or other keyword.
wrong-import-order (C0411):
 	%s should be placed before %s Used when PEP8 import order is not respected (standard imports first, then third-party libraries, then local imports)
wrong-import-position (C0413):
 	Import "%s" should be placed at the top of the module Used when code and imports are mixed
useless-import-alias (C0414):
 	Import alias does not rename original package Used when an import alias is same as original package.e.g using import numpy as numpy instead of import numpy as np
import-outside-toplevel (C0415):
 	Import outside toplevel (%s) Used when an import statement is used anywhere other than the module toplevel. Move this import to the top of the file.
ungrouped-imports (C0412):
 	Imports from package %s are not grouped Used when imports are not grouped by packages
multiple-imports (C0410):
 	Multiple imports on one line (%s) Used when import statement importing multiple modules is detected.
unneeded-not (C0113):
 	Consider changing "%s" to "%s" Used when a boolean expression contains an unneeded negation.
consider-iterating-dictionary (C0201):
 	Consider iterating the dictionary directly instead of calling .keys() Emitted when the keys of a dictionary are iterated through the .keys() method. It is enough to just iterate through the dictionary itself, as in "for key in dictionary".
consider-using-enumerate (C0200):
 	Consider using enumerate instead of iterating with range and len Emitted when code that iterates with range and len is encountered. Such code can be simplified by using the enumerate builtin.
len-as-condition (C1801):
 	Do not use `len(SEQUENCE)` without comparison to determine if a sequence is empty Used when Pylint detects that len(sequence) is being used without explicit comparison inside a condition to determine if a sequence is empty. Instead of coercing the length to a boolean, either rely on the fact that empty sequences are false or compare the length against a scalar.
invalid-characters-in-docstring (C0403):
 	Invalid characters %r in a docstring Used when a word in docstring cannot be checked by enchant.
wrong-spelling-in-comment (C0401):
 	Wrong spelling of a word '%s' in a comment: Used when a word in comment is not spelled correctly.
wrong-spelling-in-docstring (C0402):
 	Wrong spelling of a word '%s' in a docstring: Used when a word in docstring is not spelled correctly.
