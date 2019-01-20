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
				self.normal=(normal[0]*self.dist,normal[1]*self.dist,normal[2]*self.dist)
				self.color=color
				self.indexs=indexs
		dist=3.2
		face.dist=dist
		left=face((-1,-1,-1),(-1,1,-1),(-1,1,1),(-1,-1,1),(-1,0,0),0xffffffff,(0,3,6,9,12,15,18,21,24))
		right=face((1,-1,-1),(1,-1,1),(1,1,1),(1,1,-1),(1,0,0),0xff0000ff,(2,5,8,11,14,17,20,23,26))
		bottom=face((-1,-1,-1),(-1,-1,1),(1,-1,1),(1,-1,-1),(0,-1,0),0xffff0000,(18,19,20,21,22,23,24,25,26))
		top=face((-1,1,-1),(1,1,-1),(1,1,1),(-1,1,1),(0,1,0),0xff00ffff,(0,1,2,3,4,5,6,7,8))
		near=face((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(0,0,-1),0xff00ff00,(0,1,2,9,10,11,18,19,20))
		far=face((-1,-1,1),(-1,1,1),(1,1,1),(1,-1,1),(0,0,1),0xffff00ff,(6,7,8,15,16,17,24,25,26))
		planes=(left,right,bottom,top,near,far)
		def __init__(self):
			self.faces={
			self.left:0xff111111,
			self.right:0xff222222,
			self.bottom:0xff333333,
			self.top:0xff444444,
			self.near:0xff555555,
			self.far:0xff666666
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
	class RotationState:
		def __init__(self):
			self.rotateAxis=None
			self.reArrangedCubes=[range(9),range(9),range(9)]
			self.operatingCubesIndex=None
			self.rotateDegrees=[0,0,0]
			self.objTangent=None
			self.refPoint=None
			self.rotateM=QMatrix4x4()
			self.backups=[None,None,None]
			self.animateTimer=QTimer()
			self.animateTimer.setSingleShot(False)
			self.animateTimer.setInterval(50)
			self.animateTimer.timeout.connect(self.animate)
			self.animateTimer.start()
		def animate(self):
			for i in 0,1,2:
				if self.operatingCubesIndex!=i and self.rotateDegrees[i]!=0:
					fitDegree=round(self.rotateDegrees[i]/90)*90
					if math.fabs(self.rotateDegrees[i]-fitDegree)<2:
						self.rotateCubes(fitDegree-self.rotateDegrees[i],i)
					elif fitDegree>self.rotateDegrees[i]:
						self.rotateCubes(2,i)
					else:
						self.rotateCubes(-2,i)
		def rotateCubes(self,degree,index=None):
			if self.rotateAxis==None:
				return
			if index==None:
				index=self.operatingCubesIndex
			if self.rotateDegrees[index]==0:
				self.backups[index]=[]
				for cube in self.reArrangedCubes[index]:
					self.backups[index].append(QMatrix4x4(cube.matrix))
			self.rotateM.setToIdentity()
			self.rotateDegrees[index]=self.rotateDegrees[index]+degree
			fitDegree=round(self.rotateDegrees[index]/90)*90
			if math.fabs(self.rotateDegrees[index]-fitDegree)<0.001:
				self.rotateDegrees[index]=0
				self.rotateM.rotate(fitDegree,self.rotateAxis.x(),self.rotateAxis.y(),self.rotateAxis.z())
				if self.rotateDegrees[0]==0 and self.rotateDegrees[1]==0 and self.rotateDegrees[2]==0:
					self.rotateAxis=None
				for i in range(9):
					self.reArrangedCubes[index][i].matrix=self.rotateM*self.backups[index][i]

			else :
				self.rotateM.rotate(degree,self.rotateAxis.x(),self.rotateAxis.y(),self.rotateAxis.z())
				for cube in self.reArrangedCubes[index]:
					cube.matrix=self.rotateM*cube.matrix
	def __init__(self):
		self.cubes=[]
		self.rotationState=MagicCube.RotationState()
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
		depth=glReadPixelsf(wx,wy,1,1,GL_DEPTH_COMPONENT)
		color=(glReadPixels(wx,wy,1,1,GL_RGBA,GL_UNSIGNED_INT_8_8_8_8)[0][0]>>8)|0xff000000
		finded=False
		for self.curCube in self.cubes:
			if self.curCube:
				nativeV=QVector3D(*gluUnProject(wx,wy,depth,model=array((self.owner.modelView*self.curCube.matrix).data(),dtype=float64)))
				self.nativeStartX,self.nativeStartY,self.nativeStartZ=nativeV.x(),nativeV.y(),nativeV.z()
				if math.fabs(self.nativeStartX)<1.03 and math.fabs(self.nativeStartY)<1.03 and math.fabs(self.nativeStartZ)<1.03:
					finded=True
					break
		if not finded:
			return False
		for self.curFace in self.cube.planes:
			if self.curCube.faces[self.curFace]==color:
				break
		return True
	def operaContin(self,wx,wy):
		if not self.rotationState.rotateAxis:
			depth=glReadPixelsf(wx,wy,1,1,GL_DEPTH_COMPONENT)
			x,y,z=gluUnProject(wx,wy,depth,model=array((self.owner.modelView*self.curCube.matrix).data(),dtype=float64))
			if math.fabs(x)>1.03 or math.fabs(y)>1.03 or math.fabs(z)>1.03:
				return
			dV=[0,0,0]
			dV[0],dV[1],dV[2]=x-self.nativeStartX,y-self.nativeStartY,z-self.nativeStartZ
			if QVector3D(*dV).length()<0.01:
				return
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
			origin=QVector3D(0,0,0)
			rotateEndPoint=self.curCube.matrix*QVector3D.crossProduct(QVector3D(*self.curFace.normal),QVector3D(*dV))
			refPoint=self.curCube.matrix*origin
			self.rotationState.objTangent=self.curCube.matrix*QVector3D(*dV)-refPoint	
			self.rotationState.rotateAxis=rotateEndPoint-refPoint
			i=0
			mapToCubes={}
			for cube in self.cubes:
				originTranslated=cube.matrix*origin
				normalComponent=QVector3D.dotProduct(originTranslated-refPoint,self.rotationState.rotateAxis)/self.rotationState.rotateAxis.length()
				if mapToCubes.has_key(normalComponent):
					mapToCubes[normalComponent].append(cube)
				else :
					mapToCubes[normalComponent]=[cube]
				if math.fabs(normalComponent)<self.cube.dist/3000:
					i=i+1
			if i!=9:
				self.rotationState.rotateAxis=None
				return
			i=0
			for normalComponent in sorted(mapToCubes.keys()):
				for cube in mapToCubes[normalComponent]:
					self.rotationState.reArrangedCubes[i/9][i%9]=cube
					if math.fabs(normalComponent)<self.cube.dist/3000 and self.rotationState.operatingCubesIndex==None:
						self.rotationState.operatingCubesIndex=i/9
					i=i+1
		elif self.rotationState.operatingCubesIndex==None:
			finded=False
			for i in 0,1,2:
				for cube in self.rotationState.reArrangedCubes[i]:
					if cube==self.curCube:
						finded=True
						break
				if finded:
					break
			self.rotationState.operatingCubesIndex=i
		else:
			winTan=QVector3D(*gluProject(self.rotationState.objTangent.x(),self.rotationState.objTangent.y(),self.rotationState.objTangent.z(),model=array(self.owner.modelView.data(),dtype=float64)))
			winTan.setZ(0)
			winTan.setX(winTan.x()-self.owner.centerX)
			winTan.setY(winTan.y()-self.owner.centerY)
			degree=QVector3D.dotProduct(QVector3D(wx-self.oldX,wy-self.oldY,0),winTan)*360/winTan.length()/self.owner.side
			self.rotationState.rotateCubes(degree)
			self.oldX,self.oldY=wx,wy
	def operaEnd(self,wx,wy):
		self.rotationState.operatingCubesIndex=None
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
		self.timer.start() 
	def initializeGL(self):
		self.magicCube=MagicCube()
		self.magicCube.owner=self
		self.passEvent=False
	def animate(self):
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
		self.centerX=self.w/2
		self.centerY=self.h/2
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
