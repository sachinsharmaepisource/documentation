
import argparse
import logging
from pylint.lint import Run


logging.getLogger().setLevel(logging.INFO)

parser = argparse.ArgumentParser(prog="LINT")

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

# custom --convention=numpy
parser.add_argument('--convention',
                    '--convention',
                    help='convention to format to be used | '
                         'Default: %(default)s | '
                         'Type: %(type)s ',
                    default='numpy',
                    type=str)

args = parser.parse_args()
path = str(args.path)
threshold = float(args.threshold)
convention = str(args.convention)

logging.info('PyLint Starting | '
             'Path: {} | '
             'Threshold: {} |'
             'Convention: {}'.format(path, threshold, convention))

results = Run([path], convention='numpy', do_exit=False)

final_score = results.linter.stats['global_note']

if final_score < threshold:

    message = ('PyLint Failed | '
               'Score: {} | '
               'Threshold: {} '.format(final_score, threshold))

    logging.error(message)
    raise Exception(message)

else:
    message = ('PyLint Passed | '
               'Score: {} | '
               'Threshold: {} '.format(final_score, threshold))

    logging.info(message)

    exit(0)
