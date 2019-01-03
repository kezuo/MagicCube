from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt4.QtGui import *
from PyQt4.QtOpenGL import *
from PyQt4 import QtOpenGL
from PyQt4.QtCore import *
from numpy import *
import math
class MagicCube:
	cornerIndexs=(0,2,6,8,18,20,24,26)
	edgeIndexs=(1,5,7,3,19,23,25,21)
	centerIndexs=(4,10,14,16,12,22)
	originIndex=13
	class cube:
		class face:
			def __init__(self,a,b,c,d,normal,color,indexs):
				self.a=a
				self.b=b
				self.c=c
				self.d=d
				self.normal=normal
				self.color=color
				self.indexs=indexs
		dist=2.75
		left=face((-1,-1,-1),(-1,1,-1),(-1,1,1),(-1,-1,1),(-dist,0,0),0xffffffff,(0,3,6,9,12,15,18,21,24))
		right=face((1,-1,-1),(1,-1,1),(1,1,1),(1,1,-1),(dist,0,0),0xff0000ff,(2,5,8,11,14,17,20,23,26))
		bottom=face((-1,-1,-1),(-1,-1,1),(1,-1,1),(1,-1,-1),(0,-dist,0),0xffff0000,(18,19,20,21,22,23,24,25,26))
		top=face((-1,1,-1),(1,1,-1),(1,1,1),(-1,1,1),(0,dist,0),0xff00ffff,(0,1,2,3,4,5,6,7,8))
		near=face((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(0,0,-dist),0xff00ff00,(0,1,2,9,10,11,18,19,20))
		far=face((-1,-1,1),(-1,1,1),(1,1,1),(1,-1,1),(0,0,dist),0xffff00ff,(6,7,8,15,16,17,24,25,26))
		planes=(left,right,bottom,top,near,far)
		def __init__(self):
			self.faces={
			self.left:0,
			self.right:0,
			self.bottom:0,
			self.top:0,
			self.near:0,
			self.far:0
			}
			self.matrix=QMatrix4x4()
			self.glList=0
		def genList(self):
			if self.glList:
				glDeleteLists(self.glList,1)
			self.glList=glGenLists(1)		
			glNewList(self.glList,GL_COMPILE)
			for face in self.faces:
				if self.faces[face]:
					qColor=QColor()
					qColor.setRgba(self.faces[face])
					glBegin(GL_TRIANGLE_FAN)
					glColor(qColor.getRgbF())
					glVertex3f(*face.a)
					glVertex3f(*face.b)
					glVertex3f(*face.c)
					glVertex3f(*face.d)
					glEnd()
			glEndList()
	def __init__(self):
		self.cubes=[]
		self.qVRotateAxis=None
		for i in range(27):
			self.cubes.append(MagicCube.cube())
		for plane in MagicCube.cube.planes:
			for i in plane.indexs:
				if self.cubes[i]:
					self.cubes[i].faces[plane]=plane.color
					self.cubes[i].matrix.translate(*plane.normal)
		for i in range(27):
			if self.cubes[i]:
				self.cubes[i].genList()
	def draw(self):
		for cube in self.cubes:
			if cube:
				glMatrixMode(GL_MODELVIEW)
				glPushMatrix()
				glMultMatrixf(array(cube.matrix.data(),dtype=float32))
				glCallList(cube.glList)
				glPopMatrix()
	def operaBegin(self,wx,wy):
		self.oldX,self.oldY=wx,wy
		self.rotateM=QMatrix4x4()
		depth=glReadPixelsf(wx,wy,1,1,GL_DEPTH_COMPONENT)
		color=glReadPixels(wx,wy,1,1,GL_RGBA,GL_UNSIGNED_INT_8_8_8_8)
		x,y,z=gluUnProject(wx,wy,depth,model=array(self.owner.modelView.data(),dtype=float64))
		self.qVObjectStart=QVector3D(x,y,z)
		color=color[0][0]
		color=(color>>8)|0xff000000
		finded=False
		for self.curCube in self.cubes:
			if self.curCube:
				invertedM,sucess=self.curCube.matrix.inverted()
				nativeV=invertedM*QVector3D(x,y,z)
				self.nativeStartX,self.nativeStartY,self.nativeStartZ=nativeV.x(),nativeV.y(),nativeV.z()
				if math.fabs(self.nativeStartX)<1.03 and math.fabs(self.nativeStartY)<1.03 and math.fabs(self.nativeStartZ)<1.03:
					finded=True
					break
		if not finded:
			print 'No cube finded'
			return False
		for self.curFace in self.cube.planes:
			if self.curCube.faces[self.curFace]==color:
				break
		return True
	def operaContin(self,wx,wy):
		if not self.qVRotateAxis:
			modelView=self.owner.modelView*self.curCube.matrix
			depth=glReadPixelsf(wx,wy,1,1,GL_DEPTH_COMPONENT)
			x,y,z=gluUnProject(wx,wy,depth,model=array(modelView.data(),dtype=float64))
			if math.fabs(x)>1.03 or math.fabs(y)>1.03 or math.fabs(z)>1.03:
				return
			dV=[0,0,0]
			dV[0],dV[1],dV[2]=x-self.nativeStartX,y-self.nativeStartY,z-self.nativeStartZ
			indexs=[0,1,2]
			for  outAxisIndex in 0,1,2:
				if self.curFace.normal[outAxisIndex]:
					indexs.remove(outAxisIndex)
					dV[outAxisIndex]=0
					break;
			if math.fabs(dV[indexs[0]])>math.fabs(dV[indexs[1]]):
				dV[indexs[1]]=0
				alongAxisIndex=indexs[0]
			else:
				dV[indexs[0]]=0
				alongAxisIndex=indexs[1]
			qVNormal=QVector3D(*self.curFace.normal)
			self.dWindowX,self.dWindowY,z=gluProject(self.nativeStartX,self.nativeStartY,self.nativeStartZ,model=array(modelView.data(),dtype=float64))
			self.dWindowX=wx-self.dWindowX
			self.dWindowY=wy-self.dWindowY
			self.dWindowL=math.sqrt(self.dWindowX*self.dWindowX+self.dWindowY*self.dWindowY)
			qVAlong=QVector3D(*dV)
			qVRotate=QVector3D.crossProduct(qVNormal,qVAlong)
			qVRotate=self.curCube.matrix*qVRotate
			qVOrigin=QVector3D(0,0,0)
			qVRefPoint=self.curCube.matrix*qVOrigin
			self.qVRotateAxis=qVRotate-qVRefPoint
			self.rotatingCubes=[]
			for cube in self.cubes:
				qVOriginTranslated=cube.matrix*qVOrigin
				if math.fabs(QVector3D.dotProduct(qVOriginTranslated-qVRefPoint,self.qVRotateAxis))<0.04:
					self.rotatingCubes.append(cube)
			print len(self.rotatingCubes)
			if len(self.rotatingCubes)!=9:
				self.qVRotateAxis=None
		else:
			dX=wx-self.oldX
			dY=wy-self.oldY
			degree=(dX*self.dWindowX+dY*self.dWindowY)/self.dWindowL*360/self.owner.side
			self.rotateM.setToIdentity()
			self.rotateM.rotate(degree,self.qVRotateAxis.x(),self.qVRotateAxis.y(),self.qVRotateAxis.z())
			for cube in self.rotatingCubes:
				cube.matrix=self.rotateM*cube.matrix
			self.owner.update()
			self.oldX,self.oldY=wx,wy
	def operaEnd(self,wx,wy):
		self.qVRotateAxis=None
		pass
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
		self.magicCube.owner=self
		self.passEvent=False
	def animate(self):
		self.modelView.rotate(1,1,1,1)
		self.update()
	def __setGLPaintState(self):
		glEnable(GL_BLEND)
		glHint(GL_POLYGON_SMOOTH_HINT,GL_FASTEST)
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
	def mousePressEvent(self,event):	
		self.oldX=event.x()
		self.oldY=self.h-event.y()
		self.rotateM=QMatrix4x4()
		if not self.passEvent:
				self.passEvent=self.magicCube.operaBegin(self.oldX,self.oldY)
	def mouseMoveEvent(self,event):
		curX=event.x()
		curY=self.h-event.y()
		if self.passEvent:
			self.magicCube.operaContin(curX,curY)
			return 
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
		self.update()
	def mouseReleaseEvent(self,event):
		endX=event.x()
		endY=self.h-event.y()
		if self.passEvent:
			self.passEvent=False
			self.magicCube.operaEnd(endX,endY)
	def paintEvent(self,pE):
		painter=QPainter(self)
		self.__setGLPaintState()
		glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
		self.magicCube.draw()
app=QApplication(['demo'])
glFormat=QGLFormat()
glFormat.setVersion(3,0)
glFormat.setAlpha(True)
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
