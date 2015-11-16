##########################################################################
#
#  Copyright (c) 2015, Image Engine Design Inc. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#      * Redistributions of source code must retain the above
#        copyright notice, this list of conditions and the following
#        disclaimer.
#
#      * Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided with
#        the distribution.
#
#      * Neither the name of John Haddon nor the names of
#        any other contributors to this software may be used to endorse or
#        promote products derived from this software without specific prior
#        written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##########################################################################

import os
import shutil
import unittest
import subprocess

import IECore

import Gaffer
import GafferTest
import GafferImage

class ResampleTest( GafferTest.TestCase ) :

	def testDataWindow( self ) :

		r = GafferImage.Resample()
		r["dataWindow"].setValue(
			IECore.Box2f(
				IECore.V2f( 10.5, 11.5 ),
				IECore.V2f( 20.5, 21.5 )
			)
		)

		self.assertEqual(
			r["out"]["dataWindow"].getValue(),
			IECore.Box2i(
				IECore.V2i( 10, 11 ),
				IECore.V2i( 21, 22 )
			)
		)

	def testExpectedOutput( self ) :

		def __test( fileName, size, filter ) :

			inputFileName = os.path.dirname( __file__ ) + "/images/" + fileName

			reader = GafferImage.ImageReader()
			reader["fileName"].setValue( inputFileName )

			resample = GafferImage.Resample()
			resample["in"].setInput( reader["out"] )
			resample["dataWindow"].setValue( IECore.Box2f( IECore.V2f( 0 ), IECore.V2f( size.x, size.y ) ) )
			resample["filter"].setValue( filter )
			resample["boundingMode"].setValue( GafferImage.Sampler.BoundingMode.Clamp )

			crop = GafferImage.Crop()
			crop["in"].setInput( resample["out"] )
			crop["area"].setValue( IECore.Box2i( IECore.V2i( 0 ), size ) )

			outputFileName = self.temporaryDirectory() + "/%s_%dx%d_%s.exr" % ( os.path.splitext( fileName )[0], size.x, size.y, filter )
			writer = GafferImage.ImageWriter()
			writer["in"].setInput( crop["out"] )
			writer["fileName"].setValue( outputFileName )
			writer.execute()

			result = GafferImage.ImageReader()
			result["fileName"].setValue( writer["fileName"].getValue() )

			expected = GafferImage.ImageReader()
			expected["fileName"].setValue(
				"%s/images/%s_%dx%d_%s.exr" % (
					os.path.dirname( __file__ ),
					os.path.splitext( fileName )[0],
					size.x,
					size.y,
					filter
				)
			)

			self.assertFalse(
				IECore.ImageDiffOp()(
					imageA = expected["out"].image(),
					imageB = result["out"].image()
				).value
			)

			# Enable to write out images for visual comparison with OIIO.
			# The images will appear in a "resampleComparison" subdirectory
			# of the current directory.
			if False :

				if not os.path.exists( "resampleComparison" ) :
					os.makedirs( "resampleComparison" )

				shutil.copyfile( outputFileName, "resampleComparison/gaffer_" + os.path.basename( outputFileName ) )

				oiioOutputFileName = "resampleComparison/oiio_%s_%dx%d_%s.exr" % ( os.path.splitext( fileName )[0], size.x, size.y, filter )

				subprocess.check_call(
					"oiiotool --threads 1 %s --ch R,G,B --resize:filter=%s %dx%d  -o %s" %
					(
						inputFileName,
						filter,
						size.x, size.y,
						oiioOutputFileName
					),
					shell = True
				)

		tests = [
			( "resamplePatterns.exr", IECore.V2i( 4 ), "lanczos3" ),
			( "resamplePatterns.exr", IECore.V2i( 40 ), "box" ),
			( "resamplePatterns.exr", IECore.V2i( 101 ), "gaussian" ),
			( "resamplePatterns.exr", IECore.V2i( 119 ), "mitchell" ),
		]

		for args in tests :
			__test( *args )

	def testSincUpsize( self ) :

		c = GafferImage.Constant()
		c["format"].setValue( GafferImage.Format( 100, 100 ) )
		c["color"].setValue( IECore.Color4f( 1 ) )

		r = GafferImage.Resample()
		r["dataWindow"].setValue( IECore.Box2f( IECore.V2f( 0 ), IECore.V2f( 400 ) ) )
		r["boundingMode"].setValue( GafferImage.Sampler.BoundingMode.Clamp )
		r["filter"].setValue( "sinc" )
		r["in"].setInput( c["out"] )

		i = r["out"].image()
		self.assertEqual( i["R"].data, IECore.FloatVectorData( [ 1.0 ] * 400 * 400 ) )

	def testExpandDataWindow( self ) :

		d = IECore.Box2i( IECore.V2i( 5, 6 ), IECore.V2i( 101, 304 ) )
		c = GafferImage.Constant()
		c["format"].setValue( GafferImage.Format( d ) )

		r = GafferImage.Resample()
		r["in"].setInput( c["out"] )
		r["dataWindow"].setValue( IECore.Box2f( IECore.V2f( d.min ), IECore.V2f( d.max ) ) )
		r["filter"].setValue( "box" )
		self.assertEqual( r["out"]["dataWindow"].getValue(), d )

		r["expandDataWindow"].setValue( True )
		self.assertEqual( r["out"]["dataWindow"].getValue(), IECore.Box2i( d.min - IECore.V2i( 1 ), d.max + IECore.V2i( 1 ) ) )

		r["filterWidth"].setValue( IECore.V2f( 10 ) )
		self.assertEqual( r["out"]["dataWindow"].getValue(), IECore.Box2i( d.min - IECore.V2i( 5 ), d.max + IECore.V2i( 5 ) ) )

if __name__ == "__main__":
	unittest.main()