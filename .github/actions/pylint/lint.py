import argparse
import logging
from pylint.lint import Run
import os
'''
    Logic
    ----------
    1. Extract the arguments[path, threshold]
    2. Print the logs of arguments.
    3. Call Run function from pylint to get result[reports].
    4. Extract the final score from results object.
    5. If the final score is smaller than threshold then Raise exception and fail the github action with appropriate logs message.
    6. Else Exit from the code with green tick of success and it's appropriate logs message.
'''

class PyLintComuptation:
  '''PyLintComuptation is class which extracts the command line arguments using argparser and fetch the score using Pylint and compare it with threshold[argument].
  '''
  def __init__(self):
    '''init function, 
       1. It set the level of runtime logging informations.
    '''
    logging.getLogger().setLevel(logging.INFO)

  def add_arguments(self, parser):
    '''
    Parameters
    ----------
    parser : object of Argparse
        parser is used to set the command line arguments.

    Returns
    -------
    None
    '''

    parser.add_argument('-p',
                    '--path',
                    help='path to directory you want to run pylint | '
                         'Default: %(default)s | '
                         'Type: %(type)s ',
                    default='./src',
                    type=str)

    parser.add_argument('-t',
                    '--threshold',
                    help='score threshold to fail pylint runner | '
                         'Default: %(default)s | '
                         'Type: %(type)s ',
                    default=7,
                    type=float)
  
  def compute(self):
    '''
    Parameters
    ----------
    None
    
    Logic
    ----------
    1. Declare the argparse object.
    2. Add proper arguments to argparse object.
    3. Extract the arguments[path, threshold]
    4. Print the logs of arguments.
    5. Call Run function from pylint to get result[reports].
    6. Extract the final score from results object.
    7. If the final score is smaller than threshold then Raise exception and fail the github action with appropriate logs message.
    8. Else Exit from the code with green tick of success and it's appropriate logs message.
    
    Returns
    -------
    None
    '''
    parser = argparse.ArgumentParser(prog="LINT")
    self.add_arguments(parser)
     
    args = parser.parse_args()
    path = str(args.path)
    threshold = float(args.threshold)

    logging.info('PyLint Starting | '
                 'Path: {} | '
                 'Threshold: {} |'.format(path, threshold))

#     results = Run([path], do_exit=False)
    path = './.github'
    pylint_opts = [ path, '--rcfile=./.pylintrc']
    results = Run(pylint_opts, do_exit=False)
    
    final_score = results.linter.stats['global_note']
    
    if final_score < threshold:

      message = ('PyLint Failed | '
                 'Score: {} | '
                 'Threshold: {} '.format(final_score, threshold))

      logging.error(message)
      print(message)
      raise Exception(message)

    else:
      message = ('PyLint Passed | '
                 'Score: {} | '
                 'Threshold: {} '.format(final_score, threshold))

      logging.info(message)
      print(message)

      exit(0)


def main():
  '''
  Parameters
  ----------
  None
  
  Logic
  ----------
  1. Create object of class PyLintComuptation.
  2. Call compute function of class PyLintComputation.
    
  Returns
  -------
  None
  '''
  print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
  d = './.github'
  for o in os.listdir(d):
    print('directory', o)
  lint = PyLintComuptation()
  lint.compute()
 
if __name__ == "__main__":
    main()
