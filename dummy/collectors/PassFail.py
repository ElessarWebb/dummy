from dummy.collectors import Collector

class PassFail( Collector ):
	""" A class for Pass/Fail collecting
	"""

	def __init__( self ):
		super( type="value" )

	def collect( self, test ):
		# mimic script
		result = 'FAIL'
		with open( test.log_path(), 'r' ) as log:
			for line in log:
				if 'PASS' in line:
					result = 'PASS'

		return self.parse_output( result )
