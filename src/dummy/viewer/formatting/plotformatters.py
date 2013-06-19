from dummy.viewer.formatting import ResultFormatter
import logging

logger = logging.getLogger( __name__ )

try:
	import pylabs

	class PlotFormatter( ResultFormatter ):

		def __init__( self, *args, **kwargs ):
			super( PlotFormatter, self ).__init__( self, *args, **kwargs )

		def format_results( self, results, *metrics ):
			assert len( results ) > 0, "No results to format"

			# create the figure
			fig = pylab.figure( facecolor='white' )

			# get the xlabels
			x = range( 1, len( results ) + 1 )
			xlabels = [ r.test.name for r in results ]

			pylab.title( 'Metric values per test (commit: %s)' % results[0].commit, fontsize=22 )
			pylab.xticks( rotation=20 )
			pylab.grid( True, markevery='integer' )
			pylab.xlabel( 'tests', fontsize=16 )
			pylab.margins( 0.05 )
			pylab.xticks( x, xlabels )

			# create the plots
			for metric in metrics:
				self.format_metric( results, metric )

			# and show it
			pylab.legend()
			pylab.show()

		def format_metric( self, results, metric ):
			x = range( 1, len( results ) + 1 )
			y = [ t.get_metric( metric ) for t in results ]

			try:
				plot = pylab.plot( x, y )
				pylab.setp( plot,
					label=metric,
					linestyle='dashed',
					linewidth=1.0,
					marker=".",
					markersize=12.0,
					aa=True
				)
			except ( ValueError, TypeError ) as e:
				raise Exception(
					"The metric `%s` is not numeric and can thus not be plotted." % metric
				)
except ImportError:

	class PlotFormatter():

		def __init__( self, *args, **kwargs ):
			raise ImportError( "PlotFormatter is not available. matplotlib is not installed" )

	logger.debug( "matplotlib is not installed, PlotFormatter not available." )
