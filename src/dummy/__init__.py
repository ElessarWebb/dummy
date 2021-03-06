""" The Dummy generic test results framework
"""
import os
import sys
import logging
import imp

logger = logging.getLogger( __name__ )

__all__ = ( "get_version", "config" )
__version__ = "0.1.0"

def get_version():
	""" Return the version of Dummy
	"""
	return __version__

def find_config():
	cur = os.getcwd()

	while True:
		path = os.path.realpath( os.path.join( cur, "dummyconfig.py" ))
		if os.path.exists( path ): return path
		else:
			nextd = os.path.realpath( os.path.join( cur, ".." ))
			if cur == nextd: break # done
			else: cur = nextd

	# if not returned, no config found
	raise AssertionError( "Reached root. No dummyconfig.py found" )

# import the project configuration
# if this fails we cannot proceed
try:
	# operate from the root
	# and import the dummyconfig from it
	confpath = find_config()
	os.chdir( os.path.dirname( confpath ))
	userconfig = imp.load_source( 'dummyconfig', confpath )
except ImportError as e:
	# clearify the error a bit
	logger.error( "Project configuration could not be imported." )
	logger.debug( "ImportError message: `%s`" % str( e ))

	# reraise for stacktrace
	raise

# default config values
defaults = {
	'SUITES': {},
	'METRICS': {},
	'STATISTICS': {},
	'TEMP_DIR': '.tmp',
	'TESTS_DIR': 'tests',
	'TEST_OUTPUT_DIR': '.tmp/logs',
	'TARGET_DIR': 'results',
	'SRC_DIR': 'src',
	'INPUT_ENCODING': 'utf8',
	'ENV': {},
	'TEST_RUNNER': 'bin/run.sh',
	'DEFAULT_TARGET': 'default',
	'TARGETS': {},
	'LOCK_FILE': '.tmp/.lock'
}

# set the defaults
# if the userconfig hasn't got them defined
for key, value in defaults.items():
	if not hasattr( userconfig, key ):
		setattr( userconfig, key, value )

class Config( object ):

	def __init__( self ):
		# default the target name
		self.target = 'default'

	def set_target( self, target ):
		self.target = target

	def STORAGE_DIR( self, test, commit ):
		""" Returns the paths to the storage directory of a test result
		"""
		return os.path.join( self.TARGET_DIR, commit, self.target, test.name )

	def __getattr__( self, attr ):
		if self.target != "default":
			# if a target name is set
			# try to get the override from the target configuration
			try:
				return userconfig.TARGETS[ self.target ][ attr ]

			# if that fails, fallback to default configuration
			# which should always succeed if a valid configuration setting name is given,
			# because we defaulted that configuration
			except KeyError:
				pass

		return getattr( userconfig, attr )

# finally create the global configuration instance
config = Config()
