
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QMainWindow, QWidget
# pip install pyqtgraph
import pyqtgraph as pg


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Network tool")

        layout = QHBoxLayout()

        layout.addWidget(QLabel('red'))
        layout.addWidget(QLabel('green'))
        layout.addWidget(QLabel('blue'))

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def makeTestPlot(self):
        # define the data 
        title = "GeeksforGeeks PyQtGraph"
        
        # y values to plot by line 1 
        y = [2, 8, 6, 8, 6, 11, 14, 13, 18, 19] 
        
        # y values to plot by line 2 
        y2 = [3, 1, 5, 8, 9, 11, 16, 17, 14, 16] 
        x = range(0, 10) 
        
        # create plot window object 
        plt = pg.plot() 
        
        # showing x and y grids 
        plt.showGrid(x = True, y = True) 
        
        # adding legend 
        plt.addLegend() 
        
        # set properties of the label for y axis 
        plt.setLabel('left', 'Vertical Values', units ='y') 
        
        # set properties of the label for x axis 
        plt.setLabel('bottom', 'Horizontal Vlaues', units ='s') 
        
        # setting horizontal range 
        plt.setXRange(0, 10) 
        
        # setting vertical range 
        plt.setYRange(0, 20) 
        
        # setting window title to the plot window 
        plt.setWindowTitle(title) 
        
        # ploting line in green color 
        # with dot symbol as x, not a mandatory field 
        line1 = plt.plot(x, y, pen ='g', symbol ='x', symbolPen ='g', 
                                symbolBrush = 0.2, name ='green') 
        
        # ploting line2 with blue color 
        # with dot symbol as o  
        line2 = plt.plot(x, y2, pen ='b', symbol ='o', symbolPen ='b', 
                                    symbolBrush = 0.2, name ='blue') 

#pg.setConfigOptions(antialias=False)
app = QApplication(sys.argv)

window = MainWindow()
window.show()
window.makeTestPlot()

app.exec_()
