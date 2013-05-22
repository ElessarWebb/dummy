from dummy import config
from dummy.models import Test, Metric
from dummy.statistics import Statistic
from dummy.runner import storage
from dummy.formatter.resultmanager import ResultManager

import os
import glob
import subprocess
import logging
import shutil

logger = logging.getLogger( __name__ )

class Runner:

	def __init__( self ):
		self.queue = [] # list of queued tests
		self.completed = [] # list of completed tests
		self.metrics = {} # list of metrics to collect
		self.results = [] # list of TestResult instances obtained
		self.statistics = {} # list of statistics to collect
		self.gathered_stats = {} # list of gathered statistics

		# load the metric and statistic instances from the config
		self.load_metrics()
		self.load_statistics()

	def add_test( self, test ):
		self.queue.append( test )

	def add_result( self, result ):
		self.results.append( result )

	def load_metrics( self ):
		for name, metric in config.METRICS.items():
			m = Metric.parse( name, metric )
			self.metrics[ name ] = m

			logger.debug( "Loaded metric `%s`" % m.name )

	def load_statistics( self ):
		for name, statistic in config.STATISTICS.items():
			s = Statistic.parse( name, statistic )
			self.statistics[ name ] = s

			logger.debug( "Loaded statistic `%s`" % s.name )

	def clean( self ):
		if os.path.isdir( config.TEMP_DIR ):
			shutil.rmtree( config.TEMP_DIR )

	def pre_test_hook( self, test ):
		for name, metric in self.metrics.items():
			metric.pre_test_hook( test )

	def run_test( self, test ):
		# run the pre test hooks
		logger.info( "Running pre-test hooks..." )
		self.pre_test_hook( test )

		# run the test
		# and save the TestResult
		logger.info( "Running test: `%s`" % test.name )
		self.results.append( test.run( self.metrics.values() ))

		# complete it
		self.completed.append( test )
		logger.info( "100% complete" )

	def gather_statistics( self, stats=None ):
		# default stats to all configured stats
		if stats is None: stats = self.statistics

		for s in stats.values():
			self.gathered_stats[ s.name ] = s.gather( self.results )
			logger.info( "Gathered statistic `%s`: %s" % ( s.name, self.gathered_stats[ s.name ]))

	def run( self ):
		""" run the tests in the queue
		"""
		self.clean()
		logger.info( 40*"-" )

		while len( self.queue ) != 0:
			test = self.queue.pop()
			self.run_test( test )
			logger.info( 40*"-" )

	def store( self ):
		for result in self.results:
			storage.store_result( result )

	def output( self, *metrics ):
		resultmanager = ResultManager( self.results )
		resultmanager.format( 'logger', *metrics )

# subprogram run
def run( args ):
	name = args.name
	runner = Runner()

	# discover the tests we need to run and add them to the runner
	# check if we need to run a whole test suite
	if args.suite:
		# make sure to have a valid test suite name
		try:
			suite = config.SUITES.get( name )
			logger.info( "Running test-suite `%s`" % name )
			for name in suite:
				for fname in Test.glob( name ):
					runner.add_test( Test( fname ))
		except KeyError:
			logger.error( "We looked, but a test suite with name `%s` was not found." % name )

	# if not running a whole suite
	# just queue the one named test
	else:
		for n in Test.glob( name ):
			runner.add_test( Test( n ))

	# run the tests
	runner.run()

	# gather the statistics as configured
	runner.gather_statistics()

	# store the results
	if args.store:
		runner.store()

def show( args ):
	runner = Runner()

	commit = 'HEAD'
	if args.commit is not None:
		logger.debug( "Loading result from committish `%s`" % args.commit )
		commit = args.commit

	tests = args.tests
	if args.suite:
		for suite_name in args.tests:
			# make sure to have a valid test suite name
			try:
				suite = config.SUITES.get( suite_name )
				logger.info( "Loading tests from suite `%s`" % suite_name )
				tests = []
				for name in suite:
					for fname in Test.glob( name ):
						logger.debug( "Adding test `%s` to tests." % fname )
						tests.append( fname )
			except KeyError:
					logger.error( "We looked, but a test suite with name `%s` was not found." % suite_name )

	for names in [ Test.glob( name ) for name in args.tests ]:
		for name in names:
			runner.add_result( storage.load_result( commit, name ))

	if args.metric is not None:
		runner.output( *args.metric )
	else:
		runner.output()
