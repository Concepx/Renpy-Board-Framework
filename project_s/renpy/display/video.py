# Copyright 2004-2012 Tom Rothamel <pytom@bishoujo.us>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import renpy.display
import renpy.audio

# True if the movie that is currently displaying is in fullscreen mode,
# False if it's a smaller size.
fullscreen = False

# The size of a Movie object that hasn't had an explicit size set.
default_size = (400, 300)

# The file we allocated the surface for.
surface_file = None

# The surface to display the movie on, if not fullscreen.
surface = None

def movie_stop(clear=True, only_fullscreen=False):
    """
    Stops the currently playing movie.
    """

    if (not fullscreen) and only_fullscreen:
        return

    renpy.audio.music.stop(channel='movie')

    
def movie_start(filename, size=None, loops=0):
    """
    This starts a movie playing. 
    """
    
    if renpy.game.less_updates:
        return

    global default_size
    
    if size is not None:
        default_size = size
    
    filename = [ filename ]

    if loops == -1:
        loop = True
    else:
        loop = False
        filename = filename * (loops + 1)

    renpy.audio.music.play(filename, channel='movie', loop=loop)

movie_start_fullscreen = movie_start
movie_start_displayable = movie_start

def early_interact():
    """
    Called early in the interact process, to clear out the fullscreen
    flag.
    """

    global fullscreen
    fullscreen = True

def interact():
    """
    This is called each time the screen is redrawn. It helps us decide if
    the movie should be displayed fullscreen or not.
    """

    global surface
    global surface_file
    
    if not renpy.audio.music.get_playing("movie"):
        surface = None
        surface_file = None
        return False
        
    if fullscreen: 
        return True
    else:
        return False

def get_movie_texture(size):
    """
    Gets a movie texture we can draw to the screen.
    """
    
    global surface
    global surface_file

    playing = renpy.audio.music.get_playing("movie")

    if (surface is None) or (surface.get_size() != size) or (surface_file != playing):
        surface = renpy.display.pgrender.surface(size, True)
        surface_file = playing
        surface.fill((0, 0, 0, 255))

    tex = None

    if playing is not None:
        renpy.display.render.mutated_surface(surface)
        tex = renpy.display.draw.load_texture(surface)

    return tex


class Movie(renpy.display.core.Displayable):
    """
    This is a displayable that shows the current movie.
    """

    fullscreen = False
    
    def __init__(self, fps=24, size=None, **properties):
        """
        @param fps: The framerate that the movie should be shown at.
        """
        super(Movie, self).__init__(**properties)
        self.size = size
        
    def render(self, width, height, st, at):
        
        size = self.size
        
        if size is None:
            size = default_size

        width, height = size
        rv = renpy.display.render.Render(width, height, opaque=True)
        
        tex = get_movie_texture(size)
        
        if tex is not None:
            rv.blit(tex, (0, 0))
            
        return rv
            
    def event(self, ev, x, y, st):

        if ev.type == renpy.audio.audio.REFRESH_EVENT:
            renpy.display.render.redraw(self, 0)

    def per_interact(self):
        global fullscreen
        fullscreen = False
        
            
