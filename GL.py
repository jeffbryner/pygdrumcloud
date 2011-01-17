from OpenGL.GL import *
from OpenGL.GLU import *

def resize((width, height)):
    if height==0:
        height=1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0*width/height, 1.0, 10000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
def init():
    glEnable(GL_BLEND)                                          #masking functions
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    
    glShadeModel(GL_SMOOTH)
##    glClearColor(0.27, 0.45, 0.9, 0.0)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable( GL_ALPHA_TEST )
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    glAlphaFunc( GL_NOTEQUAL, 0.0 )

    glFogfv(GL_FOG_DENSITY, .01)
    glFogfv(GL_FOG_COLOR, (1,1,1,0.5))
    glEnable(GL_FOG)

    LightAmbient  = [ 0.5, 0.5, 0.5, 1.0]
    LightDiffuse  = [ 1.0, 1.0, 1.0, 1.0]
    LightIntensity  = [ 10.0, 10.0, 10.0, 10.0]
    LightPosition = [ 0, 100.0, 0, 1.0]

    glLightfv( GL_LIGHT0, GL_AMBIENT, LightAmbient )
    glLightfv( GL_LIGHT0, GL_DIFFUSE, LightDiffuse )
    glLightfv( GL_LIGHT0, GL_POSITION, LightPosition )
    glLightfv( GL_LIGHT0, GL_SPECULAR, LightIntensity )
    glEnable( GL_LIGHT0 )
