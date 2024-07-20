import pyqtgraph as pg
from PyQt5.QtGui import QPainter, QPicture
from PyQt5.QtCore import QRectF, QPointF, Qt


class ExecutedOrderItems(pg.GraphicsObject):
    """
        This graphics object draws all elements showing an order from placement until execution.
        The vertical line shows, how far ithe order went from the price of placement until execution.
        And the horizontal line, shows when it was placed and when it was executed.
        Sell side is red and buy side is green.
    """
    def __init__(self, data):
        pg.GraphicsObject.__init__(self)
        self.data = data
        self.generatePicture()

    def generatePicture(self):
        """Generates the executed order elements."""
        self.picture = QPicture()
        p = QPainter(self.picture)

        for (side, ts, start_price, exec_time, price) in self.data:
            if side == "sell":
                p.setPen(pg.mkPen(width=2, color='r'))  # red fill for bearish
            else:
                p.setPen(pg.mkPen(width=2, color='g'))  # green fill for bullish
            p.drawLine(QPointF(ts, start_price), QPointF(ts, price))
            if side == "sell":
                p.setPen(pg.mkPen(width=2, color='r', style=Qt.DashLine))  # red fill for bearish
            else:
                p.setPen(pg.mkPen(width=2, color='g', style=Qt.DashLine))  # green fill for bullish
            p.drawLine(QPointF(ts, price), QPointF(exec_time, price))
        p.end()

    def paint(self, painter, option, widget):
        painter.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QRectF(self.picture.boundingRect())


class CandlestickItems(pg.GraphicsObject):
    """Draws all candle sticks defined by the intpu \a data."""
    def __init__(self, data):
        pg.GraphicsObject.__init__(self)
        self.data = data
        self.generatePicture()

    def generatePicture(self):
        """Generates all candle stick elements."""
        self.picture = QPicture()
        p = QPainter(self.picture)
        p.setPen(pg.mkPen('w'))  # white pen for outlines

        for (t, open, high, low, close) in self.data:
            p.drawLine(QPointF(t, low), QPointF(t, high))
            if open > close:
                p.setBrush(pg.mkBrush('r'))  # red fill for bearish
            else:
                p.setBrush(pg.mkBrush('g'))  # green fill for bullish
            p.drawRect(QRectF(t - 10, open, 20, close - open))
        p.end()

    def paint(self, painter, option, widget):
        painter.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QRectF(self.picture.boundingRect())
