#/usr/bin/python
import sys
import argparse
import os

# make sure to add the dummy module directory to the path
sys.path.append(
	os.path.abspath( os.path.join( os.path.dirname( __file__ ), '../' ))
)

parser = argparse.ArgumentParser( description='Dummy test aggregation' )
sub = parser.add_subparsers()

# debug switch
parser.add_argument(
	'-D',
	'--debug',
	help="output stacktrace on error",
	action="store_true"
)

# `dummy <test>`
runner = sub.add_parser( 'run', help="run tests" )
runner.add_argument( 'name', help="test name (or suite name if -S is given)" )
runner.add_argument(
	'-s',
	'--suite',
	help="interpret `test` argument as the name of a test suite",
	action="store_true"
)

runner.set_defaults( func='run' )

if __name__ == "__main__":
	args = parser.parse_args()

	# run the subprogram
	try:
		# do this here, to prevent to catch
		# errors from loading the configuration
		from dummy.runner import run

		if not hasattr( args, 'func' ): parser.print_help()
		elif args.func == 'run': run( args )
	except Exception as e:
		# to trace or not to trace
		if args.debug:
			raise e
		else:
			print( "Error: %s" % str( e ))
