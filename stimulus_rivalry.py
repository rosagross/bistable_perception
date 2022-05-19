#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@time    :   2022/02/09 17:33:27
@author  :   rosagross
@contact :   grossmann.rc@gmail.com
'''

from psychopy import visual
import numpy as np
import os
import re
opj = os.path.join


class BRStimulus():
    """ 
    This class implements the construction of the trials in the experiment. 
    There are different trial types:
    - unambiguous (left or right wards moving)
    - ambiguous (not clear which direction), in this trial, nothing changes over the whole duration of the trial

    Every trial begins with a 10s break.
    """

    def __init__(self, settings, win, *args, **kwargs):
        
        # setting for loading the correct stimulus
        self.settings = settings
        self.path_to_stim = self.settings['Stimulus settings']['Stimulus path']
        self.stim_size = self.settings['Stimulus settings']['Stimulus size']
        self.nr_fading_stimuli = self.settings['Stimulus settings']['Nr fading stimuli']
        self.transition_length = self.settings['Stimulus settings']['Transition length']
        self.break_stim_name = self.settings['Stimulus settings']['Break stimulus name']
        self.screentick_conversion = self.settings['Task settings']['Screentick conversion']
        self.monitor_refreshrate = self.settings['Task settings']['Monitor refreshrate']
        self.screenticks_per_frame = int(self.monitor_refreshrate/self.screentick_conversion)
        self.win = win
        self.unique_stimulus_list = self.load_stimuli()
        self.lookup_list = self.create_lookup_list()



        print('check if stimulus list and look-up list have the same length')
        print(len(self.unique_stimulus_list)==len(self.lookup_list))

    def load_stimuli(self):
        """ 
        This function creates house, face and rivalry stmiulus, as well as the fixation background. 
        The color of the stimulus can either be red or blue. This alternates among blocks.
        """

        # simple, unambiguous non-fading stimuli 
        self.house_red = visual.ImageStim(self.win, image=self.path_to_stim+'house_red.bmp', units='deg', size=self.stim_size)
        self.house_blue = visual.ImageStim(self.win, image=self.path_to_stim+'house_blue.bmp', units='deg', size=self.stim_size)
        self.face_red = visual.ImageStim(self.win, image=self.path_to_stim+'face_red.bmp', units='deg', size=self.stim_size)
        self.face_blue = visual.ImageStim(self.win, image=self.path_to_stim+'face_blue.bmp', units='deg', size=self.stim_size)
        # ambiguous stimuli
        self.rivalry_redface = visual.ImageStim(self.win, image=self.path_to_stim+'rivalry_redface.bmp', units='deg', size=self.stim_size)
        self.rivalry_redhouse = visual.ImageStim(self.win, image=self.path_to_stim+'rivalry_redhouse.bmp', units='deg', size=self.stim_size)
        self.fixation_screen = visual.ImageStim(self.win, image=self.path_to_stim+'fixation_screen.bmp', units='deg', size=self.stim_size)
        # fading stimuli
        self.fading_bluehouse_2_redface = []
        self.fading_redhouse_2_blueface = []
        self.fading_redface_2_bluehouse = []
        self.fading_blueface_2_redhouse = []
        
        fading_step = 0
        self.images_per_combi = int(self.transition_length/self.screenticks_per_frame)
        transition_step = int(self.nr_fading_stimuli/self.images_per_combi)
        for i in range(self.images_per_combi):
            self.fading_bluehouse_2_redface.append(visual.ImageStim(self.win, image=self.path_to_stim+f'fading/fading_hb2fr_{fading_step}.bmp', units='deg', size=self.stim_size))
            self.fading_redhouse_2_blueface.append(visual.ImageStim(self.win, image=self.path_to_stim+f'fading/fading_hr2fb_{self.nr_fading_stimuli-1-fading_step}.bmp', units='deg', size=self.stim_size))
            self.fading_redface_2_bluehouse.append(visual.ImageStim(self.win, image=self.path_to_stim+f'fading/fading_hb2fr_{self.nr_fading_stimuli-1-fading_step}.bmp', units='deg', size=self.stim_size))
            self.fading_blueface_2_redhouse.append(visual.ImageStim(self.win, image=self.path_to_stim+f'fading/fading_hr2fb_{fading_step}.bmp', units='deg', size=self.stim_size))
            fading_step += transition_step

        unique_stimulus_list = [self.house_red, self.house_blue, self.face_red, self.face_blue, self.rivalry_redface, self.rivalry_redhouse, self.fixation_screen] 
        unique_stimulus_list = unique_stimulus_list + self.fading_bluehouse_2_redface + self.fading_redhouse_2_blueface + self.fading_redface_2_bluehouse + self.fading_blueface_2_redhouse
        return unique_stimulus_list

    def create_lookup_list(self):
        # normal stimuli 0-4
        # rivalry stimuli 5-7
        # fixation screen 8
        # fading stimuli 9-end
        stimuli_names = ['house_red', 'house_blue', 'face_red', 'face_blue', 'rivalry_redface', 'rivalry_redhouse', 'fixation_screen']
        hb2fr_fading_names = []
        hr2fb_fading_names = []
        fr2hb_fading_names = []
        fb2hr_fading_names = []

        for i in range(self.images_per_combi):
            hb2fr_fading_names.append('hb2fr' + f'_{i}')
            hr2fb_fading_names.append('hr2fb' + f'_{i}')
            fr2hb_fading_names.append('fr2hb' + f'_{i}')
            fb2hr_fading_names.append('fb2hr' + f'_{i}')

        lookup_list = stimuli_names + hb2fr_fading_names + hr2fb_fading_names + fr2hb_fading_names + fb2hr_fading_names
        
        return lookup_list

    



    
        
