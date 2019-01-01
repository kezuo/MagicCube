from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt4.QtGui import *
from PyQt4.QtOpenGL import *
from PyQt4 import QtOpenGL
from PyQt4.QtCore import *
from numpy import *
import math
class MagicCube:
	corners=(0,2,6,8,18,20,24,26)
	edges=(1,5,7,3,19,23,25,21)
	centers=(4,10,14,16,12,22)
	origin=13
	dist=2.75
	class Cube:
		def __init__(self):
			self.l=0
			self.r=0
			self.b=0
			self.t=0
			self.n=0
			self.f=0
			self.m=QMatrix4x4()
	def __init__(self):
		self.cubes=[]
		for i in range(27):
			self.cubes.append(MagicCube.Cube())
		for i in 0,3,6,9,12,15,18,21,24:
			self.cubes[i].l=0xffffffff
			self.cubes[i].m.translate(-MagicCube.dist,0,0)
		for i in 2,5,8,11,14,17,20,23,26:
			self.cubes[i].r=0xff0000ff
			self.cubes[i].m.translate(MagicCube.dist,0,0)
		for i in 18,19,20,21,22,23,24,25,26:
			self.cubes[i].b=0xffff0000
			self.cubes[i].m.translate(0,-MagicCube.dist,0)
		for i in 0,1,2,3,4,5,6,7,8:
			self.cubes[i].t=0xff00ffff
			self.cubes[i].m.translate(0,MagicCube.dist,0)
		for i in 0,1,2,9,10,11,18,19,20:
			self.cubes[i].n=0xff00ff00
			self.cubes[i].m.translate(0,0,-MagicCube.dist)
		for i in 6,7,8,15,16,17,24,25,26:
			self.cubes[i].f=0xffff00ff
			self.cubes[i].m.translate(0,0,MagicCube.dist)
		self.cubes[MagicCube.origin]=None
		for cube in self.cubes:
			if cube:
				cube.displayList=glGenLists(1)		
				glNewList(cube.displayList,GL_COMPILE)
				if cube.l:
					glBegin(GL_TRIANGLE_FAN)
					glColor(QColor(cube.l).getRgb())
					glVertex3f(-1,-1,-1)
					glVertex3f(-1,1,-1)
					glVertex3f(-1,1,1)
					glVertex3f(-1,-1,1)
					glEnd()
				if cube.r:
					glBegin(GL_TRIANGLE_FAN)
					glColor(QColor(cube.r).getRgb())
					glVertex3f(1,-1,-1)
					glVertex3f(1,-1,1)
					glVertex3f(1,1,1)
					glVertex3f(1,1,-1)
					glEnd()
				if cube.b:
					glBegin(GL_TRIANGLE_FAN)
					glColor(QColor(cube.b).getRgb())
					glVertex3f(-1,-1,-1)
					glVertex3f(-1,-1,1)
					glVertex3f(1,-1,1)
					glVertex3f(1,-1,-1)
					glEnd()
				if cube.t:
					glBegin(GL_TRIANGLE_FAN)
					glColor(QColor(cube.t).getRgb())
					glVertex3f(-1,1,-1)
					glVertex3f(1,1,-1)
					glVertex3f(1,1,1)
					glVertex3f(-1,1,1)
					glEnd()
				if cube.n:
					glBegin(GL_TRIANGLE_FAN)
					glColor(QColor(cube.n).getRgb())
					glVertex3f(-1,-1,-1)
					glVertex3f(1,-1,-1)
					glVertex3f(1,1,-1)
					glVertex3f(-1,1,-1)
					glEnd()
				if cube.f:
					glBegin(GL_TRIANGLE_FAN)
					glColor(QColor(cube.f).getRgb())
					glVertex3f(-1,-1,1)
					glVertex3f(-1,1,1)
					glVertex3f(1,1,1)
					glVertex3f(1,-1,1)
					glEnd()
				glEndList()
	
	def draw(self):
		for cube in self.cubes:
			if cube:
				glMatrixMode(GL_MODELVIEW)
				glPushMatrix()
				glMultMatrixf(array(cube.m.data(),dtype=float32))
				glCallList(cube.displayList)
				glPopMatrix()
class MagicWidget(QGLWidget):
	def __init__(self,parent=None):
		QGLWidget.__init__(self,parent)
		self.setAutoFillBackground(False)
		self.modelView=QMatrix4x4()
		self.modelView.scale(0.125,0.125,0.125)
		self.timer=QTimer()
		self.timer.setSingleShot(False)
		self.timer.timeout.connect(self.animate)
		self.timer.setInterval(25)
	def initializeGL(self):
		self.magicCube=MagicCube()
	def animate(self):
		self.modelView.rotate(1,1,1,1)
		self.update()
	def __setGLPaintState(self):
		glPointSize(3)
		glClearColor(0,0,0,0)
		glClearDepth(1)
		glDepthRange(0,1)
        	glViewport((self.w - self.side) / 2, (self.h - self.side) / 2, self.side, self.side)
		glEnable(GL_DEPTH_TEST)
		glDisable(GL_CULL_FACE)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		glMatrixMode(GL_MODELVIEW)
		glLoadMatrixf(array(self.modelView.data(),dtype=float32))
	def resizeGL(self,w,h):
		self.w=w
		self.h=h
		self.side = min(w, h)
	def __addPoint(self,event):
		z=glReadPixelsf(x,y,1,1,GL_DEPTH_COMPONENT)
		x,y,z=gluUnProject(x,y,z,model=array(self.modelView.data(),dtype=float64))
	def mousePressEvent(self,event):	
		self.oldX=event.x()
		self.oldY=self.h-event.y()
		self.rotateM=QMatrix4x4()
	def mouseMoveEvent(self,event):
		curX=event.x()
		curY=self.h-event.y()
		dX=curX-self.oldX
		dY=curY-self.oldY
		axisX=dY
		axisY=-dX
		degree=math.sqrt(dX*dX+dY*dY)*360/self.side
		self.rotateM.setToIdentity()
		self.rotateM.rotate(degree,axisX,axisY,0)
		self.modelView=self.rotateM*self.modelView	
		self.oldX=curX
		self.oldY=curY
		if not self.timer.isActive():
			self.update()
	def mouseReleaseEvent(self,event):
		pass
	def paintEvent(self,pE):
		painter=QPainter(self)
		self.__setGLPaintState()
		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
		self.magicCube.draw()
app=QApplication(['demo'])
glFormat=QGLFormat()
glFormat.setVersion(3,0)
QGLFormat.setDefaultFormat(glFormat)
overallWidget=QWidget()
overallWidget.setMinimumSize(400,600)
vBox=QVBoxLayout()
topButton=QPushButton("topButton")
bottomButton=QPushButton("bottomButton")
bar=QSlider(Qt.Horizontal)
bottomButton.clicked.connect(lambda :magicWidget.timer.start())
topButton.clicked.connect(lambda :magicWidget.timer.stop())
def setValue(x):
	pass
bar.valueChanged.connect(setValue)
magicWidget=MagicWidget()
overallWidget.setLayout(vBox)
vBox.addWidget(topButton)
vBox.addWidget(bottomButton)
vBox.addWidget(magicWidget)
vBox.addWidget(bar)
overallWidget.show()
app.exec_()
