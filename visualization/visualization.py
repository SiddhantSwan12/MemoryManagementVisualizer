from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QPainterPath
from PyQt6.QtCore import Qt, QRectF
import config

class MemoryVisualization(QWidget):
    def __init__(self, memory_manager):
        super().__init__()
        self.memory_manager = memory_manager
        self.setMinimumSize(config.MEMORY_RECT_WIDTH + 100, config.MEMORY_RECT_HEIGHT + 200)
        self.usage_history = []

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.draw_memory_blocks(painter)
        self.draw_usage_history(painter)

    def draw_memory_blocks(self, painter):
        blocks = self.memory_manager.get_blocks()
        total_memory = self.memory_manager.total_size
        
        for block in blocks:
            x = config.MEMORY_RECT_X + (block.start / total_memory) * config.MEMORY_RECT_WIDTH
            width = (block.size / total_memory) * config.MEMORY_RECT_WIDTH
            
            if block.is_free:
                color = QColor(config.COLOR_FREE_MEMORY)
            else:
                # Use a hash of the process_id to generate a unique color
                color = QColor(hash(block.process_id) % 256, hash(block.process_id * 2) % 256, hash(block.process_id * 3) % 256)
            
            painter.fillRect(QRectF(x, config.MEMORY_RECT_Y, width, config.MEMORY_RECT_HEIGHT), color)
            
            # Draw block size and process id text
            painter.setPen(QColor(config.COLOR_TEXT))
            painter.setFont(QFont("Arial", 8))
            size_text = f"{block.size}MB"
            if not block.is_free:
                size_text += f"\nPID: {block.process_id}"
            painter.drawText(QRectF(x, config.MEMORY_RECT_Y, width, config.MEMORY_RECT_HEIGHT), 
                             Qt.AlignmentFlag.AlignCenter, size_text)

    def draw_usage_history(self, painter):
        if not self.usage_history:
            return

        painter.setPen(QPen(Qt.GlobalColor.red, 2))
        
        chart_width = config.MEMORY_RECT_WIDTH
        chart_height = 100
        chart_x = config.MEMORY_RECT_X
        chart_y = config.MEMORY_RECT_Y + config.MEMORY_RECT_HEIGHT + 20

        # Draw axes
        painter.drawLine(chart_x, chart_y + chart_height, chart_x + chart_width, chart_y + chart_height)
        painter.drawLine(chart_x, chart_y, chart_x, chart_y + chart_height)

        # Create QPainterPath for the history line
        path = QPainterPath()

        # Draw usage history
        max_points = 100
        step = max(1, len(self.usage_history) // max_points)
        points = self.usage_history[-max_points*step::step]
        
        for i, usage in enumerate(points):
            x = chart_x + (i / len(points)) * chart_width
            y = chart_y + chart_height - (usage / 100) * chart_height
            if i == 0:
                path.moveTo(x, y)  # Use moveTo on the path
            else:
                path.lineTo(x, y)  # Use lineTo on the path

        # Draw the path
        painter.drawPath(path)

    def update_blocks(self):
        self.repaint()

    def update_graph(self):
        allocated_memory = sum(block.size for block in self.memory_manager.get_blocks() if not block.is_free)
        usage_percentage = (allocated_memory / self.memory_manager.total_size) * 100
        self.usage_history.append(usage_percentage)
        
        # Keep only the last 1000 points
        self.usage_history = self.usage_history[-1000:]
        
        self.repaint()
