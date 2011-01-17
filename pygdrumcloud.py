#!/usr/bin/python
# originally pygame '3D Sphere Collisions - Ian Mallett - 2008'
# and bits of kinect python examples
# Now...way different
# jeff bryner 01/2011

from OpenGL.GL import *
from OpenGL.GLU import *
import os, sys, math, random
import pygame
from pygame.locals import *
if sys.platform == 'win32' or sys.platform == 'win64':
    #loser..get linux
    os.environ['SDL_VIDEO_CENTERED'] = '1'
import GL,  ModuleGetInput
import freenect 
import numpy as np
import time
from threading import Thread
import thread
import wave
import alsaaudio
clock = pygame.time.Clock()


try: 
    TEXTURE_TARGET = GL_TEXTURE_RECTANGLE
except:
    TEXTURE_TARGET = GL_TEXTURE_RECTANGLE_ARB
  

pygame.init()

Screen = (640,480)
pygame.display.set_caption('pygame kinect drummachine pointcloud')
pygame.display.set_mode(Screen,OPENGL|DOUBLEBUF|RESIZABLE)
GL.resize(Screen)
GL.init()
rgbtex = glGenTextures(1)
glBindTexture(TEXTURE_TARGET, rgbtex)
glTexImage2D(TEXTURE_TARGET,0,GL_RGB,640,480,0,GL_RGB,GL_UNSIGNED_BYTE,None) 

#default states
CameraPos = [0.3,-.40,.80]
CameraRotate = [-15,-15]
ViewMode = 'Fill'
CloudThreshold=1.5     #how much background to show
CloudSample=13        #downsample size, resolution of the clould, higher=less resolution
CloudPointSize=2.5     #point size of points in the cloud 
KeyPress = [False]
Blocks = []


def play(filename):    
    #sys.stdout.write('%d channels, %d sampling rate\n' % (f.getnchannels(),f.getframerate()))
    f = wave.open(filename, 'rb')
    device = alsaaudio.PCM(card='default', mode=alsaaudio.PCM_NONBLOCK)
    
    # Set attributes
    device.setchannels(f.getnchannels())
    device.setrate(f.getframerate())

    # 8bit is unsigned in wav files
    samplewidth=f.getsampwidth()
    if samplewidth == 1:
        device.setformat(alsaaudio.PCM_FORMAT_U8)
    # Otherwise we assume signed data, little endian
    elif samplewidth == 2:
        device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    elif samplewidth == 3:
        device.setformat(alsaaudio.PCM_FORMAT_S24_LE)
    elif samplewidth == 4:
        device.setformat(alsaaudio.PCM_FORMAT_S32_LE)
    else:
        raise ValueError('Unsupported format')
    #device.setperiodsize(320)
    #data = f.readframes(320)
    device.setperiodsize(80)
    data = f.readframes(80)
    
    while data:
        # Read data from stdin
        device.write(data)
        data = f.readframes(1024)    
    f.close()
    
    
class Block:
    def __init__(self,x,y,z,name=None,soundfile=None,quantize=.10):
        self.radius = 1.20
        #this coordinate system don't match opengl's..it's reverse..so fix the z.
        self.x=x
        self.y=y
        self.z=-z
        #quantize the sound so it doesn't fire multiple times per collition
        self.lastfire=time.time() 
        self.quantize=quantize
        if name:
            self.name=name
        else:
            self.name="Block" + str(len(Blocks))
        if soundfile:
            self.soundfile=soundfile
        else:
            self.soundfile=None
        #uncomment for random colors
        #self.color=[random.random()-0.5,random.random()-0.5,random.random()-0.5]
        self.color=[1,1,1]
        self.rotate = [0.0,0.0]

def CollisionDetect(xyz):
    for xyzelement in xyz:
        for Block in Blocks:
            Distance = math.sqrt(  ((xyzelement[0]-Block.x)**2)  +  ((xyzelement[1]-Block.y)**2)  +  ((xyzelement[2]-Block.z)**2)  )
            if Distance <= (.065):
                #sys.stdout.write("point collide with %s: %f %s %f\n" % (Block.name,Distance,xyzelement,Block.lastfire))
                if Block.soundfile and abs(time.time() - Block.lastfire)>Block.quantize :
                    thread.start_new_thread(play, (Block.soundfile,))
                    Block.lastfire=time.time()

       
def project(depth, u, v):
    #don't ask me what this equation does..wasn't documented where I found it
    #Z = 1.0 / (-0.0030711*depth.flatten() + 3.3309495)
    #Z = 2.0/ (-0.0030711*depth.flatten() + 3.3309495)    
        #overall size/coordinate scale
        #      #scale of the depth lower=thinner
    #                                       #fish-eye scale of close objects vs far lower=close object bigger than far.
    Z = 1.0/  (-0.0030711*depth.flatten() + 3.3309495)
                                 #depth 
    X = (u.flatten()-320) * Z / 620.0
    Y = (v.flatten()-320) * Z / 620.0
    U = u.flatten()
    V = v.flatten()
    xyz = np.vstack((X,-Y,-Z)).transpose()
    uv = np.vstack((U,V)).transpose()
    #determine how much background/foreground to show
    #trim off any noise showing up as -z
    xyz = xyz[Z>0,:]
    uv = uv[Z>0,:]       
    Z=Z[Z>0]
    #how far in the distance to show?
    try:
        xyz = xyz[Z<CloudThreshold,  :]
        uv = uv[Z<CloudThreshold, :]       
    except:
        pass
    
    #check for collisions between points and drum blocks
    CollisionDetect(xyz)
    return xyz, uv

def DrawPointCloud():
    global CloudSample,CloudPointSize
    #Camera Position/Orient
    glTranslatef(CameraPos[0]/2,CameraPos[1]/2,-CameraPos[2]/2)
    glRotatef(-CameraRotate[1],1,0,0)
    glRotatef(-CameraRotate[0],0,1,0)        

    DrawBlocks()
    
    #get the kinecty goodness
    depth,tstamp=freenect.sync_get_depth()
    rgb, tstamp=freenect.sync_get_rgb()
    X,Y = np.meshgrid(range(640),range(480))
    #downsample size
    dd=CloudSample
    pointsize=CloudPointSize
    q=depth

    #to the cloud!
    projpts = project(q[::dd,::dd],X[::dd,::dd],Y[::dd,::dd])        
    xyz, uv = projpts    
    
    #use the rgb for texture
    if not rgb is None:
        rgb_ = (rgb.astype(np.float32) * 4 + 70).clip(200,255).astype(np.uint8)
        glBindTexture(TEXTURE_TARGET, rgbtex)
        glTexSubImage2D(TEXTURE_TARGET, 0, 0, 0, 640, 480, GL_RGB, GL_UNSIGNED_BYTE, rgb_);    

    # Draw the points from the kinect
    glPointSize(pointsize)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)
    glVertexPointerf(xyz)
    glTexCoordPointerf(uv)
    glEnable(TEXTURE_TARGET)
    glColor3f(1,1,1)
    glDrawElementsui(GL_POINTS, np.array(range(len(xyz))))
    #sys.stdout.write("xyz length: " + str(len(xyz)) + '\n')
    #sys.stdout.write("uv length:" + str(len(uv)) +'\n')
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_TEXTURE_COORD_ARRAY)
    glDisable(TEXTURE_TARGET)    


def DrawBlocks():

    glPointSize(15.0)
    #red block for 0/0/0 to orient
    glColor3f(1.0,0.0,0)   
    glBegin(GL_POINTS)    
    glVertex3f(0,0,0)
    
    for Block in Blocks:
        #pick a color
        #glColor3f(random.random()-0.5,random.random()-0.5,random.random()-0.5)
        if abs(time.time() - Block.lastfire)>Block.quantize:
            glColor3f(Block.color[0],Block.color[1], Block.color[2])
        else:
            #red=hit
            glColor3f(1.0,0,0)

        #draw it
        glVertex3f(Block.x,Block.y,Block.z)

    #end drawing of points    
    glEnd()  
    

def Draw():
    #Clear
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    DrawPointCloud()

    #show yourself.
    pygame.display.flip()

def GetInput():
    global CameraPos, CameraRotate, KeyPress, ViewMode, CloudThreshold,CloudPointSize,CloudSample
    CameraPos, CameraRotate, KeyPress, ViewMode, CloudThreshold, CloudSample, CloudPointSize = ModuleGetInput.main(CameraPos, CameraRotate, KeyPress, ViewMode, CloudThreshold, CloudSample, CloudPointSize)

def main():
    while True:
        GetInput()
        Draw()
        #need it slower?
        #clock.tick(200)
if __name__ == '__main__': 
    
    #make drum block placeholders 
    #put 'em where you want
#    opengl coords: +y=up 		-y=down
#		    +x=right 	        -x=left
#		    +z=back		-z=forward
#		    
#       (0,1,0)y
#	    |  /(0,0,1)z
#	    | /
#	    |/___(1,0,0)
#       (0,0,0)x
    
    #Blocks.append(Block(0,-.05,-.55))
    #Blocks.append(Block(-.30,-.05,-.55))    
    #Blocks.append(Block(1,0,1))
    #kick='wavs/kickdrum-low.wav'
    kick='wavs/kick_01.wav'
    hat='wavs/hihat-thin.wav'
    snare='wavs/snare-thinlong.wav'    
    Blocks.append(Block( .35, 0, 1.10,"snare",snare,.25)) #to my left (facing kinect), behind my chair
    Blocks.append(Block(   0, 0, 1.10,"kick",kick,.25))  #center
    Blocks.append(Block(-.25, 0, 1.10,"hat",hat,.25)) #to my right
    
    main()

















