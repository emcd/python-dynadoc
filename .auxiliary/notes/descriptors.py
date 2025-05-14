import functools as funct
import inspect

class Descriptors:

    @classmethod
    def classy( cls ):
        ''' Class method. '''

    @staticmethod
    def static( ):
        ''' Static method. '''

    @property
    def getter( self ):
        ''' Property reader. '''

    @funct.cached_property
    def cache_getter( self ):
        ''' Caching property reader. '''


members = inspect.getmembers( Descriptors )
for name, member in members:
    if name.startswith( '_' ): continue
    print( )
    print( name, member, type( member ), member.__doc__ )
    print( dir( member ) )
    print( 'function?', inspect.isfunction( member ) )
    print( 'method?', inspect.ismethod( member ) )
    print( 'data descriptor?', inspect.isdatadescriptor( member ) )


for func in (
    Descriptors.classy.__func__,
    Descriptors.getter.fget,
    Descriptors.cache_getter.func,
):
    print( )
    print( func, type( func ), func.__doc__ )


# Descriptors.classy.__doc__ = Descriptors.classy.__doc__ + " (modified)"
Descriptors.classy.__func__.__doc__ = (
    Descriptors.classy.__doc__ + " (modified)" )
Descriptors.getter.__doc__ = Descriptors.getter.__doc__ + " (modified)"
Descriptors.cache_getter.__doc__ = (
    Descriptors.cache_getter.__doc__ + " (modified)" )

print( Descriptors.classy.__doc__ )
print( Descriptors.getter.__doc__ )
print( Descriptors.cache_getter.__doc__ )
