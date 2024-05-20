import sys
import os
import subprocess
import time
from PyQt6.QtWidgets import QTabWidget, QStatusBar, QScrollArea, QMessageBox, QComboBox, QTabBar, QTabWidget, QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QTextBrowser, QHBoxLayout, QSlider
from PyQt6.QtCore import QThread, QRect, QPropertyAnimation, pyqtProperty, Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QTextCursor, QDesktopServices, QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import seaborn as sns

class Solution:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.TN = 0
        self.FP = 0
        self.FN = 0
        self.TP = 0
        self.run_times = []
        self.n_values = []

solutions = []
dataset_path = "data/positive"
in_files = []
out_files = []

class Worker(QThread):
    data_ready = pyqtSignal(int, int, float)  # signal to emit n and run_time

    def __init__(self, solution, parent=None):
        super().__init__(parent)
        self.solution = solution

    def run(self):
        i = 0
        # Iterate over all files in the directory
        for file_path in in_files:
            i += 1
            with open(file_path, 'r') as file:
                n = int(file.readline().strip())

            # Run the script and measure the time taken
            start_time = time.process_time()
            subprocess.run(["python", self.solution.path], stdin=open(file_path, 'r'))
            end_time = time.process_time()

            # Calculate and store the run time
            run_time = end_time - start_time

            self.solution.run_times.append(run_time)
            self.solution.n_values.append(n)

            self.data_ready.emit(i, n, run_time)

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

class MPLWidget2(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.canvas)

class GraphsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.graphs = {"Accuracy": None, "Fitness": None, "F1": None, "Time": None}
        self.tab_widget = QTabWidget()

        # Create a layout and add the tab widget to it
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.tab_widget)
        # Create a status bar
        #self.status_bar = QStatusBar()
        #self.layout.addWidget(self.status_bar)

        # Add labels to the status bar
        #self.status_bar.showMessage("Accuracy: 0, F1-Score: 0, Time: 0, Fitness: 0")

        sns.set_theme()
        # Add four graphs
        self.add_graph("Accuracy")
        self.add_graph("Fitness")
        self.add_graph("F1-Score")
        self.add_graph("Time")

    def add_graph(self, graph_title):
        # Create a new figure and canvas for the graph
        figure = Figure(figsize=(5, 4), dpi=100)
        canvas = FigureCanvas(figure)
        self.graphs[graph_title] = canvas

        # Add the canvas to a new tab in the tab widget
        self.tab_widget.addTab(canvas, graph_title)
        canvas.figure.clear()
        ax = canvas.figure.add_subplot(111)
        #ax.legend()
        ax.set_xlabel('n')
        ax.set_ylabel(graph_title)
        

        canvas.draw()

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

        self.top_layout = QVBoxLayout()
        self.layout.addLayout(self.top_layout)

        self.bottom_layout = QVBoxLayout()
        self.layout.addLayout(self.bottom_layout)
        self.plus_button = QPushButton("+")
        self.plus_button.clicked.connect(self.add_combo_box)
        self.bottom_layout.addWidget(self.plus_button)
        self.bottom_layout.setAlignment(self.plus_button, Qt.AlignmentFlag.AlignCenter)

    def add_combo_box(self):
        combo_box_widget = ComboBoxWidget()
        combo_box_widget.delete_button.setStyleSheet("background-color: transparent")
        self.top_layout.addWidget(combo_box_widget)

    def get_algorithm_names(self):
        algorithm_names = []
        for i in range(self.top_layout.count()):
            combo_box_widget = self.top_layout.itemAt(i).widget()
            combo_box = combo_box_widget.combo_box
            algorithm_names.append(combo_box.currentText())
        return algorithm_names
    
class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Project of Evolutionary Algorithm for Subset Sum Problem")
        self.layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabBar(AnimatedTabBar())
        self.layout.addWidget(self.tab_widget)
        # Graphs
        self.time_graph = None
        self.graphs = {"Accuracy": None, "Fitness": None, "F1": None, "Time": None}
        
        # Create tabs
        self.tab1_init()
        #self.tab2_init()
        self.tab3_init()

        with open('styles.qss', 'r') as f:
            self.setStyleSheet(f.read())

    def tab1_init(self):
        self.tab1 = QWidget()
        self.tab_widget.addTab(self.tab1, "Run Tests")

        self.main_layout = QHBoxLayout(self.tab1)
        self.graphs_widget = GraphsWidget()
        self.main_layout.addWidget(self.graphs_widget)

        self.right_layout = QVBoxLayout()

        self.right_widget = QWidget()
        self.right_widget.setFixedWidth(400)
        self.right_widget.setLayout(self.right_layout)

        self.choose_dataset_label = QLabel("Choose dataset")
        self.choose_dataset_label.setObjectName("choose_dataset_label")
        self.right_layout.addWidget(self.choose_dataset_label)

        self.file_drag_drop = FileDragDrop("")
        self.file_drag_drop.setObjectName("file_drag_drop")
        self.file_drag_drop.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_drag_drop.fileDropped.connect(self.file_dropped)
        self.right_layout.addWidget(self.file_drag_drop)

        self.drag_drop_layout = QVBoxLayout()
        self.drag_drop_label = QLabel("Drag and drop directory here")
        self.drag_drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drag_drop_layout.addWidget(self.drag_drop_label)

        self.browse_layout = QHBoxLayout()
        self.browse_button = QPushButton("Browse")
        self.browse_button.setObjectName("browse_button")
        self.browse_button.clicked.connect(self.browse_file)
        self.browse_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.browse_layout.addWidget(self.browse_button)

        self.drag_drop_layout.addLayout(self.browse_layout)
        self.file_drag_drop.setLayout(self.drag_drop_layout)

        self.add_solutions_label = QLabel("Add solutions")
        self.add_solutions_label.setObjectName("add_solutions_label")
        self.right_layout.addWidget(self.add_solutions_label)
        self.algorithm_combo_widget = AlgorithmSelectionWidget()
        self.right_layout.addWidget(self.algorithm_combo_widget)

        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_tests)
        self.right_layout.addWidget(self.run_button)

        self.main_layout.addWidget(self.right_widget)
        
    def tab2_init(self):
        self.tab2 = QWidget()
        self.tab_widget.addTab(self.tab2, "Generate Data")
        self.tab2_layout = QHBoxLayout(self.tab2)
        # Add MPLWidget to the left side of the layout
        self.graph = MPLWidget2()
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

    def tab3_init(self):
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

    def create_solutions(self):
        for solution_name in self.algorithm_combo_widget.get_algorithm_names():
            solution_path = ""
            if solution_name == "naive":
                solution_path = "naive.py"
            elif solution_name == "genetic programming":
                solution_path = "genetic_programming.py"
            elif solution_name == "evolutionary programming":
                solution_path = "evolutionary_programming.py"
            solution = Solution(solution_name, solution_path)
            solutions.append(solution)

    def locate_files(self):
        for filepath in os.listdir(dataset_path):
            fullpath = os.path.join(dataset_path, filepath)
            if fullpath.endswith(".in"):
                in_files.append(fullpath)
            elif fullpath.endswith(".out"):
                out_files.append(fullpath)

    def run_tests(self):
        self.locate_files()
        self.create_solutions()
       
        self.workers = []
        for solution in solutions:
            worker = Worker(solution)
            worker.data_ready.connect(self.update_graph)
            worker.finished.connect(self.worker_finished)
            self.workers.append(worker)

        for worker in self.workers:
            worker.start()

    def worker_finished(self):
        QMessageBox.information(self, "Info", "All tests have been run")      

    def update_graph(self, i, n, run_time):
        graph = self.graphs_widget.graphs["Time"]
        graph.figure.clear()

        # Create a new axes on this figure
        ax = graph.figure.add_subplot(111)

        for solution in solutions:
            #ax.plot(solution.n_values, solution.run_times)
            ax.scatter(solution.n_values, solution.run_times, label=solution.name)

        ax.legend()
        ax.set_xlabel('n')
        ax.set_ylabel('Run Time (seconds)')

        # Redraw the canvas (this is equivalent to plt.show() in interactive mode)
        graph.draw()

    def generate_data(self):
        # Add code to generate and inspect data
        pass
    
    def choose_dataset(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        directory_name = QFileDialog.getExistingDirectory(self, "Select a directory", "", options=options)
        if directory_name:
            self.dataset_label.setText(directory_name)

    def browse_file(self):
        directory_name = QFileDialog.getExistingDirectory(self, "Browse", "")
        if directory_name:
            dataset_path = directory_name
            base_name = os.path.basename(directory_name)
            self.file_drag_drop.setText(base_name)

    def file_dropped(self, directory_name):
        if directory_name:
            dataset_path = directory_name
            base_name = os.path.basename(directory_name)
            self.file_drag_drop.setText(base_name)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("AI App")  # Set the application name
    app.setWindowIcon(QIcon("other/rick.gif"))
    #app.setWindowIcon(QIcon("other/patrick.png")) 
    #app.setWindowIcon(QIcon("other/ryan.jpg")) 
    window = MainWindow()
    window.setGeometry(100, 100, 1200, 800)
    #window.show()
    window.showFullScreen()
    sys.exit(app.exec())