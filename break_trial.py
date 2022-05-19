#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@time    :   2022/02/09 17:33:27
@author  :   rosagross
@contact :   grossmann.rc@gmail.com
'''

from psychopy import event
import numpy as np
from exptools2.core.trial import Trial
from psychopy.hardware import keyboard
import os
import re
opj = os.path.join


class BreakTrial(Trial):
    """ 
    This class implements the construction of the trials in the experiment. 
    There are different trial types:
    - unambiguous (left or right wards moving)
    - ambiguous (not clear which direction), in this trial, nothing changes over the whole duration of the trial

    Every trial begins with a 10s break.
    """

    def __init__(self, session, trial_nr, block_ID, block_type, trial_type, phase_duration, timing*args, **kwargs):
        
        super().__init__(session, trial_nr, phase_duration,
                         parameters={'block_type': block_type,
                                     'trial_type': trial_type,
                                     'trial_nr': trial_nr, 
                                     'block_ID' : block_ID,
                                     'phase_length' : len(phase_duration)}, 
                         timing=timing,
                         verbose=False, *args, **kwargs)
        
        # store if it is a ambiguous trial or unambiguous trial 
        self.ID = trial_nr
        self.block_ID = block_ID
        self.block_type = block_type
        self.trial_type = trial_type
        
            
    def draw(self):
        ''' This tells what happens in the trial, and this is defined in the session itself. '''
        self.fixation_dot.draw()


    def get_events(self):
        """ Logs responses/triggers """

        keys = self.session.kb.getKeys(waitRelease=True)
        for thisKey in keys:

            if thisKey==self.session.exit_key:  # it is equivalent to the string 'q'
                print("End experiment!")

                if self.session.settings['Task settings']['Screenshot']==True:
                    print('\nSCREENSHOT\n')
                    self.session.win.saveMovieFrames(opj(self.session.screen_dir, self.session.output_str+'_Screenshot.png'))
                self.session.close()
                self.session.quit()

            elif (thisKey=='s') & (self.session.settings['Task settings']['Screenshot']==True):
                self.session.win.getMovieFrame()
                self.session.win.saveMovieFrames(opj(self.session.screen_dir, self.session.output_str+f'_Screenshot_{self.trial_type}.png'))
            else: 
                # the button press onset in the global experiment time
                t = thisKey.rt
                # to check if the responses have valid timing and correct button was used (only used for unambiguous trials)
                onset_delay_timing = np.NaN
                offset_delay_timing = np.NaN
                onset_delay = np.NaN
                offset_delay = np.NaN

                event_type = self.trial_type
                idx = self.session.global_log.shape[0]     
    
                self.session.global_log.loc[idx, 'event_type'] = event_type
                self.session.global_log.loc[idx, 'trial_nr'] = self.trial_nr   
                self.session.global_log.loc[idx, 'onset'] = t
                self.session.global_log.loc[idx, 'reaction_time'] = onset_delay
                self.session.global_log.loc[idx, 'key_duration'] = thisKey.duration
                self.session.global_log.loc[idx, 'phase'] = self.phase
                self.session.global_log.loc[idx, 'response'] = thisKey.name
                self.session.global_log.loc[idx, 'nr_frames'] = 0

                for param, val in self.parameters.items():
                    self.session.global_log.loc[idx, param] = val

                if self.eyetracker_on:  # send message to eyetracker
                    msg = f'start_type-{event_type}_trial-{self.trial_nr}_phase-{self.phase}_key-{thisKey.name}_time-{t}_duration-{thisKey.duration}'
                    self.session.tracker.sendMessage(msg)

        
                    


 

    



    
        
