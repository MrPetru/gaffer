//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2014, John Haddon. All rights reserved.
//  Copyright (c) 2017, Image Engine Design Inc. All rights reserved.
//
//  Redistribution and use in source and binary forms, with or without
//  modification, are permitted provided that the following conditions are
//  met:
//
//      * Redistributions of source code must retain the above
//        copyright notice, this list of conditions and the following
//        disclaimer.
//
//      * Redistributions in binary form must reproduce the above
//        copyright notice, this list of conditions and the following
//        disclaimer in the documentation and/or other materials provided with
//        the distribution.
//
//      * Neither the name of John Haddon nor the names of
//        any other contributors to this software may be used to endorse or
//        promote products derived from this software without specific prior
//        written permission.
//
//  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
//  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
//  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
//  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
//  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
//  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
//  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
//  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
//  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
//  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
//  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//
//////////////////////////////////////////////////////////////////////////

#include "IECore/Exception.h"

#include "GafferUI/TranslateHandle.h"

using namespace Imath;
using namespace IECore;
using namespace GafferUI;

IE_CORE_DEFINERUNTIMETYPED( TranslateHandle );

TranslateHandle::TranslateHandle( Style::Axes axes )
	:	Handle( defaultName<TranslateHandle>() ), m_axes( Style::X )
{
	setAxes( axes );
}

TranslateHandle::~TranslateHandle()
{
}

void TranslateHandle::setAxes( Style::Axes axes )
{
	if( axes == m_axes )
	{
		return;
	}

	if( axes > Style::Z )
	{
		/// \todo Support XYZ as motion in the camera plane,
		/// and XY, XZ and YZ as motion in those planes.
		throw IECore::Exception( "Unsupported axes" );
	}

	m_axes = axes;
 	requestRender();
}

Style::Axes TranslateHandle::getAxes() const
{
	return m_axes;
}

float TranslateHandle::translation( const DragDropEvent &event ) const
{
	return m_drag.position( event ) - m_drag.startPosition();
}

void TranslateHandle::renderHandle( const Style *style, Style::State state ) const
{
	style->renderTranslateHandle( m_axes, state );
}

void TranslateHandle::dragBegin( const DragDropEvent &event )
{
	V3f handle( 0.0f );
	handle[m_axes] = 1.0f;
	m_drag = LinearDrag( this, LineSegment3f( V3f( 0 ), handle ), event );
}
