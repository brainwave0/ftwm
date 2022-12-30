from src import dbus, increment, click_to_focus


def init() -> None:
    for hook_module in [click_to_focus, dbus]:
        hook_module.register()
