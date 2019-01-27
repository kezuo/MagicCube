from PyQt4.QtGui import *
from PyQt4.QtOpenGL import *
from PyQt4.QtCore import *
from OpenGL.GL import *#For some reason it's needed,otherwise the 'cannot make invaild context current' error jump out oddly.
from magic import MagicWidget
thread=QThread()
def performAction(actionString):
	if thread.isRunning():
		return
	thread.run=lambda:job(actionString)
	thread.start()
def job(actionString):
	l=[int(i) for i in actionString.split(' ')]
	if len(l)<2:
		return
	i=0
	kind=l[0]
	times=l[1]
	while True:
		print kind,times
		while not magicWidget.magicCube.operate(kind,times):pass
		if i+3<len(l):
			i=i+2
			kind=l[i]
			times=l[i+1]
		else:break
	while True:
		state=magicWidget.magicCube.currentState()
		if state!=False:break
	for i in range(54):
		if state[i]!=magicWidget.magicCube.rotationState.state[i]:
			print False
			return
	print True
app=QApplication(['MagicCube'])
glFormat=QGLFormat()
glFormat.setVersion(3,0)
QGLFormat.setDefaultFormat(glFormat)
overallWidget=QWidget()
overallWidget.setMinimumSize(400,600)
vBox=QVBoxLayout()
button=QPushButton()
lineEdit=QLineEdit()
magicWidget=MagicWidget()
button.clicked.connect(lambda :magicWidget.magicCube.currentState())
lineEdit.returnPressed.connect(lambda :performAction(lineEdit.text()))
overallWidget.setLayout(vBox)
vBox.addWidget(button)
vBox.addWidget(lineEdit)
vBox.addWidget(magicWidget)
overallWidget.show()
lineEdit.setFocus()
app.exec_()
