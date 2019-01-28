from PyQt4.QtGui import *
from PyQt4.QtOpenGL import *
from PyQt4.QtCore import *
from OpenGL.GL import *#For some reason it's needed,otherwise the 'cannot make invaild context current' error jump out oddly
from magic import MagicWidget
import random
threadInput=QThread()
def performInput():
	if threadInput.isRunning():
		return
	threadInput.run=lambda:jobInput(lineEdit.text())
	threadInput.start()
def jobInput(actionString):
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
threadRandom=QThread()
def swichRandom():
	global stop
	if threadRandom.isRunning():
		stop=True
	else:
		stop=False
		threadRandom.start()
def jobRandom():
	global stop
	while not stop:
		while not magicWidget.magicCube.operate(random.randint(0,8),random.randint(-2,2)):pass
threadRandom.run=jobRandom
app=QApplication(['MagicCube'])
glFormat=QGLFormat()
glFormat.setVersion(3,0)
QGLFormat.setDefaultFormat(glFormat)
overallWidget=QWidget()
overallWidget.setMinimumSize(400,600)
vBox=QVBoxLayout()
button=QPushButton('Swich randomly operation')
lineEdit=QLineEdit()
magicWidget=MagicWidget()
button.clicked.connect(swichRandom)
lineEdit.returnPressed.connect(performInput)
overallWidget.setLayout(vBox)
vBox.addWidget(button)
vBox.addWidget(lineEdit)
vBox.addWidget(magicWidget)
overallWidget.show()
lineEdit.setPlaceholderText('Operation input')
app.exec_()
