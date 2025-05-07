
def doc(docstring):
    def decorator(func):
        func.__doc__ = docstring
        return func
    return decorator
