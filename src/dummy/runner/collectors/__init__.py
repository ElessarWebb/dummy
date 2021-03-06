import os
import json

from dummy.utils import git

class Collector( object ):
	""" Abstract base class Collector
	"""

	# output types
	VALUE = 'value'
	JSON = 'json'

	TYPE_CHOICES = ( VALUE, JSON )

	def __init__( self, type="value" ):
		assert type in Collector.TYPE_CHOICES, "Unknown collector type: `%s`" % type
		self.type = type

	def pre_test_hook( self, test ):
		pass

	def collect( self, test ):
		""" Run this collector on the given TestResult.
		"""
		raise NotImplementedError( "Not implemented" )

	def store_result_file( self, test, name, content ):
		path = os.path.join( test.env()[ 'RESULTS_DIR' ], name )
		with open( path, 'w' ) as fh:
			fh.write( content )

	def parse_output( self, output ):
		""" Parse the output of the collection script if necessary

			returns:
				parsed output or unchanged output if type == VALUE
		"""
		if self.type == Collector.JSON:
			try:
				output = json.loads( output )
			except ValueError as e:
				raise ValueError( "Collector `%s` did not return valid JSON: %s" % ( self.path,
				str( e )))

		return output
