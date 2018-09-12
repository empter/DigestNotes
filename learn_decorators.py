#Decorators are callable objects which are used to modify functions or classes.

def decorator(function):
    # define another wrapper function which modifies function
    def wrapper(*args, **kwargs):
        # funny_stuff(), e.g.
        print('wrapper the function here.')
        print('Some args:', args[0])
        # call original function if needed
        function(*args, **kwargs)
        # some more funny_stuff(), e.g.
        print('some more wrapper.')
    return wrapper

@decorator
def myfun(arg):
    print('It is myfun')
# @decorator is the same as myfun = decorator(myfun)

myfun(100)
print('myfun.__name__ is:', myfun.__name__)


# Parameterized decorators: the decorator with arguments should return a function\
# that will take a function and return another function.
def pseudo_decor(argument):
    def real_decorator(function):
        def wrapper(*args, **kwargs):
            # funny_stuff()
            print('wrapper the function here.')
            # something_with_argument(argument)
            print(argument)
            # call original function
            function(*args, **kwargs)
            # some more_funny_stuff()
            print('some more wrapper.')
        return wrapper
    return real_decorator

@pseudo_decor(True)
def myfun2(arg):
    print('It is myfun')

myfun2('the args')
