import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                            QWidget, QFileDialog, QLabel, QTextEdit, QHBoxLayout)
from PyQt6.QtCore import Qt
# import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from counter import WordCounter

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
    window = WordFrequencyAnalyzer()
    window.show()
    sys.exit(app.exec())
