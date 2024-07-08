# Panmuphle
A meta-manager for `bspwm`.


```
              Controller
              /         \
      Workspace 1      Workspace 2
      /       \         /      \
  Window 1  Window 2 Window 3 Window 4

```

Thus it should look something like:
```python

controller = {
    'screens': [
        {
            'name': 'HDMI-0'
        },
        {
            'name': 'DP-0'
        }
    ],
    'workspaces': [
        {
            'name': 'workspace1',
            'windows': [
                {
                    'name': 'window1',
                },
                {
                    'name': 'window2'
                }
            ]
        }, {
            'name': 'workspace2',
            'windows': [
                {
                    'name': 'window3'
                },
                {
                    'name': 'window4'
                }
            ]
        }
    ]
}
```

Therefor each screen should keep track of which window it is displaying at any given time.

**Activating Workspaces**
When a switch of a workspace occurs, the workspace should go through each screen. For each screen, it should see if it has a window that it needs to displayed there.

If it does, it should switch that window with whatever window was there previously.

If there was no window there previously, it should empty that screen.

Therefore, the workspace switch needs to take as input the current state of what is being displayed on all available screens.

**Activating Windows**
When switching a window, the window should be provided a target screen. It should swap itself with whatever window is currently at that location.

## Functions

## Bugs

- When I open a workspace sometimes it's a new workspace, sometimes it reuses an existing workspace
- When I open an application there's multiple slide-ins
- Doesn't seem to be terminating applications properly on workspace close