from functools import wraps

def wrapper(func):
    @wraps(func)

    def decorator(*args, **kwargs):
        print("YOlo wrapper")
        return func(*args, **kwargs)

    return decorator

@wrapper
def hello(name):
    print("Ciao {}!".format(name))



hello("yoloshallo")