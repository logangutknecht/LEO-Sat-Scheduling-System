import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backend_bases import MouseButton

# Import the necessary functions and constants from the existing code
from Tasking_System import visualize_satellite_tasking, simulate_satellite_tasking, ORBITAL_PERIOD

class SatelliteVisualizationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Satellite Visualization')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # Create the Matplotlib figure and canvas
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.mpl_connect('button_press_event', self.on_map_click)
        layout.addWidget(self.canvas)

        # Create input fields for latitude and longitude
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel('Latitude:'))
        self.lat_input = QLineEdit()
        input_layout.addWidget(self.lat_input)
        input_layout.addWidget(QLabel('Longitude:'))
        self.lon_input = QLineEdit()
        input_layout.addWidget(self.lon_input)
        add_button = QPushButton('Add GPS Point')
        add_button.clicked.connect(self.add_gps_point)
        input_layout.addWidget(add_button)
        layout.addLayout(input_layout)

        # Create a start simulation button
        start_button = QPushButton('Start Simulation')
        start_button.clicked.connect(self.start_simulation)
        layout.addWidget(start_button)

        self.setLayout(layout)

        # Initialize the command GPS points
        self.commands = []
        self.visualize_satellite()

    def visualize_satellite(self):
        # Clear the previous plot
        self.figure.clear()

        # Call the visualize_satellite_tasking function with the updated commands
        visualize_satellite_tasking(self.commands, speed_factor=10, figure=self.figure)

        # Refresh the canvas
        self.canvas.draw()

    def add_gps_point(self):
        try:
            lat = float(self.lat_input.text())
            lon = float(self.lon_input.text())
            self.commands.append((lat, lon))
            self.lat_input.clear()
            self.lon_input.clear()
            self.visualize_satellite()
        except ValueError:
            print("Invalid latitude or longitude input.")

    def on_map_click(self, event):
        if event.button == MouseButton.LEFT:
            lon, lat = event.xdata, event.ydata
            self.commands.append((lat, lon))
            self.visualize_satellite()

    def start_simulation(self):
        # Generate initial command GPS points
        self.commands = simulate_satellite_tasking(10)
        self.visualize_satellite()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SatelliteVisualizationApp()
    window.show()
    sys.exit(app.exec_())