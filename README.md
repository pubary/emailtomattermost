# Bank-notification bot

-----

### Python Bot for Mattermost

Checking emails during the day and sending into Mattermost
channel messages with information from banks' email
notifications about receipts on the account. Calculation
of the amount of money received on the bank account during
the day.

The project was created using the framework [*mmpy-bot*][1]

### Installation

#### What do you need:

* a computer (with Windows, macOS or Linux)
* Python installed on your machine (with pip)


#### Step 1: Install Python (>=3.8):

If you're on Linux or macOS you should have Python and Git installed, just check that your Python version is >= 3.8.

On Windows you have to install it for sure.

Check that pip3 is installed by typing `pip3 -V` If that returns an error you have to [install it][2]!<br>
If you are on Linux and your user cannot have root permissions, you can install pip in the local user environment:
+ Download pip from an online repository: `~$ wget https://bootstrap.pypa.io/get-pip.py`
+ Install the downloaded package into a local directory (.local/bin): `~$ python get-pip.py --user`



#### Step 2: Install Bank-notification bot:

Is good practice creating virtual environments when you install a new package.
That will save you from a lot of problems!

##### Create a virtual environment

We create a virtual environment called *em-venv* and activate it:

* create a directory where you will create the virtual environment `mkdir emailtomattermost`
* write in console: `python3 -m venv em-venv`<br>
  > If your Linux user cannot have root permissions and you have installed *pip* in the local user environment,
you need to install virtualenv also for your user:
    + go to directory *~/.local/bin*
    + install the virtualenv: `~/.local/bin$ ./pip install virtualenv`
    + go to directory *emailtomattermost*
    + creating a virtual environment named *em-venv*: `$ virtualenv em-venv`
* being in the directory where the virtual environment is created, activate the *em-venv*:
  + `$ source em-venv/bin/activate` on Linux/macOS
  + `em-venv\scripts\activate.bat` on Windows cmd
  + `em-venv\scripts\activate.ps1` on Windows PowerShell
     > If you activate the venv correctly, you will see a little *(em-venv)* on the left side of the command line!

##### Clone Bank-notification bot from GIT:

+ being in the directory *emailtomattermost* where the virtual environment is created, clone the project:<br>
`git clone http://git......emailtomattermost.git`
+ install the requirements: `pip3 install -r requirements.txt`
+ copy *example.env* file as *.env*: `cp example.env .env`<br>
   You need to add your settings in *.env* file after creating the bot in your Mattermost channel.


#### Step 3: Creating and connection Mattermost bot

Write the URL of your Mattermost server in the *.env* file

##### To create a new bot:

+ In Mattermost go to: *Integrations → Bot Accounts → Add Bot Account*
+ On the bot creation page, specify the bot's name, display name, description, and add an avatar.<br>
In the Role field, select the Participant option and click Create Bot Account.
Select the *post:channels* checkbox and click Create Bot Account
+ On the page that opens, copy the bot token and paste it into the *.env* file.

##### To connect bot to the channel:

+ Add a bot to your team. Write the name of your team in the *.env* file.
+ Create a channel for your team where the bot will send notifications.
Copy the channel ID and paste it into the *.env* file
+ Add a bot to the created channel.


#### Step 4: Start the bot

Make sure that you have made all the settings in the *.env* file:

+ settings of the email to which you receive notifications from the banks
+ Mattermost server URL
+ your Mattermost team-name
+ Mattermost channel ID
+ bot token

The file *config.py* contains a list of e-mail addresses from which banks will receive notifications.
It also contains templates for searching for information and for sending messages.<br>
You can also make changes to the *config.py* file to make changes to the bot. 
But to send messages to the Mattermost channel you need entry `MY_DEBUG = False` in this file.

Now everything is ready, and you can finally run the bot in the *bot* directory: `python3 emailtomattermost.py`
  > If you close the terminal in which you ran the bot, it will stop working. To prevent this, 
    use for example on Linux *nohup* from directory with *emailtomattermost.py*:<br>
  > `$ nohup python3 emailtomattermost.py &`

After starting the bot, if you make any changes to the program files, you must restart it:
+ To do this, you must first stop the bot that is already running. If the bot was started with "nohup",
just type the command `kill <pid>` (*pid* is the process ID of *emailtomattermost.py*).
  > To find the pid, run `ps -ef | grep emailtomattermost.py`.
+ go to the *emailtomattermost* directory with the *emailtomattermost.py* file and activate the virtual environment,
  if it was previously deactivated for some reason.
+ being in the directory with the *emailtomattermost.py* file restart the bot:<br>
`$ nohup python3 emailtomattermost.py &` (if using *nohup*)


[1]: (https://pypi.org/project/mmpy-bot/)
[2]: (https://pip.pypa.io/en/stable/installation/)
