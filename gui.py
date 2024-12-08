import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                            QWidget, QFileDialog, QLabel, QTextEdit, QHBoxLayout,
                            QSplashScreen, QProgressBar)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QColor, QPainter, QFont
# import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from counter import WordCounter

class SplashScreen(QSplashScreen):
    def __init__(self):
        # Create a pixmap with proper dimensions
        width = 600
        height = 300
        splash_pix = QPixmap(width, height)
        splash_pix.fill(QColor("#2C3E50"))  # Fill the entire pixmap first
        
        # Start painting
        painter = QPainter(splash_pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # Enable antialiasing
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)  # Enable text antialiasing
        
        # Add welcome message
        welcome_font = QFont("Arial", 24)
        welcome_font.setBold(True)
        painter.setFont(welcome_font)
        painter.setPen(QColor("#3498DB"))  # Light blue color for welcome message
        welcome_rect = painter.drawText(0, 20, width, 40, Qt.AlignmentFlag.AlignCenter, "Welcome to")
        
        # Add title with a modern font
        title_font = QFont("Arial", 48)
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.setPen(QColor("#FFFFFF"))  # Explicit white color
        title_rect = painter.drawText(0, 60, width, 100, Qt.AlignmentFlag.AlignCenter, "Word Frequency Analyzer")
        
        # Add loading text
        loading_font = QFont("Arial", 20)
        loading_font.setBold(True)
        painter.setFont(loading_font)
        loading_rect = painter.drawText(0, 160, width, 40, Qt.AlignmentFlag.AlignCenter, "Loading...")
        
        # Finish painting
        painter.end()
        
        # Initialize splash screen with the painted pixmap
        super().__init__(splash_pix, Qt.WindowType.WindowStaysOnTopHint)
        
        # Add progress bar with a clean style
        progress_width = int(width * 0.8)  # 80% of splash width
        progress_height = 25
        progress_x = (width - progress_width) // 2
        progress_y = 210
        
        self.progress = QProgressBar(self)
        self.progress.setGeometry(progress_x, progress_y, progress_width, progress_height)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 12px;
                text-align: center;
                background-color: rgba(52, 73, 94, 0.5);
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #3498DB;
                border-radius: 12px;
            }
        """)

    def update_progress(self, value, message="Loading..."):
        self.progress.setValue(value)
        # Draw the message with proper font and color
        self.showMessage(message, 
                        Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, 
                        QColor("#FFFFFF"))

# Lazy imports - these will only be imported when needed
def load_analysis_libraries():
    global pd, sns, plt, FigureCanvas
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    return pd, sns, plt, FigureCanvas

class WordFrequencyAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Word Frequency Analyzer")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize word counter
        self.word_counter = WordCounter()

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Create horizontal layout for buttons
        button_layout = QHBoxLayout()
        
        # Add file selection button
        self.select_button = QPushButton("Select CSV File")
        self.select_button.clicked.connect(self.select_file)
        button_layout.addWidget(self.select_button)
        
        # Add save figure button
        self.save_button = QPushButton("Save Graph")
        self.save_button.clicked.connect(self.save_figure)
        self.save_button.setEnabled(False)  # Disable until we have a graph
        button_layout.addWidget(self.save_button)
        
        # Add button layout to main layout
        layout.addLayout(button_layout)

        # Add status label
        self.status_label = QLabel("Please select a CSV file")
        layout.addWidget(self.status_label)

        # Add matplotlib figure
        self.figure, self.ax = plt.subplots(figsize=(10, 5))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Add text area for word frequencies
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

    def select_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        if filename:
            self.analyze_file(filename)

    def save_figure(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Graph",
            "",
            "PNG Files (*.png);;All Files (*)"
        )
        if filename:
            if not filename.endswith('.png'):
                filename += '.png'
            self.figure.savefig(filename, dpi=300, bbox_inches='tight')
            self.status_label.setText(f"Graph saved as: {filename}")

    def analyze_file(self, filename):
        try:
            # Process file using WordCounter
            df_plot, most_common = self.word_counter.load_file(filename)
            
            # Clear previous plot
            self.ax.clear()
            
            # Create bar plot
            sns.barplot(data=df_plot, x='Word', y='Frequency', color='skyblue', ax=self.ax)
            
            # Add value labels on top of each bar
            for i, v in enumerate(df_plot['Frequency']):
                self.ax.text(i, v, str(v), ha='center', va='bottom')
            
            # Customize the plot
            self.ax.set_title('Top 20 Most Frequent Words in Tweets', pad=20)
            self.ax.set_xticklabels(self.ax.get_xticklabels(), rotation=45, ha='right')
            self.ax.set_xlabel('Words')
            self.ax.set_ylabel('Frequency')
            
            # Adjust layout
            self.figure.tight_layout()
            
            # Update canvas
            self.canvas.draw()
            
            # Update text area with frequencies
            self.text_area.clear()
            self.text_area.append("Top 100 most frequent words:\n")
            self.text_area.append("Word : Frequency\n")
            self.text_area.append("-" * 20 + "\n")
            for i, (word, freq) in enumerate(most_common, 1):
                self.text_area.append(f"{i}. {word}: {freq}\n")
            
            # Enable save button now that we have a graph
            self.save_button.setEnabled(True)
            
            self.status_label.setText(f"Analysis complete: {filename}")
            
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            print(f"Error: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Create and show splash screen
    splash = SplashScreen()
    splash.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
    splash.show()
    app.processEvents()  # Force the splash screen to be shown immediately
    
    # Move splash screen to center of screen
    screen = app.primaryScreen().geometry()
    splash_geometry = splash.geometry()
    splash.move(
        (screen.width() - splash_geometry.width()) // 2,
        (screen.height() - splash_geometry.height()) // 2
    )
    
    # Create main window but don't show it yet
    window = WordFrequencyAnalyzer()
    
    # Simulate loading steps
    def load_step(step):
        steps = {
            0: ("Initializing application...", 20),
            1: ("Loading core components...", 40),
            2: ("Preparing user interface...", 60),
            3: ("Finalizing...", 80),
            4: ("Ready!", 100)
        }
        
        if step < len(steps):
            message, progress = steps[step]
            splash.update_progress(progress, message)
            app.processEvents()  # Ensure the progress is displayed
            QTimer.singleShot(500, lambda: load_step(step + 1))
        else:
            window.show()
            splash.finish(window)
    
    # Start loading sequence
    QTimer.singleShot(100, lambda: load_step(0))
    
    sys.exit(app.exec())
