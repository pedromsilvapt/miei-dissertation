from musikla.core.events.event import VoiceEvent
from musikla.core.events.transformers import ComposeNotesTransformer, ComposeChordsTransformer, VoiceIdentifierTransformer, AnnotateTransformer, EnsureOrderTransformer
from musikla.core.events import MusicEvent
from .sequencer import Sequencer, SequencerFactory
from typing import List, Optional
from pathlib import Path
import json

class DebugSequencer ( Sequencer ):
    def __init__ ( self, filename : str ):
        super().__init__()

        self.filename : str = filename

        self.events : List[MusicEvent] = []
        
        self.set_transformers(
            ComposeNotesTransformer(),
            ComposeChordsTransformer(),
            VoiceIdentifierTransformer(),
            AnnotateTransformer()
        )
    
    @property
    def playing ( self ):
        return True

    def build ( self ) -> str:
        items = list()
        groups = list()
        # groups.append( {
        #     'id': 'default',
        #     'content': 'Default'
        # } )
        # groups.append( {
        #     'id': '<voiceless>',
        #     'content': '<Voiceless>'
        # } )

        for i, event in enumerate( self.events ):
            voice_name = "<voiceless>"

            if isinstance( event, VoiceEvent ) and event.voice is not None:
                voice_name = event.voice.name

            group_name = f"{voice_name}: { event.staff }"

            if not any( g[ 'id' ] == group_name for g in groups ):
                groups.append( { 'id': group_name, 'content': group_name } )

            obj = {
                'id': i,
                'content': str( event ),
                'title': str( event ),
                'start': event.timestamp,
                'group': group_name,
                'type': 'point'
            }

            if event.end_timestamp > event.timestamp:
                obj[ 'type'] = 'range'
                obj[ 'end' ] = event.end_timestamp

            items.append( obj )

        template = f"""<html>
    <head>
        <script type="text/javascript" src="http://unpkg.com/vis-timeline@latest/standalone/umd/vis-timeline-graph2d.min.js"></script>
        <link href="http://unpkg.com/vis-timeline@latest/styles/vis-timeline-graph2d.min.css" rel="stylesheet" type="text/css" />
        <style type="text/css">
            #visualization {{
                width: 100%;
                height: 800px;
                border: 1px solid lightgray;
            }}
        </style>
    </head>
    <body>
        <div id="visualization"></div>
        <div id="details"></div>
        <script type="text/javascript">
        // DOM element where the Timeline will be attached
        var container = document.getElementById('visualization');

        var detailsContainer = document.getElementById('details');

        // Create a DataSet (allows two way data-binding)
        var groups = { json.dumps( groups ) }

        var items = new vis.DataSet( { json.dumps( items ) } );

        // Configuration for the Timeline
        var options = {{
            multiselect: true,
            groupHeightMode: 'fixed'
        }};

        // Create a Timeline
        var timeline = new vis.Timeline(container, items, groups, options);

        timeline.on( 'select', e => {{
            if ( e.items.length == 0 ) {{
                detailsContainer.innerHTML = '';
            }} else {{
                detailsContainer.innerHTML = e.items
                    .map( id => items.get( id ) )
                    .map( ev => "<p>" + ev.content + " [" + ev.start + " - " + ev.end + " = " + ( ev.end - ev.start ) + "]" + "</p>" )
                    .join( '' );
            }}
        }} );
        </script>
    </body>
</html>
"""

        return template

    def get_time ( self ):
        return 0

    def on_event ( self, event : MusicEvent ):
        self.events.append( event )
    
    def on_close ( self ):
        with open( self.filename, 'w' ) as f:    
            f.write( self.build() )
                
            f.flush()

    def join ( self ):
        pass

    def start ( self ):
        pass

class DebugSequencerFactory( SequencerFactory ):
    def init ( self ):
        self.name = 'debug'
    
    def from_str ( self, uri : str, args ) -> Optional[DebugSequencer]:
        suffix = ( Path( uri ).suffix or '' ).lower()

        if suffix == '.html' or suffix == '.htm':
            return DebugSequencer( uri )
        
