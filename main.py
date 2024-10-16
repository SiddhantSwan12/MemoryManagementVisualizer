import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, 
                             QLineEdit, QLabel, QComboBox, QInputDialog, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from memory_manager.memory import MemoryManager
from visualization.visualization import MemoryVisualization
from utils.metrics import MetricsTracker
import config
import json

class MemoryVisualizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Memory Management Visualizer")
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        self.memory_manager = MemoryManager(config.MEMORY_SIZE)
        self.metrics_tracker = MetricsTracker(self.memory_manager)

        self.init_ui()

        # Timer for continuous updates (30 FPS)
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_visualization)
        self.update_timer.start(1000 // 30)  # 30 FPS

        # Timer for graph updates (every 10 seconds)
        self.graph_timer = QTimer(self)
        self.graph_timer.timeout.connect(self.update_graph)
        self.graph_timer.start(10000)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.memory_vis = MemoryVisualization(self.memory_manager)
        main_layout.addWidget(self.memory_vis)

        controls_layout = QHBoxLayout()

        self.size_input = QLineEdit()
        self.size_input.setPlaceholderText("Allocation size (MB)")
        controls_layout.addWidget(self.size_input)

        self.process_id_input = QLineEdit()
        self.process_id_input.setPlaceholderText("Process ID")
        controls_layout.addWidget(self.process_id_input)

        allocate_button = QPushButton("Allocate")
        allocate_button.clicked.connect(self.handle_allocation)
        controls_layout.addWidget(allocate_button)

        deallocate_button = QPushButton("Deallocate")
        deallocate_button.clicked.connect(self.handle_deallocation)
        controls_layout.addWidget(deallocate_button)

        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["First Fit", "Best Fit", "Worst Fit", "Next Fit"])
        self.algorithm_combo.currentTextChanged.connect(self.handle_algorithm_change)
        controls_layout.addWidget(self.algorithm_combo)

        # Page Replacement Algorithm
        self.page_algorithm_combo = QComboBox()
        self.page_algorithm_combo.addItems(["None", "FIFO", "LRU", "LFU"])
        self.page_algorithm_combo.currentTextChanged.connect(self.handle_page_algorithm_change)
        controls_layout.addWidget(self.page_algorithm_combo)

        compact_button = QPushButton("Compact Memory")
        compact_button.clicked.connect(self.handle_compaction)
        controls_layout.addWidget(compact_button)

        simulate_button = QPushButton("Simulate Allocations")
        simulate_button.clicked.connect(self.handle_simulation)
        controls_layout.addWidget(simulate_button)

        save_button = QPushButton("Save State")
        save_button.clicked.connect(self.save_state)
        controls_layout.addWidget(save_button)

        load_button = QPushButton("Load State")
        load_button.clicked.connect(self.load_state)
        controls_layout.addWidget(load_button)

        main_layout.addLayout(controls_layout)

        self.metrics_label = QLabel()
        main_layout.addWidget(self.metrics_label)

    def update_visualization(self):
        self.memory_vis.update_blocks()
        self.update_metrics()

    def update_graph(self):
        self.memory_vis.update_graph()

    def handle_allocation(self):
        try:
            size = int(self.size_input.text())
            process_id = int(self.process_id_input.text())
            start = self.memory_manager.allocate(size, process_id)
            if start is not None:
                self.show_message(f"Allocated {size}MB for process {process_id} at position {start}")
            else:
                self.show_message("Allocation failed: Not enough memory", QMessageBox.Icon.Warning)
        except ValueError:
            self.show_message("Invalid input. Please enter numbers for size and process ID.", QMessageBox.Icon.Warning)
        self.size_input.clear()
        self.process_id_input.clear()

    def handle_deallocation(self):
        start, ok = QInputDialog.getInt(self, "Deallocate Memory", "Enter start position to deallocate:")
        if ok:
            if self.memory_manager.deallocate(start):
                self.show_message(f"Deallocated memory at position {start}")
            else:
                self.show_message("Deallocation failed: Invalid start position", QMessageBox.Icon.Warning)

    def handle_algorithm_change(self, algorithm):
        self.memory_manager.set_algorithm(algorithm)
        self.show_message(f"Allocation algorithm changed to {algorithm}")

    def handle_page_algorithm_change(self, algorithm):
        self.memory_manager.set_page_replacement_algorithm(algorithm)
        self.show_message(f"Page replacement algorithm changed to {algorithm}")

    def handle_compaction(self):
        self.memory_manager.compact_memory()
        self.show_message("Memory compacted")

    def handle_simulation(self):
        num_allocations, ok1 = QInputDialog.getInt(self, "Simulate Allocations", "Number of allocations:", 10, 1, 1000)
        if ok1:
            min_size, ok2 = QInputDialog.getInt(self, "Simulate Allocations", "Minimum allocation size (MB):", 1, 1, 100)
            if ok2:
                max_size, ok3 = QInputDialog.getInt(self, "Simulate Allocations", "Maximum allocation size (MB):", 10, min_size, 1000)
                if ok3:
                    self.memory_manager.simulate_allocations(num_allocations, min_size, max_size)
                    self.show_message(f"Simulated {num_allocations} allocations")

    def save_state(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Memory State", "", "JSON Files (*.json)")
        if filename:
            state = self.memory_manager.get_memory_state()
            with open(filename, 'w') as f:
                json.dump(state, f)
            self.show_message(f"Memory state saved to {filename}")

    def load_state(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load Memory State", "", "JSON Files (*.json)")
        if filename:
            with open(filename, 'r') as f:
                state = json.load(f)
            self.memory_manager.set_memory_state(state)
            self.show_message(f"Memory state loaded from {filename}")

    def update_visualization(self):
        self.memory_vis.update()
        self.update_metrics()

    def update_metrics(self):
        self.metrics_tracker.update()
        metrics_text = f"""
        Current Algorithm: {self.memory_manager.algorithm}
        Page Replacement Algorithm: {self.memory_manager.page_replacement_algorithm}
        Allocated Memory: {self.metrics_tracker.get_allocation_percentage():.2f}%
        Fragmentation Ratio: {self.memory_manager.get_fragmentation_ratio():.2f}
        Allocation Success Rate: {self.memory_manager.get_allocation_success_rate():.2f}
        Average Allocation Time: {self.memory_manager.get_average_allocation_time():.6f} seconds
        Compactions Performed: {self.memory_manager.compaction_count}
        """
        self.metrics_label.setText(metrics_text)

    def show_message(self, message, icon=QMessageBox.Icon.Information):
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setText(message)
        msg_box.setWindowTitle("Memory Management Visualizer")
        msg_box.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MemoryVisualizerApp()
    window.show()
    sys.exit(app.exec())