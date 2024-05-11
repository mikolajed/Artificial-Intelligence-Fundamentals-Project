import sys
import os
from PyQt6.QtWidgets import QComboBox, QTabBar, QTabWidget, QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QTextBrowser, QHBoxLayout, QSlider
from PyQt6.QtCore import QRect, QPropertyAnimation, pyqtProperty, Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QTextCursor, QDesktopServices
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import seaborn as sns

class FileDragDrop(QLabel):
    fileDropped = pyqtSignal(str)

    def __init__(self, title, parent=None):
        super(FileDragDrop, self).__init__(title, parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0].toLocalFile()
            self.fileDropped.emit(url)

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

class ComboBoxWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.combo_box = QComboBox()
        self.combo_box.addItems(["naive", "genetic programming", "evolutionary programming"])
        self.delete_button = QPushButton("🗑️")
        self.delete_button.clicked.connect(self.delete_self)
        self.layout.addWidget(self.combo_box)
        self.layout.addWidget(self.delete_button)

    def delete_self(self):
        self.deleteLater()

class AlgorithmSelectionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.plus_button = QPushButton("+")
        self.plus_button.clicked.connect(self.add_combo_box)
        self.layout.addWidget(self.plus_button)
        self.layout.setAlignment(self.plus_button, Qt.AlignmentFlag.AlignCenter)

    def add_combo_box(self):
        combo_box_widget = ComboBoxWidget()
        self.layout.addWidget(combo_box_widget)

class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Project of Evolutionary Algorithm for Subset Sum Problem")
        self.layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabBar(AnimatedTabBar())
        self.layout.addWidget(self.tab_widget)
        self.graph1 = None
        self.graph = None
        self.datast_path = ""
        self.solutions_paths = []
        
        # Create tabs

        # Tab 1
        self.tab1 = QWidget()
        self.tab_widget.addTab(self.tab1, "Run Tests")

        # Create a main layout
        self.main_layout = QHBoxLayout(self.tab1)
        # Add MPLWidget to the left side of the layout
        self.graph1 = MPLWidget()
        #plt.style.use('ggplot')  # 'ggplot' is a popular style that emulates the aesthetics of ggplot in R.
        sns.set_theme()
        self.main_layout.addWidget(self.graph1)

        # Create a QVBoxLayout for the right side of the layout
        self.right_layout = QVBoxLayout()

        # Create a QWidget for the right side of the layout
        self.right_widget = QWidget()
        self.right_widget.setFixedWidth(400)
        self.right_widget.setLayout(self.right_layout)

        # Add "Choose dataset" label to the top of the right layout
        self.choose_dataset_label = QLabel("Choose dataset")
        self.choose_dataset_label.setObjectName("choose_dataset_label")
        self.right_layout.addWidget(self.choose_dataset_label)

        # Add drag and drop area
        self.file_drag_drop = FileDragDrop("")
        self.file_drag_drop.setObjectName("file_drag_drop")
        self.file_drag_drop.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_drag_drop.fileDropped.connect(self.file_dropped)
        self.right_layout.addWidget(self.file_drag_drop)

        # Create a QVBoxLayout for the drag and drop label and the "Browse" button
        self.drag_drop_layout = QVBoxLayout()
        self.drag_drop_label = QLabel("Drag and drop file here")
        self.drag_drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drag_drop_layout.addWidget(self.drag_drop_label)

        # Create a QHBoxLayout for the "Browse" button
        self.browse_layout = QHBoxLayout()
        self.browse_button = QPushButton("Browse")
        self.browse_button.setObjectName("browse_button")
        self.browse_button.clicked.connect(self.browse_file)
        self.browse_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.browse_layout.addWidget(self.browse_button)

        # Add the "Browse" button layout to the drag and drop layout
        self.drag_drop_layout.addLayout(self.browse_layout)

        # Add the drag and drop layout to the drag and drop area
        self.file_drag_drop.setLayout(self.drag_drop_layout)

        # Add "Add solutions" label
        self.add_solutions_label = QLabel("Add solutions")
        self.add_solutions_label.setObjectName("add_solutions_label")
        self.right_layout.addWidget(self.add_solutions_label)

        # Create an MPLWidget
        self.algorithm_combo_widget = AlgorithmSelectionWidget()

        # Add the MPLWidget to the right layout
        self.right_layout.addWidget(self.algorithm_combo_widget)


        # Add "Run" button to the bottom of the right layout
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.draw_cos_wave)
        self.right_layout.addWidget(self.run_button)

        # Add the right layout to the main layout
        self.main_layout.addWidget(self.right_widget)
        
        # Tab 2
        self.tab2 = QWidget()
        self.tab_widget.addTab(self.tab2, "Generate Data")
        self.tab2_layout = QHBoxLayout(self.tab2)
        # Add MPLWidget to the left side of the layout
        self.graph = MPLWidget()
        self.tab2_layout.addWidget(self.graph)
        # Add controls to the right side of the layout
        self.controls = QWidget()
        self.controls_layout = QVBoxLayout(self.controls)
        self.tab2_layout.addWidget(self.controls)

        self.mean_label = QLabel("Mean:")
        self.mean_slider = QSlider(Qt.Orientation.Horizontal)
        self.mean_slider.setMinimum(-100)
        self.mean_slider.setMaximum(100)
        self.mean_slider.valueChanged.connect(self.update_plot)
        self.controls_layout.addWidget(self.mean_label)
        self.controls_layout.addWidget(self.mean_slider)

        self.std_label = QLabel("Standard Deviation:")
        self.std_slider = QSlider(Qt.Orientation.Horizontal)
        self.std_slider.setMinimum(1)
        self.std_slider.setMaximum(100)
        self.std_slider.valueChanged.connect(self.update_plot)
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

    def draw_cos_wave(self):
        self.graph1.figure.clear()
        ax = self.graph1.figure.add_subplot(111)
        x = np.linspace(0, 10, 100)
        line, = ax.plot(x, np.cos(x))

        def animate(i):
            line.set_ydata(np.cos(x + i / 10.0))  
            return line,
    
        # Init only required for blitting to give a clean slate.
        def init():
            line.set_ydata(np.ma.array(x, mask=True))
            return line,
        ani = FuncAnimation(self.graph1.figure, animate, np.arange(1, 200), init_func=init,
                            interval=50, blit=True)
        self.graph1.canvas.draw()

    def update_plot(self):
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


    def open_link(self, url):
        QDesktopServices.openUrl(url)

    def run_tests(self):
        # Add code to run tests and visualize results
        pass

    def generate_data(self):
        # Add code to generate and inspect data
        pass
    
    def choose_dataset(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "All Files (*);;Python Files (*.py)", options=options)
        if file_name:
            self.dataset_label.setText(file_name)

    def browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Browse", "", "All Files (*)")
        if file_name:
            self.datast_path = file_name
            base_name = os.path.basename(file_name)
            self.file_drag_drop.setText(base_name)

    def file_dropped(self, file_name):
        if file_name:
            self.datast_path = file_name
            base_name = os.path.basename(file_name)
            self.file_drag_drop.setText(base_name)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.setGeometry(100, 100, 1200, 800)
    window.show()
    sys.exit(app.exec())