# CLICK TO FOCUS

Clicking a window gives it keyboard focus. Aside from global shortcut keys, all keystrokes will be sent to the focused window.

# DBUS INTERFACE

Some actions can be initiated using a DBus interface which is exposed at `/com/github/brainwave0/ftwm/interface`.

## Increment

The `Increment` action is for increasing or decreasing the size of the focused window. An error message,`com.github.brainwave0.ftwm.error.InvalidInput`, is returned in response to invalid input.

### parameters

- `dimension`: `width` or `height`
- `direction`: `-1` to decrease, `1` to increase

## Arrange

Re-arranges the windows according to the rules of the layout. Windows are placed in order from largest to smallest.

# LAYOUT

New windows are placed as close to the center of the screen as possible without overlapping. Also, the screen aspect ratio is taken into account; depending on the screen, the windows may be arranged more vertically or horizontally.

# FACE TRACKING

Panning of the screen is based on the location of the face in the video feed. If there are multiple faces, the one nearest to the screen is tracked. It is assumed that the nearest face is the largest one in the camera frame.

# EVENTS

A subset of X events are currently handled.

## Map Request

When a new window is created, it is placed on the screen according to the layout.

## Destroy Notify

The window is simply removed from the list.

## Button Press

Handles click-to-focus.

# COMMAND LINE INTERFACE

The application can be controlled from the command line. It is just a shell script that uses the DBus interface.

# CONFIGURATION

The application can be configured using the `settings.ini` file, by default located in `~/.config/ftwm/`. Details on specific options can be found in the file.