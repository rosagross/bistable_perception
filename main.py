#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@time    :   2022/02/10 13:31:04
@author  :   rosagross
@contact :   grossmann.rc@gmail.com
'''


import sys
import os
import re
from datetime import datetime
from bistable_perception_session import BistablePerceptionSession
from figure_ground_session import FigureGroundSession
datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def main():
    subject = sys.argv[1]
    sess = sys.argv[2] # so for example if something went wrong and we wanna to the experiment again, increase session number when starting
    task = sys.argv[3]
    task = task[5:]
    print('Experiment:', task)
    subject_ID = int(re.findall(r'(?<=-)\d+', subject)[0])
    output_str = subject + '_' + sess
    output_dir = './output_data/'+output_str+f'_Logs_{task}'
    settings_file = './settings_' +task+'.yml'
    eyetracker_on = True if sys.argv[4] == "True" else False

    if not os.path.exists('./output_data'):
        os.mkdir('./output_data')

    if os.path.exists(output_dir):
        print("Warning: output directory already exists. Renaming to avoid overwriting.")
        output_dir = output_dir + datetime.now().strftime('%Y%m%d%H%M%S')
    
    # instantiate and run the session 
    if task == 'FG':
        experiment_session = FigureGroundSession(output_str, output_dir, settings_file, subject_ID, eyetracker_on)
    else:
        experiment_session = BistablePerceptionSession(output_str, output_dir, settings_file, subject_ID, eyetracker_on, task)
    experiment_session.run()


if __name__ == '__main__':
    main()
