import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton, QLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Genetic Algorithm for Subset Sum Problem")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.create_tabs()

        # Apply custom stylesheet
        self.setStyleSheet("""
            /* Tab bar */
            QTabBar::tab {
                background-color: #3498db;
                color: white;
                padding: 8px;
            }
            
            QTabBar::tab:selected {
                background-color: #2980b9;
            }
            
            /* Buttons */
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 3px;
            }
            
            QPushButton:hover {
                background-color: #27ae60;
            }
            
            /* Labels */
            QLabel {
                color: #34495e;
            }
        """)

    def create_tabs(self):
        self.tab1 = QWidget()
        self.tab_widget.addTab(self.tab1, "Run Tests and Visualize")
        self.tab1_layout = QVBoxLayout(self.tab1)
        self.run_tests_button = QPushButton("Run Tests")
        self.run_tests_button.clicked.connect(self.run_tests)
        self.tab1_layout.addWidget(self.run_tests_button)

        self.tab2 = QWidget()
        self.tab_widget.addTab(self.tab2, "Generate Data/Inspect Data")
        self.tab2_layout = QVBoxLayout(self.tab2)
        self.generate_data_button = QPushButton("Generate Data")
        self.generate_data_button.clicked.connect(self.generate_data)
        self.tab2_layout.addWidget(self.generate_data_button)

        self.tab3 = QWidget()
        self.tab_widget.addTab(self.tab3, "About the Project")
        self.tab3_layout = QVBoxLayout(self.tab3)
        self.about_label = QLabel("This is a project about...")
        self.tab3_layout.addWidget(self.about_label)

    def run_tests(self):
        # Add code to run tests and visualize results
        pass

    def generate_data(self):
        # Add code to generate and inspect data
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setGeometry(100, 100, 800, 600)
    window.show()
    sys.exit(app.exec_())
