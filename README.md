# bistable_perception
This is an bistable experiment which can be executed in two different settings: **binocular rivarly** or **rotating sphere**. using the rotating sphere illusion to study consciousness and perception of ambiguous stimuli. An eyetracking device (EyeLink) may be connected. 


**Requirements**

- python 3.6 (3.8 works as well)
- psychopy 2022.1.1
- exptools2 (installation instructions can be found on [this repository](https://github.com/VU-Cog-Sci/exptools2))
- pylink (included in psychopy standalone, but can be retreived on the [sr-research webpage](https://www.sr-support.com/thread-48.html) as well)

**Usage**

To execute the experiment run: ```python main.py sub-xxx ses-x task-BR\RS False\True``` <br>
The task can be either a binocular rivalry or a rotating sphere experiment. The boolean operator in the end indicates if we want to run it in connection with the eyetracking device.
<br>
Before the real experiment starts, the participant has the possibility to practice. Press 'y' to start a preactice session. It will always start with an ambiguous block. After that there will still be the option to do further test trials.
<br>
Please check the ```settings.yml``` file for experiment settings that can be changed. Change the button names in the file to the ones your subject is going to use! If you want to test if the eyetracker captures the gaze correctly, set ```Test eyetracker``` to ```True```. It is important to insert the correct refreshrate of the monitor, because it is used to calculate the rotation speed.
<br>
In the beginning, a practice block can be started by pressing 'y' when it shows 'Practice block, please wait'. Press 'n' to start real experiment. After the pracice block press 'y' to go to the starting point of the real experiment and 'n' to keep on testing. Then finally press 't' to start  the real experiment. The 't' will be visible in the output file as the experiment onset.

<br>

## Code Structure
- ```main.py``` creates the session object.
- ```session.py``` creates the trials and blocks of the exeriment. Creates the stimuli, executes the trials end draws the stimuli.
- ``
- ```trial.py``` implements the trial object, which outlines how a trial should look like. Logs button presses and parameters for the trials. 
- ```settings.yml``` contains the experiment and task settings
- input file formats are task specific!
    - For rotating sphere experiment: 
        - For ambiguous stimuli:  ```Amb_<stimulus resolution>x<stimulus resolution>-<nr. of frames total>frames-<nr. of dots>dots(size=<dot size>)_<sphere number>.<nr. of current frame>.bmp```. Example: ```Amb_800x800-190frames-350dots(size=0.02)_1.1.bmp``` for the first frame of the ambiguous sphere. By changing the sphere number you can create multiple spheres with the same parameters without overwriting the existing bmps.
        - For unambiguous (control) stimuli: ```Contr_Unamb_<black at back>BB_<white at back>WB_<black at front>BF_<white at front>WF_<dot size min>-<dot size max>DS_<stimulus resolution>x<stimulus resolution>-<nr. of frames total>frames-<nr. of dots>dots(size=<dot size>)_5.45.bmp```. Example: ```Contr_Unamb_0.25BB_0.75WB_0BF_1WF_0.012-0.028DS_800x800-190frames-350dots(size=0.02)_<sphere number>.45.bmp``` for 45th frame of the disambiguoated control sphere. 
    - For binocular rivalry experiment:
        - For ambiguous stimuli: 'rivalry_redface.bmp' and 'rivalry_redhouse.bmp'
        - For unambiguous stimuli: 'house_red.bmp', 'house_blue.bmp', 'face_red.bmp' and 'face_blue.bmp'
        - Fixation screen: 'fixation_screen.bmp'

### Term clarification
- monitor refreshrate: The rate in which the monitor is able to refresh the image (in Hz). This is determined by the computer hardware. Mostly this can be changed in display settings on the computer, so make sure that you know what the monitor refresh rate is and enter it in the settings file.
- screen tick: The shortest refresh period possible. This depends on the monitor refresh rate. If the refresh rate is 60Hz, there are 60 screen ticks per second.
- frame rate: The rate in which the monitor changes the image on the display (in this experiment this would be the rate in which the monitor updates the image that shows the dots on a different position). This is defined by the experimenter within the code. For example the frame rate could be 4, which would mean that the frame lasts 4 screen ticks.


## Conditions and tiral procedure

Two main conditions:
1) Ambiguous (e.g. binocular rivalry, or ambiguous rotating globe)
2) Unambiguous

**Note**
- Subjects with even IDs start with the ambiguous, odd with the unambiguous condition
- Trial counting starts with 1
- The breaks have trialID and blockID of '0'
- The participant uses the preferred hand to respond. Which finger is used for which button is indicated in the instructions. Carefully check the instructions in the beginning.
<br>

