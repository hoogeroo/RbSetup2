import sys
import matplotlib as plt
plt.use('QtAgg')  # Use the QtAgg backend for Matplotlib (works for PyQt6)
import matplotlib.figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QApplication, QWidget, QGridLayout

class PlotWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle('Matplotlib in PyQt6')
        self.setGeometry(100, 100, 800, 600)

        # Create a grid layout
        grid_fluo = QGridLayout(self)

        # Create a Matplotlib figure and canvas
        self.figure_fluo = plt.figure.Figure()
        self.canvas_fluo = FigureCanvas(self.figure_fluo)
        
        # Set up the figure (this could be customized further)
        self.makeFluoFig()

        # Add the canvas as a QWidget to the layout
        grid_fluo.addWidget(self.canvas_fluo, 0, 0, 15, 15)

    def makeFluoFig(self):
        """This function can be customized to add your plot to the figure."""
        ax = self.figure_fluo.add_subplot(111)
        ax.plot([1, 2, 3, 4], [1, 4, 9, 16])  # Example plot
        ax.set_title('Example Plot')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlotWindow()
    window.show()
    sys.exit(app.exec())
