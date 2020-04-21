from musikla.audio.sequencers.abc.sequencer import ABCSequencer
from musikla.core.events import MusicEvent
from .sequencer import Sequencer, SequencerFactory
from typing import Optional
from pathlib import Path
from tempfile import gettempdir, gettempprefix

class HTMLSequencer ( Sequencer ):
    def __init__ ( self, filename : str ):
        super().__init__()

        self.filename : str = filename

        temp : str = f"{ gettempdir() }/{ gettempprefix() }-{ Path( filename ).name }.abc"

        self.abc_sequencer : ABCSequencer = ABCSequencer( temp )
    
    @property
    def playing ( self ):
        return self.abc_sequencer.playing

    def build ( self ) -> str:
        abc = str( self.abc_sequencer.file_builder.build() )

        template = f"""<html>
    <head>
        <link rel="stylesheet" href="http://dev.music.free.fr/css/music.min.css" />
        <script src="http://dev.music.free.fr/js/abc-ui-1.0.0.min.js"></script>
    </head>
    <body>
        <div class="abc-source">
            {abc}
        </div>
        <script>
            $ABC_UI.init();
        </script>
    </body>
</html>
"""

        return template

    def get_time ( self ):
        return self.abc_sequencer.get_time()

    def on_event ( self, event : MusicEvent ):
        self.abc_sequencer.register_event( event )
    
    def on_close ( self ):
        self.abc_sequencer.close()

        with open( self.filename, 'w' ) as f:    
            f.write( self.build() )
                
            f.flush()

    def join ( self ):
        pass

    def start ( self ):
        self.abc_sequencer.start()

class HTMLSequencerFactory( SequencerFactory ):
    def init ( self ):
        self.name = 'html'
    
    def from_str ( self, uri : str, args ) -> Optional[HTMLSequencer]:
        suffix = ( Path( uri ).suffix or '' ).lower()

        if suffix == '.html' or suffix == '.htm':
            return HTMLSequencer( uri )
        
