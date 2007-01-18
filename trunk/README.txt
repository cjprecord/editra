Project Name: Editra
Current Project Info:
Author: Cody Precord
Email: codyprecord@gmail.com

#----------------------------------------------------------------------------#

Info:
This project was begun as a way to learn more about python and gui design and 
a clear path for its developement is still under consideration. However 
maintaining its crossplatform portability and ease of use will remain a top 
priority.

Currently the editor is able to handle many different programming languages
with custom styling for code highlighting. Most interface commands have key
accelerators to make for efficient usage of the features. Profile support
is also available to save your preferences so you dont need to manually set 
it up the way you like it each time.

#----------------------------------------------------------------------------#

Features:
Syntax Highlighting for a wide range of languages
Tabbed editting windows
Custom user profile support
Bracket/paren highlighting
Indentation Guides
Undo/Redo
Find/Find-Replace
Code Completion
Profiling to save your preferences

#----------------------------------------------------------------------------#

Compatibility:
It has been tested on the following systems, but it should run on any system
that supports python and wxpython.

Linux (tested on Gentoo and Suse)
Macintosh OS X
Windows XP

Dependancies:
If you wish to run the source code you will need to have the following
libraries installed.

Required for all systems:
Python 2.4 ( http://python.org )
wxPython 2.6 ( http://wxpython.org )

Required for Linux Only:

Required for OS X Only:

Required for Windows Only:

#----------------------------------------------------------------------------#

INSTALLATION:

Windows:
For windows there is a self extracting installer available, just double click 
on it and it will bring up the familiar windows installer interface just
follow the on screen instructions.

Linux:
Currently no installer package has been put together. Still working out
details of installation directories

Macintosh:
Mount the disk image and drag the applet to your applications folder

#----------------------------------------------------------------------------#

USAGE:

A: Starting the Program

   1) Running Source Scripts:

   Linux / OS X:
   someone@somewere ~> python pypad.py

   Windows:
   C:\Pypads_script_directory\> python pypad.py

   OR

   Double click on the script and it will execute if the default python file handler 
   is the python interpreter

   2) Running Windows binary

   Double click on the binary

   3) Running the OS X applet

   Double click on the applet in the Applications folder

B: Basic Operation

   Shown are all the possible ways of accomplishing the following tasks
   use the method you like best.

   1) Opening Files

      a. Click on the Open Icon in the toolbar
      b. File=>Open 
      c. Drop a file from your file manager on the text control
      d. From command line ( pypad yourFileName )
      e. CTRL + O  (capital o not zero)

   2) Start New Document

      a. Click on the New Icon in the toolbar
      b. File=>New
      c. CTRL + N
      d. From command line ( pypad aNewFileName )

   3) Save a file

      a. Click on the Save Icon in the toolbar
      b. File=>Save
      c. File=>Save As
      d. CTRL + S

   4) Undo

      a. Click on the Undo Icon in the toolbar
      b. CTRL + Z

   5) Redo

      a. Click on the Redo Icon in the toolbar
      b. CTRL + SHIFT + Z

C: Configurations and Settings

   1) Formating

      a. Word Wrap (On / Off)
      b. Font (All available system fonts. Currently Broken)

   2) Settings

      a. Syntax Highlighting (On / Off)
      b. Indentation Guides  (On / Off)
      c. Code Completion     (On / Off) (not very functional yet)

D: Profiles

   1) File Locations

      a. Default Profile
          - Windows: In the Pypad Installation directory
          - Others: profiles directory in src package

      b. User Profile(s)
          - All: In the users home directory (~/.pypad/profiles)

E: Advanced Usage


#----------------------------------------------------------------------------#

