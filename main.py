from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt4.QtGui import *
from PyQt4.QtOpenGL import *
from PyQt4.QtCore import QString
class MyDrawer(QGLWidget):
	def __init__(self,parent=None):
		QGLWidget.__init__(self,parent)
		self.setMinimumSize(400,600)
	def initializeGL(self):
		self.g=1
		glClearColor(1,1,0,1)
		glClearDepth(1)
	def resizeGL(self,w,h):
		glViewport(0,0,w,h)
	def changeColor(self):
		if self.g:
			self.g=0
		else :
			self.g=1
		glClearColor(1,self.g,0,1)
		self.update()
	def paintGL(self):
		glClear(GL_COLOR_BUFFER_BIT)
		glFlush()
app=QApplication(['demo'])
win=QWidget()
box=QVBoxLayout()
button=QPushButton('changeColor')
myDrawer=MyDrawer()
button.clicked.connect(myDrawer.changeColor)
box.addWidget(button)
box.addWidget(myDrawer)
win.setLayout(box)
win.show()
app.exec_()
