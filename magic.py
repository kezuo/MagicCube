from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt4.QtGui import *
from PyQt4.QtOpenGL import *
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
		dist=2.2
		face.dist=dist
		left=face((-1,-1,-1),(-1,1,-1),(-1,1,1),(-1,-1,1),(-1,0,0),0xffffffff,{0:29,3:28,6:27,9:32,12:31,15:30,18:35,21:34,24:33})
		right=face((1,-1,-1),(1,-1,1),(1,1,1),(1,1,-1),(1,0,0),0xff0000ff,{2:9,5:10,8:11,11:12,14:13,17:14,20:15,23:16,26:17})
		bottom=face((-1,-1,-1),(-1,-1,1),(1,-1,1),(1,-1,-1),(0,-1,0),0xffff0000,{18:51,19:52,20:53,21:48,22:49,23:50,24:45,25:46,26:47})
		top=face((-1,1,-1),(1,1,-1),(1,1,1),(-1,1,1),(0,1,0),0xff00ffff,{0:42,1:43,2:44,3:39,4:40,5:41,6:36,7:37,8:38})
		near=face((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(0,0,-1),0xff00ff00,{0:0,1:1,2:2,9:3,10:4,11:5,18:6,19:7,20:8})
		far=face((-1,-1,1),(-1,1,1),(1,1,1),(1,-1,1),(0,0,1),0xffff00ff,{6:20,7:19,8:18,15:23,16:22,17:21,24:26,25:25,26:24})
		planes=(left,right,bottom,top,near,far)
		def __init__(self):
			self.faces={
			self.left:[0xff111111,-1],
			self.right:[0xff222222,-1],
			self.bottom:[0xff333333,-1],
			self.top:[0xff444444,-1],
			self.near:[0xff555555,-1],
			self.far:[0xff666666,-1]
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
					qColor.setRgba(self.faces[face][0])
					glBegin(GL_TRIANGLE_FAN)
					glColor(qColor.getRgbF())
					glVertex3f(*face.a)
					glVertex3f(*face.b)
					glVertex3f(*face.c)
					glVertex3f(*face.d)
					glEnd()
			glEndList()
	class RotationState:
		operationIndexs=(
		((6,3,0,42,39,36,20,23,26,45,48,51),(35,32,29,28,27,30,33,34)),
		(7,4,1,43,40,37,19,22,25,46,49,52),
		((8,5,2,44,41,38,18,21,24,47,50,53),(15,12,9,10,11,14,17,16)),
		((8,7,6,35,34,33,26,25,24,17,16,15),(53,52,51,48,45,46,47,50)),
		(5,4,3,32,31,30,23,22,21,14,13,12),
		((2,1,0,29,28,27,20,19,18,11,10,9),(44,43,42,39,36,37,38,41)),
		((44,43,42,29,32,35,51,52,53,15,12,9),(2,1,0,3,6,7,8,5)),
		(41,40,39,28,31,34,48,49,50,16,13,10),
		((38,37,36,27,30,33,45,46,47,17,14,11),(18,19,20,23,26,25,24,21))
		)
		def __init__(self):
			self.controledIndex=None
			self.remainDegree=0
			self.state=range(54)
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
			self.mutex=QMutex()
		def animate(self):
			if self.controledIndex!=None:
				index=self.controledIndex
				remain=self.remainDegree
				if math.fabs(self.remainDegree)<=4:
					self.controledIndex=None
					self.remainDegree=0
					self.rotateCubes(remain,index)
				elif self.remainDegree>0:
					self.remainDegree=self.remainDegree-4
					self.rotateCubes(4,self.controledIndex)
				elif self.remainDegree<0:
					self.remainDegree=self.remainDegree+4
					self.rotateCubes(-4,self.controledIndex)
				return
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
			self.mutex.lock()
			if self.rotateAxis==None:
				self.mutex.lock()
				return
			if index==None:
				index=self.operatingCubesIndex
			if self.rotateDegrees[index]==0:
				self.backups[index]=[]
				for cube in self.reArrangedCubes[index]:
					self.backups[index].append(QMatrix4x4(cube.matrix))
			self.rotateM.setToIdentity()
			self.rotateDegrees[index]=self.rotateDegrees[index]+degree
			fitDegree=round(self.rotateDegrees[index]/90.0)*90
			if math.fabs(self.rotateDegrees[index]-fitDegree)<0.000001:
				self.rotateDegrees[index]=0
				self.rotateM.rotate(fitDegree,self.rotateAxis.x(),self.rotateAxis.y(),self.rotateAxis.z())
				times=round(fitDegree/90)
				uniformIndex=index
				if self.rotateAxis.x()!=0:
					if self.rotateAxis.x()<0:
						times=times*-1
						uniformIndex=2-index
					kind=uniformIndex
				elif self.rotateAxis.y()!=0:
					if self.rotateAxis.y()<0:
						times=times*-1
						uniformIndex=2-index
					kind=uniformIndex+3
				elif self.rotateAxis.z()!=0:
					if self.rotateAxis.z()<0:
						times=times*-1
						uniformIndex=2-index
					kind=uniformIndex+6
				if self.remainDegree==0 and self.rotateDegrees[0]==0 and self.rotateDegrees[1]==0 and self.rotateDegrees[2]==0:
					self.rotateAxis=None
				for i in range(9):
					self.reArrangedCubes[index][i].matrix=self.rotateM*self.backups[index][i]
				self.changeState(kind,int(times))
			else :
				self.rotateM.rotate(degree,self.rotateAxis.x(),self.rotateAxis.y(),self.rotateAxis.z())
				for cube in self.reArrangedCubes[index]:
					cube.matrix=self.rotateM*cube.matrix
			self.mutex.unlock()
		def changeState(self,kind,times):
			times=times%4
			print 'changestate',kind,times
			if len(self.operationIndexs[kind])>2:
				for i in range(times):
					a,b,c=self.state[self.operationIndexs[kind][9]],self.state[self.operationIndexs[kind][10]],self.state[self.operationIndexs[kind][11]]
					for j in 2,1,0:	
						self.state[self.operationIndexs[kind][(j+1)*3]],self.state[self.operationIndexs[kind][(j+1)*3+1]],self.state[self.operationIndexs[kind][(j+1)*3+2]]=self.state[self.operationIndexs[kind][j*3]],self.state[self.operationIndexs[kind][j*3+1]],self.state[self.operationIndexs[kind][j*3+2]]
					self.state[self.operationIndexs[kind][0]],self.state[self.operationIndexs[kind][1]],self.state[self.operationIndexs[kind][2]]=a,b,c
			else:
				for i in range(times):
					a,b,c=self.state[self.operationIndexs[kind][0][9]],self.state[self.operationIndexs[kind][0][10]],self.state[self.operationIndexs[kind][0][11]]
					for j in 2,1,0:	
						self.state[self.operationIndexs[kind][0][(j+1)*3]],self.state[self.operationIndexs[kind][0][(j+1)*3+1]],self.state[self.operationIndexs[kind][0][(j+1)*3+2]]=self.state[self.operationIndexs[kind][0][j*3]],self.state[self.operationIndexs[kind][0][j*3+1]],self.state[self.operationIndexs[kind][0][j*3+2]]
					self.state[self.operationIndexs[kind][0][0]],self.state[self.operationIndexs[kind][0][1]],self.state[self.operationIndexs[kind][0][2]]=a,b,c
					a,b=self.state[self.operationIndexs[kind][1][6]],self.state[self.operationIndexs[kind][1][7]]
					for j in 2,1,0:	
						self.state[self.operationIndexs[kind][1][(j+1)*2]],self.state[self.operationIndexs[kind][1][(j+1)*2+1]]=self.state[self.operationIndexs[kind][1][j*2]],self.state[self.operationIndexs[kind][1][j*2+1]]
					self.state[self.operationIndexs[kind][1][0]],self.state[self.operationIndexs[kind][1][1]]=a,b
			current=self.owner.currentState()
			if current==False:
				print 'unaligned'
				return
			for i in range(54):
				if self.state[i]!=current[i]:
					print 'state error'
					return
			print 'ok'
	def __init__(self):
		self.cubes=[]
		self.rotationState=MagicCube.RotationState()
		self.rotationState.owner=self
		self.centerPosition=range(54)
		for i in range(27):
			self.cubes.append(MagicCube.cube())
		for plane in MagicCube.cube.planes:
			for i in plane.indexs:
				self.cubes[i].faces[plane][0]=plane.color
				self.cubes[i].faces[plane][1]=plane.indexs[i]
				self.cubes[i].matrix.translate(*plane.normal)
		for plane in MagicCube.cube.planes:
			planePosition=QVector3D(*plane.normal)
			for i in plane.indexs:
				centerPosition=self.cubes[i].matrix*planePosition
				self.centerPosition[plane.indexs[i]]=centerPosition
		for i in range(27):
			if self.cubes[i]:
				self.cubes[i].genList()
	def currentState(self):
		state=range(54)
		aligned=0
		for i in range(54):
			position=self.centerPosition[i]
			finded=False
			for cube in self.cubes:
				for face in cube.faces:
					sub=cube.matrix*QVector3D(*face.normal)-position
					if sub.length()<0.01:
						state[i]=cube.faces[face][1]
						aligned=aligned+1
						finded=True
						break
				if finded:
					break
		print 'aligned',aligned
		if aligned!=54:
			return False
		return state

	def operate(self,kind,times):
		self.rotationState.mutex.lock()
		if kind<0 or kind>8 or self.rotationState.remainDegree!=0 or self.rotationState.rotateDegrees[0]!=0 or self.rotationState.rotateDegrees[1]!=0 or self.rotationState.rotateDegrees[2]!=0:
			self.rotationState.mutex.unlock()
			return False
		direction=kind/3
		self.rotationState.controledIndex=kind%3
		self.rotationState.rotateAxis=[0,0,0]
		self.rotationState.rotateAxis[direction]=1
		self.rotationState.rotateAxis=QVector3D(*self.rotationState.rotateAxis)
		self.rotationState.remainDegree=times*90
		refPoint=QVector3D(0,0,0)
		origin=refPoint
		mapToCubes={}
		for cube in self.cubes:
			originTranslated=cube.matrix*origin
			normalComponent=QVector3D.dotProduct(originTranslated-refPoint,self.rotationState.rotateAxis)/self.rotationState.rotateAxis.length()
			if mapToCubes.has_key(normalComponent):
				mapToCubes[normalComponent].append(cube)
			else :
				mapToCubes[normalComponent]=[cube]
		i=0
		for normalComponent in sorted(mapToCubes.keys()):
			for cube in mapToCubes[normalComponent]:
				self.rotationState.reArrangedCubes[i/9][i%9]=cube
				i=i+1
		self.rotationState.mutex.unlock()
		return True
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
			if self.curCube.faces[self.curFace][0]==color:
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
			if QVector3D(*dV).length()<0.02:
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
