# -*- coding: utf-8 -*-
"""
--------------------------------------------------------------------------
Musical Synthesizer
--------------------------------------------------------------------------
License:   
Copyright 2019 Josh Stelling

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this 
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, 
this list of conditions and the following disclaimer in the documentation 
and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors 
may be used to endorse or promote products derived from this software without 
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE 
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

--------------------------------------------------------------------------
Background Information: 
    This code is used for a small musical synthesizer based around the 
    BeagleBoard PocketBeagle. The synthesizer can be used to play music as well
    as record what is being played to play it back on a repeating loop so that 
    the user can play concurrently with a recording that they make. The 
    synthesizer also has a built in metronome to help keep tempo, and a 
    potentiometer that can be used to change the timbre of the notes.


--------------------------------------------------------------------------
Notes:
        - This program is intended for use on the Hackster.io project listed below
          https://www.hackster.io/jas21/pocketbeagle-synthesizer-10f638
        - Inspiration was pulled from the following projects:
            https://www.hackster.io/etiennedesportes/pocket-synthesizer-785b50
            https://www.hackster.io/the-ohmonics/the-ohminator-analog-synthesizer-142dc7
            https://www.hackster.io/team-sunshine/keychain-synth-376159
            https://www.hackster.io/nickericlester/ir-breakbeam-candy-dispenser-with-zelda-music-c76e65
        
 
  
"""
import os
import time
import threading

import Adafruit_BBIO.ADC as ADC
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM



# ------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------

# Define PWM Pins for 3 speakers
metro_speaker = "P1_36"    
playback_speaker = "P2_3"    
live_speaker = "P2_1"    

# Define GPIO pins for 12 musical keys
key_c = "P1_2"
key_cs = "P1_4"
key_d = "P1_20"
key_ds = "P1_34"
key_e = "P2_2"
key_f = "P2_4"
key_fs = "P2_6"
key_g = "P2_8"
key_gs = "P2_10"
key_a = "P2_17"
key_as = "P2_18"
key_b = "P2_19"

# Potentiometer to control tempo
tempo_pot = "P1_19"

# Potentiometer to control timbre
timbre_pot = "P1_21"

# Switch to toggle record/playback
playback_switch = "P2_35"

# Current note tracker
current_note = 0

# Initialized recording list
recording = []

# Set initial timbre
Timbre = 50

#-------------------------------------------------------------------------
# Note Library
#-------------------------------------------------------------------------

# Notes library courtesy of Nicholas Lester
# https://www.hackster.io/nickericlester/ir-breakbeam-candy-dispenser-with-zelda-music-c76e65
NOTE_C4  = 262
NOTE_CS4 = 277
NOTE_D4  = 294
NOTE_DS4 = 311
NOTE_E4  = 330
NOTE_F4  = 349
NOTE_FS4 = 370
NOTE_G4  = 392
NOTE_GS4 = 415
NOTE_A4  = 440
NOTE_AS4 = 466
NOTE_B4  = 494


# Setup all GPIO pins as GPIO.IN
def setup():
    GPIO.setup(key_c, GPIO.IN)
    GPIO.setup(key_cs, GPIO.IN)
    GPIO.setup(key_d, GPIO.IN)
    GPIO.setup(key_ds, GPIO.IN)
    GPIO.setup(key_e, GPIO.IN)
    GPIO.setup(key_f, GPIO.IN)
    GPIO.setup(key_fs, GPIO.IN)
    GPIO.setup(key_g, GPIO.IN)
    GPIO.setup(key_gs, GPIO.IN)
    GPIO.setup(key_a, GPIO.IN)
    GPIO.setup(key_as, GPIO.IN)
    GPIO.setup(key_b, GPIO.IN)
    GPIO.setup(playback_switch, GPIO.IN)
    
    ADC.setup()
# end def

# Start definition for Live playback function
def play_note_hold(Note, Timbre):
    global current_note
    if not current_note == Note:
        PWM.start(live_speaker, Timbre, Note)
        current_note = Note
    time.sleep(.01)
# end def

# Turn off speaker (quicker than PWM.stop)
def speaker_off(Speaker):
    global current_note
    PWM.start(Speaker, 0, 1)
    current_note = 0
# end def

# Define thread for metronome functionality
class metThread(threading.Thread):
    tempo = None
    speaker = None
    # Take in speaker pin and tempo values
    def __init__(self, tempo, speaker):        # Basically the same for any class
        """Class initialization method"""
        threading.Thread.__init__(self)
        self.tempo   = tempo
        self.speaker   = speaker
        return
    # End def

    def run(self):
        """Class run method"""
        # While running, repeatedly beep while constantly checking tempo
        while(1):
            PWM.start(self.speaker, 50, 2000)
            time.sleep(0.1)
            PWM.start(self.speaker, 0, 2000)
            time.sleep(1-float(ADC.read(tempo_pot)))
        return
    
# Define thread for recording playback
class playbackThread(threading.Thread):
    speaker = None
    song = None
    # Take in song file and speaker pin as inputs
    def __init__(self, speaker, song):        # Basically the same for any class
        """Class initialization method"""
        threading.Thread.__init__(self)
        self.song   = song
        self.speaker   = speaker
        return
    # End def

    def run(self):
        """Class run method"""
        global recording
        global Timbre
        while(1):
            # While the playback switch is set to 1, don't playback 
            while(GPIO.input(playback_switch) == 1):
                pass
            song = recording;
            # While playback switch is 0, read through the song file and play
            while(GPIO.input(playback_switch) == 0):
                for i in range(0, len(song)):
                    print('ready')
                    PWM.start("P2_3", Timbre, song[i][0])
                    time.sleep(song[i][2] - song[i][1])
                    PWM.start("P2_3", 0, 100)
                    try:
                        time.sleep(song[i+1][1] - song[i][2])
                    except:
                        pass
                    
                                        
        return



# end def

# Define the main live playback function
def task():
    """Execute the main program."""
    
    global recording
    global Timbre
    while(1):
        # If the playback switch is set to record (1), initialise the recording
        # file and take note of the time
        if (GPIO.input(playback_switch) == 1):
            t = time.time()
            recording = []

            while(GPIO.input(playback_switch) == 1):
                # Set timbre of sound by changing duty cycle
                Timbre = (float(ADC.read(timbre_pot))+0.001)*88
                
                
                # Wait for button press
                # When a button is pressed, record the time that the putton was
                # pressed, play the associated note, and record the time that
                # the button is released. Then, append the note, start, and stop
                # to the recording file.
                if(GPIO.input(key_c) == 1):
                    start = time.time()-t
                    while(GPIO.input(key_c) == 1):
                        play_note_hold(NOTE_C4, Timbre)
                    end = time.time()-t
                    recording.append((NOTE_C4, start, end))
                    

                if(GPIO.input(key_cs) == 1):
                    start = time.time()-t
                    while(GPIO.input(key_cs) == 1):
                        play_note_hold(NOTE_CS4, Timbre)
                    end = time.time()-t
                    recording.append((NOTE_CS4, start, end))
                    

                if(GPIO.input(key_d) == 1):
                    start = time.time()-t
                    while(GPIO.input(key_d) == 1):
                        play_note_hold(NOTE_D4, Timbre)
                    end = time.time()-t
                    recording.append((NOTE_D4, start, end))
                    

                if(GPIO.input(key_ds) == 1):
                    start = time.time()-t
                    while(GPIO.input(key_ds) == 1):
                        play_note_hold(NOTE_DS4, Timbre)
                    end = time.time()-t
                    recording.append((NOTE_DS4, start, end))
                    

                if(GPIO.input(key_e) == 1):
                    start = time.time()-t
                    while(GPIO.input(key_e) == 1):
                        play_note_hold(NOTE_E4, Timbre)
                    end = time.time()-t
                    recording.append((NOTE_E4, start, end))
                    

                if(GPIO.input(key_f) == 1):
                    start = time.time()-t
                    while(GPIO.input(key_f) == 1):
                        play_note_hold(NOTE_F4, Timbre)
                    end = time.time()-t
                    recording.append((NOTE_F4, start, end))
                    

                if(GPIO.input(key_fs) == 1):
                    start = time.time()-t
                    while(GPIO.input(key_fs) == 1):
                        play_note_hold(NOTE_FS4, Timbre)
                    end = time.time()-t
                    recording.append((NOTE_FS4, start, end))
                    

                if(GPIO.input(key_g) == 1):
                    start = time.time()-t
                    while(GPIO.input(key_g) == 1):
                        play_note_hold(NOTE_G4, Timbre)
                    end = time.time()-t
                    recording.append((NOTE_G4, start, end))
                    

                if(GPIO.input(key_gs) == 1):
                    start = time.time()-t
                    while(GPIO.input(key_gs) == 1):
                        play_note_hold(NOTE_GS4, Timbre)
                    end = time.time()-t
                    recording.append((NOTE_GS4, start, end))
                    

                if(GPIO.input(key_a) == 1):
                    start = time.time()-t
                    while(GPIO.input(key_a) == 1):
                        play_note_hold(NOTE_A4, Timbre)
                    end = time.time()-t
                    recording.append((NOTE_A4, start, end))
                    

                if(GPIO.input(key_as) == 1):
                    start = time.time()-t
                    while(GPIO.input(key_as) == 1):
                        play_note_hold(NOTE_AS4, Timbre)
                    end = time.time()-t
                    recording.append((NOTE_AS4, start, end))
                    

                if(GPIO.input(key_b) == 1):
                    start = time.time()-t
                    while(GPIO.input(key_b) == 1):
                        play_note_hold(NOTE_B4, Timbre)
                    end = time.time()-t
                    recording.append((NOTE_B4, start, end))
                    

                # Turn off speaker between notes
                speaker_off(live_speaker)
                
                
        # If not set in recording mode
        if(GPIO.input(playback_switch) == 0):
            
            while(GPIO.input(playback_switch) == 0):
                
                # Set timbre of sound by changing duty cycle
                Timbre = (float(ADC.read(timbre_pot))+0.001)*88
                
                # Wait for button press. Similar to other playback, but without 
                # recording anything
                while(GPIO.input(key_c) == 1):
                    play_note_hold(NOTE_C4, Timbre)
                    
                
                while(GPIO.input(key_cs) == 1):
                    play_note_hold(NOTE_CS4, Timbre)
                    
                
                while(GPIO.input(key_d) == 1):
                    play_note_hold(NOTE_D4, Timbre)
                    
                
                while(GPIO.input(key_ds) == 1):
                    play_note_hold(NOTE_DS4, Timbre)
        
                
                while(GPIO.input(key_e) == 1):
                    play_note_hold(NOTE_E4, Timbre)
        
                
                while(GPIO.input(key_f) == 1):
                    play_note_hold(NOTE_F4, Timbre)
        
                
                while(GPIO.input(key_fs) == 1):
                    play_note_hold(NOTE_FS4, Timbre)
        
                
                while(GPIO.input(key_g) == 1):
                    play_note_hold(NOTE_G4, Timbre)
        
                
                while(GPIO.input(key_gs) == 1):
                    play_note_hold(NOTE_GS4, Timbre)
        
                
                while(GPIO.input(key_a) == 1):
                    play_note_hold(NOTE_A4, Timbre)
        
                
                while(GPIO.input(key_as) == 1):
                    play_note_hold(NOTE_AS4, Timbre)
        
                
                while(GPIO.input(key_b) == 1):
                    play_note_hold(NOTE_B4, Timbre)
                    
                # Turn off speaker between notes
                speaker_off(live_speaker)
            
# End def


# ------------------------------------------------------------------------
# Main script
# ------------------------------------------------------------------------

if __name__ == '__main__':
    # Setup pins
    setup()
    # Define threads
    t1 = metThread(tempo_pot, metro_speaker)
    t2 = playbackThread(playback_speaker, recording)
    # Start each thread
    try:
        t1.start()
        t2.start()
        task()
    except KeyboardInterrupt:
        pass
    
    # After keyboard interupt, stop PWMs and join threads
    main_thread = threading.currentThread()
    for t in threading.enumerate():
        if t is not main_thread:
            try:
                t.join()
            except KeyboardInterrupt:
                pass
            
    PWM.stop(playback_speaker)
    PWM.stop(metro_speaker)
    PWM.stop(live_speaker)
    PWM.cleanup()
    