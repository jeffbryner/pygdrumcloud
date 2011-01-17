from OpenGL.GL import *
from OpenGL.GLU import *
import GL
import os, sys, math, random
import pygame
from pygame.locals import *
pygame.init()


def main(CameraPos, CameraRotate, KeyPress, ViewMode, CloudThreshold,CloudSample,CloudPointSize):
    keystate = pygame.key.get_pressed()
    mrel = pygame.mouse.get_rel()
    #mrel[0] is gl X coord, -=left
    #mrel[1] is gl Y coord, -=up
    mpress = pygame.mouse.get_pressed()
    for event in pygame.event.get():
        if event.type == QUIT or keystate[K_ESCAPE]:
            pygame.quit(); sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            ScrollSpeed = 1.1
            if event.button == 4: #Scroll In
                #CameraPos[1] += ScrollSpeed*math.sin(math.radians(CameraRotate[1]))
                #CameraPos[2] -= ScrollSpeed*math.cos(math.radians(CameraRotate[0]))*math.cos(math.radians(CameraRotate[1]))
                #CameraPos[0] += ScrollSpeed*math.sin(math.radians(CameraRotate[0]))*math.cos(math.radians(CameraRotate[1]))
                CameraPos[2]-=ScrollSpeed
            elif event.button == 5: #Scroll Out
                #CameraPos[1] -= ScrollSpeed*math.sin(math.radians(CameraRotate[1]))
                #CameraPos[2] += ScrollSpeed*math.cos(math.radians(CameraRotate[0]))*math.cos(math.radians(CameraRotate[1]))
                #CameraPos[0] -= ScrollSpeed*math.sin(math.radians(CameraRotate[0]))*math.cos(math.radians(CameraRotate[1]))
                CameraPos[2]+=ScrollSpeed
        elif event.type == VIDEORESIZE:
            print event
            #glViewport(0, 0, event.w, event.h)
            #gluPerspective(45, .05*event.w/event.h, 1.0, 10000.0)
            GL.resize(event.size)
        
    if mpress[0]:
        #left mouse controls scene position/left right
        Angle = math.radians(-CameraRotate[0])
        #Speed = 0.1*(CameraPos[1]/50.0)
        Speed = .08
        #sys.stdout.write("mrel %s \t CameraPos %s\n" % (str(mrel), str(CameraPos)))
        CameraPos[0]+=(Speed*mrel[0])
        CameraPos[1]+=(Speed*(-1*mrel[1])) #(change orientation to match opengl where -y is down, +y is up)
        #CameraPos[0] -= (Speed*math.cos(Angle)*mrel[0])
        #CameraPos[2] -= (Speed*math.sin(Angle)*-mrel[0])
        #CameraPos[0] -= (Speed*math.sin(Angle)*mrel[1])
        #CameraPos[2] -= (Speed*math.cos(Angle)*mrel[1])
    if mpress[2]:
        #right mouse controls rotation of camera
        CameraRotate[0] += mrel[0]
        CameraRotate[1] += mrel[1] 
    if keystate[K_SPACE]:
        print CameraPos
        print CameraRotate
        CameraPos = [0.3,-.40,.80]
        CameraRotate = [-15,-15]        
        ViewMode = 'Fill'
    if keystate[K_KP_PLUS]:
        CloudThreshold +=.02
        #sys.stdout.write("CloudThreshold: %f \n" % (CloudThreshold) )
    if keystate[K_KP_MINUS]:
        CloudThreshold -=.02 
        #sys.stdout.write("CloudThreshold: %f \n" % (CloudThreshold) )        
    if keystate[K_MINUS]:
        if CloudPointSize-.25>0:
            CloudPointSize-=.25
        sys.stdout.write("CloudPointSize: %f \n" % (CloudPointSize) )        
    if keystate[K_EQUALS] :
        if CloudPointSize+.25>0:
            CloudPointSize+=.25
        sys.stdout.write("CloudPointSize: %f \n" % (CloudPointSize) )                    

    if keystate[K_1]:
        if CloudSample-.5>.5:
            CloudSample-=.5
        sys.stdout.write("CloudSample: %f \n" % (CloudSample) )        
    if keystate[K_2] :
        if CloudSample+.5>0:
            CloudSample+=.5
        sys.stdout.write("CloudSample: %f \n" % (CloudSample) )                    
        
        
        
        
    if keystate[K_F1]:
        if not KeyPress[0]:
            if ViewMode == 'Fill': glPolygonMode(GL_FRONT_AND_BACK, GL_LINE); ViewMode = 'Line'
            elif ViewMode == 'Line': glPolygonMode(GL_FRONT_AND_BACK, GL_POINT); ViewMode = 'Point'
            elif ViewMode == 'Point': glPolygonMode(GL_FRONT_AND_BACK, GL_FILL); ViewMode = 'Fill'
            KeyPress[0] = True
    if not keystate[K_F1]: KeyPress[0] = False
    return CameraPos, CameraRotate, KeyPress, ViewMode, CloudThreshold,CloudSample,CloudPointSize
