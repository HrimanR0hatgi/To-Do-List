# \# My Productivity

# 

# A Windows desktop productivity application built with Python and CustomTkinter.

# 

# My Productivity combines task management, habit tracking, scheduled reminders, and an accountability system that integrates with a Brave browser extension.

# 

# \## Features

# 

# \- Create, edit, and complete tasks with priorities and planned dates.

# \- Set deadlines and add task comments.

# \- Track daily completion targets and progress.

# \- Track habits and completion streaks.

# \- Receive desktop notifications and use the system tray.

# \- Automatically check qualifying unfinished tasks on a schedule.

# \- Block configured entertainment websites in Brave while the accountability lock is active.

# 

# \## Technology Stack

# 

# \- Python

# \- CustomTkinter

# \- Pystray

# \- Pillow

# \- Winotify

# \- JavaScript

# \- Brave Extension Manifest V3

# \- Local HTTP bridge

# 

# \## Installation

# 

# Install Python on Windows, then install the dependencies:

# 

# &#x20;   python -m pip install -r requirements.txt

# 

# Run the desktop application:

# 

# &#x20;   python main.py

# 

# \## Brave Extension Setup

# 

# 1\. Open brave://extensions.

# 2\. Enable Developer mode.

# 3\. Select Load unpacked.

# 4\. Choose the Blocker folder.

# 5\. Keep My Productivity running while using the extension.

# 

# The extension communicates with the desktop application through a local HTTP bridge.

# 

# \## Accountability Schedule

# 

# The intended schedule is a task warning at 10:30 PM and an accountability checkpoint at 11:00 PM.

# 

# Qualifying tasks are unfinished tasks planned for the current date or tasks with deadlines on or before the current date. Completing all tasks covered by an active lock releases the browser block.

# 

# Missed-checkpoint recovery is implemented, but the complete workflow across sleep, shutdown, and scheduled wake-up scenarios still requires validation.

# 

# \## Limitations

# 

# \- Windows desktop application.

# \- Website blocking applies to configured sites in Brave, not all browsers.

# \- Data is stored locally; cloud synchronization is not implemented.

# \- Scheduled execution across sleep and shutdown depends on application recovery and Windows power settings.

