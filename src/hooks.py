from typing import Callable, Coroutine


class Hook:
    def __init__(self):
        self.functions = []
        self.coroutines = []

    def register(self, function: Callable) -> None:
        if isinstance(function, Coroutine):
            self.coroutines.append(function)
        else:
            self.functions.append(function)

    def fire(self, *args, **kwargs) -> None:
        for function in self.functions:
            function(*args, **kwargs)
    async def fire_async(self, *args, **kwargs) -> None:
        for coroutine in self.coroutines:
            coroutine(*args, **kwargs)


map_request = Hook()
button_pressed = Hook()
window_clicked = Hook()
main_initializing = Hook()
window_initialized = Hook()
