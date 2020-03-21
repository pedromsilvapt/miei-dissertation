from typing import Any, cast
from ..voice import Voice
from .event import DurationEvent
from wave import Wave_read, open
from pathlib import Path
from subprocess import Popen, PIPE
import os

class SoundEvent( DurationEvent ):
    @staticmethod
    def is_optimized ( file : str ) -> bool:
        suffix : str = Path( file ).suffix.lower()

        if suffix == '.wav' or suffix == '.wave':
            wave : Wave_read = open( file, 'rb' )

            return wave.getnchannels() == 1 and wave.getsampwidth() == 2 and wave.getframerate() == 44100
        else:
            return False

    @staticmethod
    def optimize_folder ( input : str, output : str ):
        for file in os.listdir( input ):
            if os.path.isfile( os.path.join( input, file ) ):
                SoundEvent.optimize( os.path.join( input, file ), os.path.join( output, file ) )

    @staticmethod
    def optimize ( input : str, output : str ):
        p = Popen( 
            [ "ffmpeg", '-y', '-hide_banner', "-loglevel", "panic", "-i", input, "-vn", "-c:a", "pcm_s16le", "-ac", "1", '-ar', '44100', "-f", "wav", output ]
        )

        p.wait()

    @staticmethod
    def convert ( file : str ) -> Wave_read:
        p = Popen( 
            [ "ffmpeg", '-y', '-hide_banner', "-loglevel", "panic", "-i", file, "-vn", "-c:a", "pcm_s16le", "-ac", "1", '-ar', '44100', "-f", "wav", "-" ], 
            stdout = PIPE
        )

        return open( cast( Any, p.stdout ), 'rb' )
    
    @staticmethod
    def open_wave ( file : str ) -> Wave_read:
        suffix : str = Path( file ).suffix.lower()

        if suffix == '.wav' or suffix == '.wave':
            wave : Wave_read = open( file, 'rb' )

            if wave.getnchannels() != 1 or wave.getsampwidth() != 2 or wave.getframerate() != 44100:
                return SoundEvent.convert( file )

            return wave
        else:
            return SoundEvent.convert( file )
        

    def __init__ ( self, file : str, timestamp = 0, duration = None, value = None, velocity : int = 127, voice : Voice = None ):
        super().__init__( timestamp, duration, value, voice )

        self.file : str = file
        self.velocity : int = velocity
        self.wave : Wave_read = SoundEvent.open_wave( self.file )
        self.wave_duration : int = int( ( self.wave.getnframes() / float( self.wave.getframerate() ) ) * 1000 )
        
        if self.duration is None and self.value is None:
            self.duration = self.wave_duration

        if self.duration is not None and self.value is None:
            self.value = self.voice.from_duration_absolute( self.duration )
        elif self.duration is None and self.value is not None:
            self.duration = self.voice.get_duration( float( self.value ) )

    def __str__ ( self ) -> str:
        res = f"sample({ self.file })"

        if self.value != 1:
            res += str( self.value )
        
        return res
