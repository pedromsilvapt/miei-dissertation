from typing import Optional, Union

class Instrument():
    @staticmethod
    def from_program ( program : int, bank : int = None, soundfont : Union[int, str] = None ) -> 'Instrument':
        return Instrument( GeneralMidi.get_name( program ), program, bank, soundfont )

    def __init__ ( self, name : str, program : int, bank : int = None, soundfont : Union[int, str] = None ):
        self.name : str = name
        self.program : int = program
        self.bank : Optional[int] = bank
        self.soundfont : Optional[Union[int, str]] = soundfont

class GeneralMidi():
    @staticmethod
    def get_name ( program : int ) -> str:
        for attr in dir( program ):
            if attr.startswith( "_" ): continue

            if hasattr( GeneralMidi, attr ) and getattr( GeneralMidi, attr ) == program:
                return attr
        
        return "(Unknown)"

    # Piano
    AcousticGrandPiano = 1
    BrightAcousticPiano = 2
    ElectricGrandPiano = 3
    HonkyTonkPiano = 4
    ElectricPiano1 = 5
    ElectricPiano2 = 6
    Harpsichord = 7
    Clavinet = 8

    # Chromatic Percussion
    Celesta = 9
    Glockenspiel = 10
    MusicBox = 11
    Vibraphone = 12
    Marimba = 13
    Xylophone = 14
    TubularBells = 15
    Dulcimer = 16

    # Organ
    DrawbarOrgan = 17
    PercussiveOrgan = 18
    RockOrgan = 19
    ChurchOrgan = 20
    ReedOrgan = 21
    Accordion = 22
    Harmonica = 23
    TangoAccordion = 24

    # Guitar
    AcousticGuitarNylon = 25
    AcousticGuitarSteel = 26
    ElectricGuitarJazz = 27
    ElectricGuitarClean = 28
    ElectricGuitarMuted = 29
    OverdrivenGuitar = 30
    DistortionGuitar = 31
    GuitarHarmonics = 32

    # Bass
    AcousticBass = 33
    ElectricBassFinger = 34
    ElectricBassPick = 35
    FretlessBass = 36
    SlapBass1 = 37
    SlapBass2 = 38
    SynthBass1 = 39
    SynthBass2 = 40

    # Strings
    Violin = 41
    Viola = 42
    Cello = 43
    Contrabass = 44
    TremoloStrings = 45
    PizzicatoStrings = 46
    OrchestralHarp = 47
    Timpani = 48

    # Ensemble
    StringEnsemble1 = 49
    StringEnsemble2 = 50
    SynthStrings1 = 51
    SynthStrings2 = 52
    ChoirAahs = 53
    VoiceOohs = 54
    SynthChoir = 55
    OrchestraHit = 56

    # Brass
    Trumpet = 57
    Trombone = 58
    Tuba = 59
    MutedTrumpet = 60
    FrenchHorn = 61
    BrassSection = 62
    SynthBrass1 = 63
    SynthBrass2 = 64

    # Reed
    SopranoSax = 65
    AltoSax = 66
    TenorSax = 67
    BaritoneSax = 68
    Oboe = 69
    EnglishHorn = 70
    Bassoon = 71
    Clarinet = 72

    # Pipe
    Piccolo = 73
    Flute = 74
    Recorder = 75
    PanFlute = 76
    BlownBottle = 77
    Shakuhachi = 78
    Whistle = 79
    Ocarina = 80

    # Synth Lead
    Lead1Square = 81
    Lead2Sawtooth = 82
    Lead3Calliope = 83
    Lead4Chiff = 84
    Lead5Charang = 85
    Lead6Vvoice = 86
    Lead7Fifths = 87
    Lead8BassLead = 88

    # Synth Pad
    Pad1NewAge = 89
    Pad2Warm = 90
    Pad3Polysynth = 91
    Pad4Choir = 92
    Pad5Bowed = 93
    Pad6Metallic = 94
    Pad7Halo = 95
    Pad8Sweep = 96

    # Synth Effects
    FX1Rain = 97
    FX2Soundtrack = 98
    FX3Crystal = 99
    FX4Atmosphere = 100
    FX5Brightness = 101
    FX6Goblins = 102
    FX7Echoes = 103
    FX8SciFi = 104

    # Ethnic
    Sitar = 105
    Banjo = 106
    Shamisen = 107
    Koto = 108
    Kalimba = 109
    Bagpipe = 110
    Fiddle = 111
    Shanai = 112

    # Percussive
    TinkleBell = 113
    Agogo = 114
    SteelDrums = 115
    Woodblock = 116
    TaikoDrum = 117
    MelodicTom = 118
    SynthDrum = 119
    ReverseCymbal = 120

    # Sound effects
    GuitarFretNoise = 121
    BreathNoise = 122
    Seashore = 123
    BirdTweet = 124
    TelephoneRing = 125
    Helicopter = 126
    Applause = 127
    Gunshot = 128
