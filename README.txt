README

Manual Requirements:
1. Must put in credentials manualls into credential file
2. Must have lambda functions already written and placed in /home/<user>/lambda
3. Must edit python file to have correct prefix
4. Must edit 2nd lambda function to have correct prefix

Potential problems:
1. If an error occurs during any lambda function, the entire process stops
2. Did not know what the VOL paramater was for the results so it was left it out
3. Path to lambda functions/zipfiles are hardcoded atm (only works for 'bao', which is me)

Notes:
- For the purposes of this lab, the function sleeps for 10 seconds after every SNS
- I have made and used 2 trimmed down versions of the raw data so we don't sit here for a long time
- Must run python script with ipython

Zoom video:
https://drive.google.com/file/d/1WoRTTzR6myTQ1HoSxdpVQH2vYGMKw-Bo/view?usp=sharing

	Zoom did not let me upload to their cloud.
	I upploaded to google drive instead.