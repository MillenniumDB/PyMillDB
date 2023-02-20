from functools import wraps


def check_closed(func):
    # Raises an exception if the class was closed before calling its method

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._closed:
            raise Exception(f"{self.__class__.__name__} instance is closed")
        return func(self, *args, **kwargs)

    return wrapper
