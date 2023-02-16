# FTWM

An experimental window manager with which you can pan a virtual desktop by moving your head.

<img src="screencast.gif" title="" alt="screencast.gif" data-align="center">

## Status

It's somewhat usable. Some critical features are missing, like being able to close windows, or fullscreen handling. See below for limitations and known issues.

## Features

- You can pan the windows using your face!

- It has DBus interface which can be controlled using the included `ftwmcmd` script, which can be used in keyboard shortcuts using something like xbindkeys.

- Click to focus

- Optimal window arrangement

- Configuration via a `.ini` file

- Automatically selects the first camera that can see your face

- Windows completely stop moving when your head is still

## Limitations and Known Issues

The following issues include bugs and missing features that I plan to fix.

### framerates

Depending on your webcam, you may experience low framerates in low light. This is because exposure duration is increased to compensate. In other words, it takes longer to capture each frame.

### fullscreen applications

Fullscreen applications may not take up the whole screen, nor will they be static.

### existing window management

Windows opened before the application has finished loading are unmanaged. As a workaround, I put a delay in my `.xinitrc` before any startup GUI applications load.

### window placement

New windows may be difficult to find. Currently all new windows are placed wherever there is room, and you have to look around to find them. Also, there is a bug where empty space is counted as occupied, causing windows to be placed in sub-optimal locations.

### cpu usage

It uses up to about 12% of the CPU on my machine, or about 97% of a single core.

### window resizing

Changing the window sizes is supposed to be smarter than it is now. Currently I can resize them by 20% at a time using the keyboard, but this is supposed to vary so you can get closer to the exact size you want.

## Configuration

The `settings.ini` file, located by default in `~/.config/ftwm`, includes options to tune the smoothness of window movements, customize how far you can move them, and specify the threshold at which stillness is detected. There are also some camera settings. Details are in the included `settings.ini` file.

## Roadmap

1. Window-closing functionality

2. Fullscreen handling

3. Monocle layout

4. Compensate for low camera framerates

5. Handle floating windows

6. Fix window placement

7. Manage existing windows on startup

8. Point to new windows

9. Focus new windows

10. Reduce CPU usage

11. Improve window-resizing
