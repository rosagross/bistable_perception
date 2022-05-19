#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@time    :   2022/02/10 13:31:09
@author  :   rosagross
@contact :   grossmann.rc@gmail.com
'''

import numpy as np
import os
import re
from datetime import datetime
from psychopy import visual
from psychopy.hardware import keyboard
from exptools2.core import PylinkEyetrackerSession
from trial import BPTrial
from stimulus_rivalry import BRStimulus
from stimulus_rotating_sphere import RSStimulus
import random

opj = os.path.join

class BistablePerceptionSession(PylinkEyetrackerSession):

    def __init__(self, output_str, output_dir, settings_file, subject_ID, eyetracker_on, task):
        """
        Parameters
        ----------
        output_str : str
            Basename for all output-files (like logs)
        output_dir : str
            Path to desired output-directory (default: None, which results in $pwd/logs)
        settings_file : str
            Path to yaml-file with settings (default: None, which results in the package's
            default settings file (in data/default_settings.yml)
        subject_ID : int
            ID of the current participant
        eyetracker_on : bool 
            Determines if the cablibration process is getting started.
        """

        super().__init__(output_str, output_dir, settings_file, eyetracker_on=eyetracker_on)
    	
        self.subject_ID = subject_ID
        self.task = task

        # load task setting from settings.yml file
        self.stimulus_names = self.settings['Task settings']['Stimulus names']
        self.previous_percept_duration = self.settings['Task settings']['Previous percept duration']
        self.percept_jitter = self.settings['Task settings']['Percept duration jitter']
        self.stim_dur_ambiguous = self.settings['Task settings']['Stimulus duration ambiguous']
        self.n_blocks = self.settings['Task settings']['Blocks'] 
        self.n_practice_blocks = self.settings['Task settings']['Blocks practice']         
        self.response_interval = self.settings['Task settings']['Response interval']
        self.break_duration = self.settings['Task settings']['Break duration']
        self.exit_key = self.settings['Task settings']['Exit key']
        self.break_buttons = self.settings['Task settings']['Break buttons'] 
        self.monitor_refreshrate = self.settings['Task settings']['Monitor refreshrate']
        self.screentick_conversion = self.settings['Task settings']['Screentick conversion']
        self.test_eyetracker = self.settings['Task settings']['Test eyetracker']
        self.break_stim_name = self.settings['Stimulus settings']['Break stimulus name']
        

        if self.settings['Task settings']['Screenshot']==True:
            self.screen_dir=output_dir+'/'+output_str+'_Screenshots'
            if not os.path.exists(self.screen_dir):
                os.mkdir(self.screen_dir)

        # this determines how fast our stimulus images change, so the speed of the rotation 
        self.screenticks_per_frame = int(self.monitor_refreshrate/self.screentick_conversion)

        # randomly choose if the participant responds with the right BUTTON to stimulus 1 or 2
        if random.uniform(1,100) < 50:
            self.response_button = 'upper_stim1'
        else:
            self.response_button = 'upper_stim2'

        # initialize the keyboard for the button presses
        self.kb = keyboard.Keyboard()

        # count the subjects responses for each condition
        self.unambiguous_responses = 0 
        self.ambiguous_responses = 0 
        self.total_responses = 0  
        
        # variables needed for trial and block creation
        self.trial_list = []
        self.stimulus_index_list = []
        self.practice_blocks = []
        self.trial_nr = 0

        # ambiguous phase durations 
        self.nr_phases_ambig = int(self.stim_dur_ambiguous*self.monitor_refreshrate/self.screenticks_per_frame)
        self.amb_phase_dur = [self.screenticks_per_frame]*self.nr_phases_ambig
        self.break_phase_durations = [self.screenticks_per_frame]*int(self.break_duration*self.monitor_refreshrate/self.screenticks_per_frame)

        # define which condition starts (equal subjects are 0, unequal 1)
        # either start with ambiguous or unambiguous 
        self.start_condition = 0 if self.subject_ID % 2 == 0 else 1 

        # make all the trials beforehand and load experiment specific stimuli
        self.create_stimuli()        
        self.create_trials()


    def create_trials(self):
        """
        Creates the trials with its phase durations and randomization. 
        One trial looks like the following, depending on the block type
        """
        self.trial_nr = 1
        
        for i in range(self.n_blocks):  
            # we start counting with 1 because the blocks with ID 0 are breaks!
            block_ID = i + 1 

            print("\ncurrent block is", block_ID)
            print("start condition", self.start_condition)
            
            # start off with a break
            self.trial_list.append(BPTrial(self, 0, block_ID, 'break', 'break', 'break', self.break_phase_durations, 'frames', self.stimulus_index_list_break))
            
            # equal subjects start with rivarly, unequal with unambiguous
            if (block_ID + self.start_condition) % 2 == 0:
                block_type = 'ambiguous'
                trial_type = 'ambiguous'

                if self.task == 'BR':
                    # determine type and color combination
                    np.random.shuffle(self.colors_rivalry)
                    color_comb = 'rivalry_' + self.colors_rivalry[0] 
                    self.colors_rivalry = self.colors_rivalry[1:]
                    # add the fitting stimuli indices to the stimulus list
                    stimulus_index = self.stimuli.lookup_list.index(color_comb)
                    stimulus_index_list = [stimulus_index]*len(self.amb_phase_dur)
                
                elif self.task == 'RS':
                    # the rotating globe has no color combination 
                    color_comb = np.NaN
                    # add the fitting stimuli indices to the stimulus list
                    stimulus_index_list = []
                    # loop over the phase duration array 
                    for phase_index in range(len(self.amb_phase_dur)):
                        frame_index = (phase_index+1)%self.stimuli.nr_of_frames
                        stimulus_index = self.stimuli.lookup_list.index(f'ambiguous_{frame_index}')
                        stimulus_index_list.append(stimulus_index)
                
                self.trial_list.append(BPTrial(self, self.trial_nr, block_ID, block_type, trial_type, color_comb, self.amb_phase_dur, 'frames', stimulus_index_list))
                self.trial_nr += 1 


            else:
                block_type = 'unambiguous'

                phase_durations_unambiguous = self.create_duration_array()
                print("durations unambiguous:", phase_durations_unambiguous)

                if self.task == 'BR':
                    np.random.shuffle(self.colors_ambiguous)
                    color_comb = self.colors_ambiguous[0] 
                    self.colors_ambiguous = self.colors_ambiguous[1:]

                # create an unambiguous block
                for i, phase_duration in enumerate(phase_durations_unambiguous):
                    # determine if next trial shows stimulus 1 or 2
                    
                    if self.task == 'BR':
                        trial_type = 'house' if self.trial_nr % 2 == 0 else 'face'
                        # we have to insert the transition period here (except for the last trial)
                        # the trial nr, block ID and block and trial type stay the same as for the previous trial 
                        # get the correct color combination
                        if (trial_type=='house') & (color_comb=='redface'):
                            fading_color = 'hb2fr'
                        elif (trial_type=='face') & (color_comb=='redface'):
                            fading_color = 'fr2hb'
                        elif (trial_type=='house') & (color_comb=='redhouse'):
                            fading_color = 'hr2fb'
                        else:
                            fading_color = 'fb2hr'
                        
                        fading_index_list = []
                        for i in len(self.images_per_combi):
                            # choose stimulus from list depending on fading color
                            stimulus_index = self.stimuli.lookup_list.index(fading_color+f'_{i}')
                            fading_index_list.append(stimulus_index)

                        if self.nr_fading_stimuli != 0:
                            unambiguous_stimulus_index = self.stimuli.lookup_list.index(color_comb)
                            
                            # cut out the beginning and end of trial because the transition takes time (but the e)
                            if ((i == len(phase_durations_unambiguous)-1) or (i == 0)):
                                print('last or first')
                                phase_duration_total = phase_duration - int(self.stimuli.transition_length/2) # in the beginning/end only cut half 
                                prefading_phases = [self.screenticks_per_frame]*(phase_duration_total/self.screenticks_per_frame)
                                print('phases before fading', prefading_phases)
                                
                                stimulus_index_list = [unambiguous_stimulus_index]*len(prefading_phases)

                                # make trial for the period before the fading begins
                                self.trial_list.append(BPTrial(self, trial_nr, block_ID, block_type, trial_type, color_comb, prefading_phases, 'frames', stimulus_index_list))
                                if i == 0:
                                    print('first transition')
                                    print('transition phases', self.transition_phases)
                                    # make fading trial
                                    self.trial_list.append(BPTrial(self, trial_nr, block_ID, block_type, trial_type, fading_color, self.transition_phases, 'frames', fading_index_list))
                                
                            else:
                                print('phase duration before', phase_duration)
                                phase_duration_total = phase_duration - self.transition_length
                                prefading_phases = [self.screenticks_per_frame]*(phase_duration_total/self.screenticks_per_frame)
                                stimulus_index_list = [unambiguous_stimulus_index]*len(prefading_phases)

                                self.trial_list.append(BRTrial(self, trial_nr, block_ID, block_type, trial_type, color_comb, prefading_phases, 'frames', stimulus_index_list))
                                self.trial_list.append(BRTrial(self, trial_nr, block_ID, block_type, trial_type, fading_color, self.transition_phases, 'frames', fading_index_list))
                                
                        else:
                            unambiguous_phases = [self.screenticks_per_frame]*(phase_duration/self.screenticks_per_frame)
                            stimulus_index_list = [unambiguous_stimulus_index]*len(unambiguous_phases)
                            self.trial_list.append(BPTrial(self, trial_nr, block_ID, block_type, trial_type, color_comb, [phase_duration], 'frames', stimulus_index_list))

                    elif self.task == 'RS':

                        # create the unambiguous trials 
                        unambiguous_block = self.create_unambiguous_block(phase_durations_unambiguous, block_ID, block_type)
                        # .. and append it to the trial list
                        self.trial_list = [*self.trial_list, *unambiguous_block]


    def create_stimuli(self):
       
        # depending on the experiment, we create different stimuli objects
        if self.task == 'BR':

            # create an experiment specific stimulus object, which creates a list of all unique stimuli
            self.stimuli = BRStimulus(self.settings, self.win)

            # build an array with the possible color combinations 
            # (has to be done BEFORE we construct the trials below)
            color_combinations = ['redface', 'redhouse']
            colors_list = []
            # add the colorcombination alternatingly 
            for i in range(int(self.n_blocks/2)):
                # if there is an odd nr. of trials we should choose the last block randomly!
                if ((self.n_blocks%2) != 0) and (i == self.n_blocks-1):
                    idx = 0 if random.uniform(1,100) < 50 else 1
                else:
                    idx = 0 if (i%2)==0 else 1 
                    
                colors_list.append(color_combinations[idx])

            self.colors_rivalry = np.array(colors_list)
            self.colors_ambiguous = np.array(colors_list)
            self.transition_phases = [self.screenticks_per_frame]*int(self.stimuli.transition_length/self.screenticks_per_frame)

        elif self.task == 'RS':
            self.stimuli = RSStimulus(self.settings, self.win)
        
        else:    
            print('Invalid experiment ID entered!')
            self.close()

        # get the stimulus index for the breaks
        stimulus_index_break = self.stimuli.lookup_list.index(self.break_stim_name)
        self.stimulus_index_list_break = [stimulus_index_break]*len(self.break_phase_durations)


    def create_unambiguous_block(self, stim_duration_list, block_ID, block_type):
        '''
        This function creates a list full of left and right rotation unambiguous trials.
        It is used for creating practice and actual experiment blocks.
        '''
        # the block will start at the beginning of the total frames of the stimulus
        last_frame_previous = 0 
        dummy = 0 # need this to add the previous last frame from the trial before
        block_list = [] # this is where we store the trials prior to concatenating them to the suitable trial list

        # the durations should determine the switch between left and right rotation
        for i, stim_duration in enumerate(stim_duration_list):
            # determine if next trial shows house or face
            trial_type = 'right' if self.trial_nr % 2 == 0 else 'left'

            # create the phase durations depending on the duration of the stimulus
            nr_phases_unambig = int(stim_duration/self.screenticks_per_frame)
            phase_durations_unambiguous = [self.screenticks_per_frame]*nr_phases_unambig
            
            # TODO: write function for computing the indice lists! (reocurring snippet..)
            # loop over the phases
            stimulus_index_list = []
            for phase_index in range(len(phase_durations_unambiguous)):
                frame_index = (phase_index+last_frame_previous+1)%self.stimuli.nr_of_frames
                stimulus_index = self.stimuli.lookup_list.index(f'ambiguous_{frame_index}')
                stimulus_index_list.append(stimulus_index)

            # the number of phases also tells us which image was the last one, so that
            # the next rotation can start from there
            last_frame_previous = (last_frame_previous+dummy)%self.nr_of_frames
            if trial_type == 'right':
                last_frame_previous = self.nr_of_frames - last_frame_previous 
            elif trial_type == 'left':
                last_frame_previous = abs(last_frame_previous - self.nr_of_frames)
            self.trial_nr += 1 
            block_list.append(BPTrial(self, self.trial_nr, block_ID, block_type, trial_type, np.NaN, phase_durations_unambiguous,'frames', stimulus_index_list))
            # save old value and update new one
            dummy = last_frame_previous
            last_frame_previous = nr_phases_unambig


    def create_duration_array(self):
        """
        Function that takes the duration entries from the setting file and constructs the 
        phase duration (duration of trial and ISI) for all trials. 
        The jitter is added to the mean percept duration from previous studies. If the jitter is
        0.1s, a random nr between -0.1 and 0.1 is added. 
        """

        if isinstance(self.previous_percept_duration, list):
            print('Use predefined phase durations')
            phase_durations = [elem*self.screenticks_per_frame for elem in self.previous_percept_duration]
            np.random.shuffle(phase_durations)
        else:
            # while the number is not above the trial duration, generate more trial durations
            max_duration = self.stim_dur_ambiguous
            nr_frames_total = max_duration*self.monitor_refreshrate
            frames_percept_duration = self.previous_percept_duration*self.monitor_refreshrate
            jitter_in_frames = int(self.percept_jitter*self.monitor_refreshrate)
            current_duration = 0 
            phase_durations = []
            while True:
                percept_duration = frames_percept_duration + random.randrange(-jitter_in_frames, jitter_in_frames)
                current_duration = np.array(phase_durations).sum() + percept_duration
                if current_duration > nr_frames_total:
                    break
                
                phase_durations.append(int(percept_duration))
                
            current_duration = np.array(phase_durations).sum()
            duration_difference = int(nr_frames_total - current_duration)
            # append whats missing to the last trial
            phase_durations.append(duration_difference)

        print("duration unambiguous block:", np.array(phase_durations).sum(), "and length:", len(phase_durations))
        print(phase_durations)
        return phase_durations

    def draw_stimulus(self):
        """
        Depending on what phase we are in, this function draws the apropriate stimulus.
        """

        index = self.current_trial.stimulus_index_list[self.current_trial.phase]
        self.stimuli.unique_stimulus_list[index].draw()

    def wait_for_yesno(self, text):
        '''
        This function is used to implement a yes or no response. 
        If the key pressed 'y' it returns True, if 'n' it returns false. 
        '''

        stim = visual.TextStim(self.win, text=text)
        stim.draw()
        self.win.flip()
        wait_for_key = True
        while wait_for_key:
            keys = self.kb.getKeys(keyList=['y', 'n'])  
            for key in keys:
                if key.name == 'y':
                    answer = True
                    wait_for_key = False
                elif key.name == 'n':
                    answer = False
                    wait_for_key = False
        return answer


    def run(self):
        print("-------------RUN SESSION---------------")
        
        if self.eyetracker_on:
            self.calibrate_eyetracker()
            self.start_recording_eyetracker()

        if self.response_button == 'upper_stim1':
            button_instructions = f'Upper - {self.stimulus_names[0]}\n Lower - {self.stimulus_names[1]}'
        else:
            button_instructions = f'Upper - {self.stimulus_names[1]}\n Lower - {self.stimulus_names[0]}'
        
        self.display_text(button_instructions, keys='space')
   
        # this method actually starts the timer which keeps track of trial onsets
        self.start_experiment()
        self.kb.clock.reset()
            
        self.kb.clock.reset()
        for trial in self.trial_list:
            self.current_trial = trial 
            self.current_trial_start_time = self.kb.clock.getTime()
            # the run function is implemented in the parent Trial class, so our Trial inherited it
            self.current_trial.run()

        self.display_text('End. \n Well done!:)', keys='space')
        self.close()






        
