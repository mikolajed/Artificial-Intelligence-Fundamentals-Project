import sys
from PyQt5.QtWidgets import QTabBar, QTabWidget, QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QTextBrowser, QHBoxLayout, QSlider
from PyQt5.QtCore import QRect, QPropertyAnimation, pyqtProperty, Qt, QUrl
from PyQt5.QtGui import QTextCursor
from PyQt5.QtGui import QDesktopServices
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class MPLWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.canvas)

class AnimatedTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._target_rect = QRect()

    def tabRect(self, index):
        if index == self.currentIndex():
            return self._target_rect
        return super().tabRect(index)

    @pyqtProperty(QRect)
    def targetRect(self):
        return self._target_rect

    @targetRect.setter
    def targetRect(self, rect):
        self._target_rect = rect
        self.update()

    def animateMoveTab(self, from_rect, to_rect):
        self._animation = QPropertyAnimation(self, b'targetRect')
        self._animation.setDuration(2000)
        self._animation.setStartValue(from_rect)
        self._animation.setEndValue(to_rect)
        self._animation.start()

    def setCurrentIndex(self, index):
        from_rect = self.tabRect(self.currentIndex())
        super().setCurrentIndex(index)
        to_rect = self.tabRect(index)
        self.animateMoveTab(from_rect, to_rect)

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Project of Evolutionary Algorithm for Subset Sum Problem")
        self.layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabBar(AnimatedTabBar())
        self.layout.addWidget(self.tab_widget)

        # Create tabs

        # Tab 1
        def draw_cos_wave():
            # Clear the current plot
            self.graph1.figure.clear()

            # Create a new plot
            ax = self.graph1.figure.add_subplot(111)
            x = np.linspace(0, 10, 100)
            line, = ax.plot(x, np.cos(x))

            def animate(i):
                line.set_ydata(np.cos(x + i / 10.0))  # update the data
                return line,

            # Init only required for blitting to give a clean slate.
            def init():
                line.set_ydata(np.ma.array(x, mask=True))
                return line,

            ani = FuncAnimation(self.graph1.figure, animate, np.arange(1, 200), init_func=init,
                                interval=50, blit=True)

            # Redraw the canvas
            self.graph1.canvas.draw()

        self.tab1 = QWidget()
        self.tab_widget.addTab(self.tab1, "Run Tests")
        # self.tab1_layout = QVBoxLayout(self.tab1)
        # self.run_tests_button = QPushButton("Run Tests")
        # self.run_tests_button.clicked.connect(self.run_tests)
        # self.tab1_layout.addWidget(self.run_tests_button)
        self.tab1_layout = QHBoxLayout(self.tab1)
        # Add MPLWidget to the left side of the layout
        self.graph1 = MPLWidget()
        self.tab1_layout.addWidget(self.graph1)
        # Add "Run" button to the right side of the layout
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(draw_cos_wave)
        self.tab1_layout.addWidget(self.run_button)

        # Tab 2
        def update_plot():
            mean = self.mean_slider.value()
            std_dev = self.std_slider.value()
            # Clear the current plot
            self.graph.figure.clear()
            # Create a new plot
            ax = self.graph.figure.add_subplot(111)
            x = np.linspace(-10, 10, 100)
            y = (1 / (np.sqrt(2 * np.pi * std_dev**2))) * np.exp(-((x - mean)**2) / (2 * std_dev**2))
            ax.plot(x, y)
            # Redraw the canvas
            self.graph.canvas.draw()
        self.tab2 = QWidget()
        self.tab_widget.addTab(self.tab2, "Generate Data/Inspect Data")

        # self.tab2_layout = QHBoxLayout(self.tab2)
        # self.graph = MPLWidget()
        # self.tab2_layout.addWidget(self.graph)
        # self.controls = QWidget()
        # self.controls_layout = QVBoxLayout(self.controls)
        # self.tab2_layout.addWidget(self.controls)
        # self.mean_label = QLabel("Mean:")
        # self.mean_text = QTextEdit()
        # self.controls_layout.addWidget(self.mean_label)
        # self.controls_layout.addWidget(self.mean_text)
        # self.std_label = QLabel("Standard Deviation:")
        # self.std_text = QTextEdit()
        # self.controls_layout.addWidget(self.std_label)
        # self.controls_layout.addWidget(self.std_text)
        self.tab2_layout = QHBoxLayout(self.tab2)

        # Add MPLWidget to the left side of the layout
        self.graph = MPLWidget()
        self.tab2_layout.addWidget(self.graph)

        # Add controls to the right side of the layout
        self.controls = QWidget()
        self.controls_layout = QVBoxLayout(self.controls)
        self.tab2_layout.addWidget(self.controls)

        self.mean_label = QLabel("Mean:")
        self.mean_slider = QSlider(Qt.Horizontal)
        self.mean_slider.setMinimum(-100)
        self.mean_slider.setMaximum(100)
        self.mean_slider.valueChanged.connect(update_plot)
        self.controls_layout.addWidget(self.mean_label)
        self.controls_layout.addWidget(self.mean_slider)

        self.std_label = QLabel("Standard Deviation:")
        self.std_slider = QSlider(Qt.Horizontal)
        self.std_slider.setMinimum(1)
        self.std_slider.setMaximum(100)
        self.std_slider.valueChanged.connect(update_plot)
        self.controls_layout.addWidget(self.std_label)
        self.controls_layout.addWidget(self.std_slider)

        # Tab 3
        self.tab3 = QWidget()
        self.tab_widget.addTab(self.tab3, "About the Project")
        self.tab3_layout = QVBoxLayout(self.tab3)
        self.about_text = QTextBrowser()
        self.about_text.setOpenExternalLinks(True)
        self.about_text.anchorClicked.connect(self.open_link)
        self.about_text.setObjectName("aboutText")
        self.about_text.setReadOnly(True)
        self.about_text.setHtml("""
            <h1 style="text-align: center;">
            Project of Evolutionary Algorithm for Subset Sum Problem
            </h1>
            <p style="text-align: center;">Developed by</p>                            
            <ul style="list-style-type: none; text-align: center; font-size: 24px;">
                <li style="font-size: 24px;">Mikołaj Jędrzejewski</li>
                <li style="font-size: 24px;">Piotr Syrokomski</li>
                <li style="font-size: 24px;">Mateusz Małkiewicz</li>
            </ul>
            <p style="text-align: center;">Supervised by</p>
            <ul style="list-style-type: none; text-align: center; font-size: 24px;">
                <li style="font-size: 24px;">Dr hab.&nbsp;inż.&nbsp;Jerzy Balicki</li>
            </ul>
            <p style="text-align: center;">Warsaw University of Technology</p>
            <p style="text-align: center;">Faculty of Mathematics and Information Science</p>
            <p style="text-align: center;">2024</p>
            <p> Available at: 
                <a href=https://github.com/mikolajjedrzejewski/evolutionary-algorithm-for-subset-sum-problem>
                    github.com/mikolajjedrzejewski/evolutionary-algorithm-for-subset-sum-problem
                </a>
            </p>
        """)
        self.tab3_layout.addWidget(self.about_text)

        with open('styles.qss', 'r') as f:
            self.setStyleSheet(f.read())

    def open_link(self, url):
        QDesktopServices.openUrl(url)

    def run_tests(self):
        # Add code to run tests and visualize results
        pass

    def generate_data(self):
        # Add code to generate and inspect data
        pass

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.setGeometry(100, 100, 800, 600)
    window.show()
    app.exec_()