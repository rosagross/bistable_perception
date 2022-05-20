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


class RSStimulus():
    """ 
    This class implements the organization of different stimulus types in lists in the experiment. 
    There are different trial types which need different stimuli:
    - unambiguous (left or right wards moving)
    - ambiguous (not clear which direction the dots are moving)
    - break stimulus (fixation dot)

    With creating a lookup table, the stimulus can be accessed via indice in the experiment session.
    This safes us if-statements in the refresh loop
    """

    def __init__(self, settings, win, *args, **kwargs):
        
        # setting for loading the correct stimulus
        self.settings = settings
        self.path_to_stim = self.settings['Stimulus settings']['Stimulus path']
        self.stim_size = self.stim_size = self.settings['Stimulus settings']['Stimulus size']
        self.break_stim_name = self.settings['Stimulus settings']['Break stimulus name']
        self.path_to_stim = self.settings['Stimulus settings']['Stimulus path']
        self.stimulus_resolution = self.settings['Stimulus settings']['Stimulus resolution']
        self.dot_size = self.settings['Stimulus settings']['Dot size']
        self.nr_of_frames = self.settings['Stimulus settings']['Number frames'] 
        self.nr_of_dots = self.settings['Stimulus settings']['Number dots'] 
        self.sphere_number_ambiguous = self.settings['Stimulus settings']['Sphere number ambiguous'] 
        self.sphere_number_unambiguous = self.settings['Stimulus settings']['Sphere number unambiguous'] 
        self.black_at_back = self.settings['Stimulus settings']['Black at back'] 
        self.white_at_back = self.settings['Stimulus settings']['White at back'] 
        self.black_at_front = self.settings['Stimulus settings']['Black at front'] 
        self.white_at_front = self.settings['Stimulus settings']['White at front'] 
        self.dot_size_min = self.settings['Stimulus settings']['Dot size min'] 
        self.dot_size_max = self.settings['Stimulus settings']['Dot size max'] 
        self.win = win
        self.unique_stimulus_list = self.load_stimuli()
        self.lookup_list = self.create_lookup_list()

        print('check if stimulus list and look-up list have the same length')
        print(len(self.unique_stimulus_list)==len(self.lookup_list))


    def load_stimuli(self):
        """ 
        Function loading the dot stimuli and fixation dot 
        """

        # here we load the images that were produced in the MATLAB code 
        self.fixation_dot = visual.ImageStim(self.win, image=self.path_to_stim+'FixDot.bmp',  units='deg', size=self.stim_size)

        # save the globe stimuli in different lists, since one rotation consists out of 190 images
        self.ambiguous_stim_list = []
        self.unambiguous_stim_list_right = []
        self.unambiguous_stim_list_left = []

        # we have a certain number of frames that make up one rotation of the sphere
        for i in range(self.nr_of_frames):
            filename_amb = f'Amb_{self.stimulus_resolution}x{self.stimulus_resolution}-{self.nr_of_frames}frames-{self.nr_of_dots}dots(size={self.dot_size})_{self.sphere_number_ambiguous}.{i+1}.bmp'
            filename_unamb_right = f'Contr_Unamb_{self.black_at_back}BB_{self.white_at_back}WB_{self.black_at_front}BF_{self.white_at_front}WF_{self.dot_size_min}-{self.dot_size_max}DS_{self.stimulus_resolution}x{self.stimulus_resolution}-{self.nr_of_frames}frames-{self.nr_of_dots}dots(size={self.dot_size})_{self.sphere_number_unambiguous}.{i+1}.bmp'
            filename_unamb_left = f'Contr_Unamb_{self.black_at_back}BB_{self.white_at_back}WB_{self.black_at_front}BF_{self.white_at_front}WF_{self.dot_size_min}-{self.dot_size_max}DS_{self.stimulus_resolution}x{self.stimulus_resolution}-{self.nr_of_frames}frames-{self.nr_of_dots}dots(size={self.dot_size})_{self.sphere_number_unambiguous}.{self.nr_of_frames-i}.bmp'
            
            self.ambiguous_stim_list.append(visual.ImageStim(self.win, image=self.path_to_stim+filename_amb, units='deg', size=self.stim_size))
            self.unambiguous_stim_list_right.append(visual.ImageStim(self.win, image=self.path_to_stim+filename_unamb_right, units='deg', size=self.stim_size))
            # create the left rotation list separately since it takes longer if we do the indices counting backwards later on!
            self.unambiguous_stim_list_left.append(visual.ImageStim(self.win, image=self.path_to_stim+filename_unamb_left, units='deg', size=self.stim_size))

        # load a stimulus that can test the eye tracking data 
        dots = [visual.Circle(self.win, lineColor='red', units='pix', size=70, pos=[-250,-250]),
                visual.Circle(self.win, lineColor='red', units='pix', size=70, pos=[250,-250]),
                visual.Circle(self.win, lineColor='red', units='pix', size=70, pos=[250,250]),
                visual.Circle(self.win, lineColor='red', units='pix', size=70, pos=[-250,250])]

        self.eye_tracking_test = dots
        
        unique_stimulus_list = self.ambiguous_stim_list + self.unambiguous_stim_list_left + self.unambiguous_stim_list_right + [self.fixation_dot] + self.eye_tracking_test
        return unique_stimulus_list


    def create_lookup_list(self):
        """ 
        Creating a look-up list that matches exactly the stimulus list created 
        """
        # ambiguous stim list: 0-nr_of_frames
        # unambiguosu left: nr_of_frames-nr_of_frames*2
        # unambiguous right: nr_of_frames*2-nr_of_frames*3
        # fixation dot: last element
        ambiguous_names = []
        unambiguous_left_names = []
        unambiguous_right_names = []

        for i in range(self.nr_of_frames):
            ambiguous_names.append('ambiguous' + f'_{i}')
            unambiguous_left_names.append('unambiguous_left' + f'_{i}')
            unambiguous_right_names.append('unambiguous_right' + f'_{i}')

        self.eyetracking_test_names = []
        for i in range(len(self.eye_tracking_test)):
            self.eyetracking_test_names.append(f'tracking_test_{i}')

        lookup_list = ambiguous_names + unambiguous_left_names + unambiguous_right_names + [self.break_stim_name] + self.eyetracking_test_names
        return lookup_list

    



    
        
