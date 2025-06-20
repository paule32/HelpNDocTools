class GridGraphicsViewFormDesigner(QGraphicsView):
    def __init__(self, scene, window_size):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        # Setze die Größe der Szene auf das Doppelte der Fenstergröße
        scene.setSceneRect(0, 0, window_size.width() * 2, window_size.height() * 2)
        self.selected_item   = None  # Aktuell ausgewähltes Element
        self.resize_mode     = None  # Speichert den aktiven Ziehpunkt
        self.last_resize_pos = None  # Speichert die letzte Position für die 10-Pixel-Schritte
        self.window_size     = window_size  # Speichert die Fenstergröße, um die Mausbewegung zu begrenzen
    
    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        # Gitterabstand und Punktgröße festlegen
        grid_size  = 10  # Abstand zwischen den Punkten
        point_size =  2  # Punktgröße: 2x2 Pixel

        # Pinsel und Farbe für das Gitter definieren
        pen = QPen(QColor(200, 200, 200))  # Farbe der Punkte
        painter.setPen(pen)
        brush = QBrush(QColor(200, 200, 200))  # Füllfarbe der Punkte
        painter.setBrush(brush)

        # Start- und Endkoordinaten des sichtbaren Bereichs bestimmen
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)

        # Punkt-Gitter zeichnen als 2x2 Pixel Rechtecke
        for x in range(left, int(rect.right()), grid_size):
            for y in range(top, int(rect.bottom()), grid_size):
                painter.drawRect(x, y, point_size, point_size)
    
    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)
        
        if self.selected_item:
            pen = QPen(QColor("red"), 4, Qt.DashLine)
            painter.setPen(pen)
            item_rect = self.selected_item.sceneBoundingRect()
            painter.drawRect(item_rect)

            # Füllfarbe und Größe für die Ziehpunkte festlegen
            painter.setBrush(QBrush(QColor("red")))
            rect_size = 12

            # Berechne und zeichne die Positionen der Ziehpunkte auf jeder Seite
            for point in self.calculate_resize_handles(item_rect):
                painter.drawRect(int(point.x() - rect_size / 2), int(point.y() - rect_size / 2), rect_size, rect_size)

    def calculate_resize_handles(self, item_rect):
        """Berechnet die Positionen der Ziehpunkte an den Seiten des Rahmens."""
        left_center   = QPointF(item_rect.left ()     , item_rect.center().y())
        right_center  = QPointF(item_rect.right()     , item_rect.center().y())
        top_center    = QPointF(item_rect.center().x(), item_rect.top())
        bottom_center = QPointF(item_rect.center().x(), item_rect.bottom())
        return [left_center, right_center, top_center, bottom_center]

    def mousePressEvent(self, event):
        # Bestimme das ausgewählte Element und speichere es
        item = self.itemAt(event.pos())
        if isinstance(item, QGraphicsItem):
            self.selected_item = item
            self.last_resize_pos = self.mapToScene(event.pos())  # Setze die Ausgangsposition
        else:
            self.selected_item   = None
            self.last_resize_pos = None
        
        # Prüfe, ob ein Ziehpunkt angeklickt wurde
        pos = self.mapToScene(event.pos())
        item_rect = self.selected_item.sceneBoundingRect() if self.selected_item else None
        handles = self.calculate_resize_handles(item_rect) if item_rect else []

        # Zuordnung der Ziehpunkte zu den Seiten mit einem Toleranzbereich von 10 Pixel
        if self.selected_item and self.is_near_point(pos, handles[0], threshold=10):
            self.resize_mode = 'left'
        elif self.selected_item and self.is_near_point(pos, handles[1], threshold=10):
            self.resize_mode = 'right'
        elif self.selected_item and self.is_near_point(pos, handles[2], threshold=10):
            self.resize_mode = 'top'
        elif self.selected_item and self.is_near_point(pos, handles[3], threshold=10):
            self.resize_mode = 'bottom'
        else:
            self.resize_mode = None  # Keine Ziehpunkte ausgewählt

        self.viewport().update()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # Begrenze die Mausbewegung auf die Fenstergröße
        if event.pos().x() < 0 or event.pos().y() < 0 or event.pos().x() > self.window_size.width() or event.pos().y() > self.window_size.height():
            return

        if self.selected_item and self.resize_mode:
            pos = self.mapToScene(event.pos())
            delta = pos - self.last_resize_pos  # Berechne die Verschiebung seit dem letzten Schritt

            # Anpassung des Rechtecks in 10-Pixel-Schritten
            if self.resize_mode == 'left' and abs(delta.x()) >= 10:
                adjustment = 10 * (-1 if delta.x() > 0 else 1)
                new_width = max(10, self.selected_item.rect().width() + adjustment)
                self.selected_item.setRect(self.selected_item.rect().x() - adjustment, 
                                           self.selected_item.rect().y(), 
                                           new_width, 
                                           self.selected_item.rect().height())
                self.last_resize_pos = pos  # Aktualisiere die Position

            elif self.resize_mode == 'right' and abs(delta.x()) >= 10:
                adjustment = 10 * (1 if delta.x() > 0 else -1)
                new_width = max(10, self.selected_item.rect().width() + adjustment)
                self.selected_item.setRect(self.selected_item.rect().x(), 
                                           self.selected_item.rect().y(), 
                                           new_width, 
                                           self.selected_item.rect().height())
                self.last_resize_pos = pos  # Aktualisiere die Position

            elif self.resize_mode == 'top' and abs(delta.y()) >= 10:
                adjustment = 10 * (-1 if delta.y() > 0 else 1)
                new_height = max(10, self.selected_item.rect().height() + adjustment)
                self.selected_item.setRect(self.selected_item.rect().x(), 
                                           self.selected_item.rect().y() - adjustment, 
                                           self.selected_item.rect().width(), 
                                           new_height)
                self.last_resize_pos = pos  # Aktualisiere die Position

            elif self.resize_mode == 'bottom' and abs(delta.y()) >= 10:
                adjustment = 10 * (1 if delta.y() > 0 else -1)
                new_height = max(10, self.selected_item.rect().height() + adjustment)
                self.selected_item.setRect(self.selected_item.rect().x(), 
                                           self.selected_item.rect().y(), 
                                           self.selected_item.rect().width(), 
                                           new_height)
                self.last_resize_pos = pos  # Aktualisiere die Position

            self.viewport().update()
        elif self.selected_item:
            # Snap-Funktion beim Bewegen des Elements
            grid_size = 10
            new_pos = self.mapToScene(event.pos())
            snapped_x = round(new_pos.x() / grid_size) * grid_size
            snapped_y = round(new_pos.y() / grid_size) * grid_size

            # Verschieben der Szene, wenn sich das Element an den Rand nähert
            buffer_zone = 20  # Abstand zum Rand, um die Szene zu verschieben
            move_offset = 10  # Verschiebung der Szene in Pixeln
            if new_pos.x() > self.window_size.width() - buffer_zone:
                self.setSceneRect(self.sceneRect().adjusted(-move_offset, 0, move_offset, 0))
            elif new_pos.x() < buffer_zone:
                self.setSceneRect(self.sceneRect().adjusted(move_offset, 0, -move_offset, 0))
            if new_pos.y() > self.window_size.height() - buffer_zone:
                self.setSceneRect(self.sceneRect().adjusted(0, -move_offset, 0, move_offset))
            elif new_pos.y() < buffer_zone:
                self.setSceneRect(self.sceneRect().adjusted(0, move_offset, 0, -move_offset))

            self.selected_item.setPos(snapped_x, snapped_y)
            self.viewport().update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # Zurücksetzen des Resize-Modus nach dem Loslassen
        self.resize_mode = None
        super().mouseReleaseEvent(event)

    def is_near_point(self, pos, point, threshold=10):
        """Hilfsfunktion zur Überprüfung, ob die Position `pos` nahe an einem bestimmten Punkt `point` liegt."""
        return abs(pos.x() - point.x()) < threshold and abs(pos.y() - point.y()) < threshold

class DraggableComponentFormDesigner(QGraphicsRectItem):
    def __init__(self, name, x=0, y=0, width=50, height=50, view=None, label="", connections=[]):
        super().__init__(0, 0, width, height)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setPos(x, y)
        self.name = name
        self.label = label
        self.connections = connections  # Speichert relative Positionen der Verankerungen
        self.view = view
        self.last_snap_pos = QPointF(x, y)
        self.scroll_timer = QTimer()
        self.scroll_timer.setSingleShot(True)
        self.scroll_timer.timeout.connect(self.resume_movement)
        self.is_scrolling = False
        
    def resume_movement(self):
        self.is_scrolling = False
    
    def paint(self, painter, option, widget):
        # Hintergrundfarbe und Rahmen zeichnen
        painter.setBrush(QColor("skyblue"))
        painter.drawRect(self.rect())
        
        # Text im Zentrum des Bauteils zeichnen
        painter.setPen(QPen(Qt.black))
        painter.drawText(self.rect(), Qt.AlignCenter, self.label)

class GridGraphicsView(QGraphicsView):
    def __init__(self, scene, window_size):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        # Setze die Größe der Szene auf das Doppelte der Fenstergröße
        scene.setSceneRect(0, 0, window_size.width() * 2, window_size.height() * 2)
        self.selected_item = None  # Aktuell ausgewähltes Element
        self.resize_mode = None  # Speichert den aktiven Ziehpunkt
        self.last_resize_pos = None  # Speichert die letzte Position für die 10-Pixel-Schritte
    
    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        # Gitterabstand und Punktgröße festlegen
        grid_size  = 10  # Abstand zwischen den Punkten
        point_size =  2  # Punktgröße: 2x2 Pixel

        # Pinsel und Farbe für das Gitter definieren
        pen = QPen(QColor(200, 200, 200))  # Farbe der Punkte
        painter.setPen(pen)
        brush = QBrush(QColor(200, 200, 200))  # Füllfarbe der Punkte
        painter.setBrush(brush)

        # Start- und Endkoordinaten des sichtbaren Bereichs bestimmen
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)

        # Punkt-Gitter zeichnen als 2x2 Pixel Rechtecke
        for x in range(left, int(rect.right()), grid_size):
            for y in range(top, int(rect.bottom()), grid_size):
                painter.drawRect(x, y, point_size, point_size)
    
    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)
        
        if self.selected_item:
            pen = QPen(QColor("red"), 4, Qt.DashLine)
            painter.setPen(pen)
            item_rect = self.selected_item.sceneBoundingRect()
            painter.drawRect(item_rect)

            # Füllfarbe und Größe für die Ziehpunkte festlegen
            painter.setBrush(QBrush(QColor("red")))
            rect_size = 12

            # Berechne und zeichne die Positionen der Ziehpunkte auf jeder Seite
            for point in self.calculate_resize_handles(item_rect):
                painter.drawRect(int(point.x() - rect_size / 2), int(point.y() - rect_size / 2), rect_size, rect_size)

    def calculate_resize_handles(self, item_rect):
        """Berechnet die Positionen der Ziehpunkte an den Seiten des Rahmens."""
        left_center = QPointF(item_rect.left(), item_rect.center().y())
        right_center = QPointF(item_rect.right(), item_rect.center().y())
        top_center = QPointF(item_rect.center().x(), item_rect.top())
        bottom_center = QPointF(item_rect.center().x(), item_rect.bottom())
        return [left_center, right_center, top_center, bottom_center]

    def mousePressEvent(self, event):
        # Bestimme das ausgewählte Element und speichere es
        item = self.itemAt(event.pos())
        if isinstance(item, QGraphicsItem):
            self.selected_item = item
            self.last_resize_pos = self.mapToScene(event.pos())  # Setze die Ausgangsposition
        else:
            self.selected_item   = None
            self.last_resize_pos = None
        
        # Prüfe, ob ein Ziehpunkt angeklickt wurde
        pos = self.mapToScene(event.pos())
        item_rect = self.selected_item.sceneBoundingRect() if self.selected_item else None
        handles = self.calculate_resize_handles(item_rect) if item_rect else []

        # Zuordnung der Ziehpunkte zu den Seiten mit einem Toleranzbereich von 10 Pixel
        if self.selected_item and self.is_near_point(pos, handles[0], threshold=10):
            self.resize_mode = 'left'
        elif self.selected_item and self.is_near_point(pos, handles[1], threshold=10):
            self.resize_mode = 'right'
        elif self.selected_item and self.is_near_point(pos, handles[2], threshold=10):
            self.resize_mode = 'top'
        elif self.selected_item and self.is_near_point(pos, handles[3], threshold=10):
            self.resize_mode = 'bottom'
        else:
            self.resize_mode = None  # Keine Ziehpunkte ausgewählt

        self.viewport().update()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.selected_item and self.resize_mode:
            pos = self.mapToScene(event.pos())
            delta = pos - self.last_resize_pos  # Berechne die Verschiebung seit dem letzten Schritt

            # Anpassung des Rechtecks in 10-Pixel-Schritten
            if self.resize_mode == 'left' and abs(delta.x()) >= 10:
                adjustment = 10 * (-1 if delta.x() > 0 else 1)
                new_width = max(10, self.selected_item.rect().width() + adjustment)
                self.selected_item.setRect(self.selected_item.rect().x() - adjustment, 
                                           self.selected_item.rect().y(), 
                                           new_width, 
                                           self.selected_item.rect().height())
                self.last_resize_pos = pos  # Aktualisiere die Position

            elif self.resize_mode == 'right' and abs(delta.x()) >= 10:
                adjustment = 10 * (1 if delta.x() > 0 else -1)
                new_width = max(10, self.selected_item.rect().width() + adjustment)
                self.selected_item.setRect(self.selected_item.rect().x(), 
                                           self.selected_item.rect().y(), 
                                           new_width, 
                                           self.selected_item.rect().height())
                self.last_resize_pos = pos  # Aktualisiere die Position

            elif self.resize_mode == 'top' and abs(delta.y()) >= 10:
                adjustment = 10 * (-1 if delta.y() > 0 else 1)
                new_height = max(10, self.selected_item.rect().height() + adjustment)
                self.selected_item.setRect(self.selected_item.rect().x(), 
                                           self.selected_item.rect().y() - adjustment, 
                                           self.selected_item.rect().width(), 
                                           new_height)
                self.last_resize_pos = pos  # Aktualisiere die Position

            elif self.resize_mode == 'bottom' and abs(delta.y()) >= 10:
                adjustment = 10 * (1 if delta.y() > 0 else -1)
                new_height = max(10, self.selected_item.rect().height() + adjustment)
                self.selected_item.setRect(self.selected_item.rect().x(), 
                                           self.selected_item.rect().y(), 
                                           self.selected_item.rect().width(), 
                                           new_height)
                self.last_resize_pos = pos  # Aktualisiere die Position

            self.viewport().update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # Zurücksetzen des Resize-Modus nach dem Loslassen
        self.resize_mode = None
        super().mouseReleaseEvent(event)

    def is_near_point(self, pos, point, threshold=10):
        """Hilfsfunktion zur Überprüfung, ob die Position `pos` nahe an einem bestimmten Punkt `point` liegt."""
        return abs(pos.x() - point.x()) < threshold and abs(pos.y() - point.y()) < threshold

class DraggableComponent(QGraphicsRectItem):
    def __init__(self, name, x=0, y=0, width=50, height=50, view=None, label="", connections=[], resizable_horizontal=True):
        super().__init__(0, 0, width, height)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setPos(x, y)
        self.name = name
        self.label = label
        self.connections = connections
        self.view = view
        self.last_snap_pos = QPointF(x, y)
        self.scroll_timer = QTimer()
        self.scroll_timer.setSingleShot(True)
        self.scroll_timer.timeout.connect(self.resume_movement)
        self.is_scrolling = False
        self.resizable_horizontal = resizable_horizontal
        
        if self.resizable_horizontal == False:
            self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, False)
            self.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.setFlag(QGraphicsItem.ItemIsMovable, True)
        
    def paint(self, painter, option, widget):
        # Hintergrundfarbe und Rahmen zeichnen
        painter.setBrush(QColor("skyblue"))
        painter.drawRect(self.rect())
        
        # Text im Zentrum des Bauteils zeichnen
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        painter.setPen(Qt.black)
        text_rect = self.rect()
        painter.drawText(text_rect, Qt.AlignCenter, self.label)
        
        # Verankerungen relativ zur aktuellen Position zeichnen
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)
        for connection in self.connections:
            start_offset, end_offset = connection
            start_point = self.rect().topLeft() + start_offset
            end_point = self.rect().topLeft() + end_offset
            painter.drawLine(start_point, end_point)

            # Kreis an den Endpunkten der Linie zeichnen
            painter.setBrush(Qt.black)
            painter.drawEllipse(start_point, 2, 2)  # Startpunkt Kreis
            painter.drawEllipse(end_point, 2, 2)    # Endpunkt Kreis
    
    def mouseMoveEvent(self, event):
        if not self.is_scrolling:
            delta = event.scenePos() - self.last_snap_pos
            snapped_x, snapped_y = self.last_snap_pos.x(), self.last_snap_pos.y()

            if self.resizable_horizontal and abs(delta.x()) >= 10:
                snapped_x += 10 * (1 if delta.x() > 0 else -1)

            if abs(delta.y()) >= 10:
                snapped_y += 10 * (1 if delta.y() > 0 else -1)

            self.setPos(QPointF(snapped_x, snapped_y))
            self.last_snap_pos = QPointF(snapped_x, snapped_y)

            self.update()
            self.view.update()

            self.snap_based_scroll()
            self.restrict_cursor_within_window()
    
    def snap_based_scroll(self):
        view_rect = self.view.viewport().rect()
        scene_pos = self.view.mapFromScene(self.scenePos())
        width_threshold = self.rect().width() * 0.75
        height_threshold = self.rect().height() * 0.75
        scroll_step = 10

        if scene_pos.x() + width_threshold > view_rect.width():
            self.is_scrolling = True
            self.view.horizontalScrollBar().setValue(
                self.view.horizontalScrollBar().value() + scroll_step
            )
            self.scroll_timer.start(25)
        elif scene_pos.x() < width_threshold:
            self.is_scrolling = True
            self.view.horizontalScrollBar().setValue(
                self.view.horizontalScrollBar().value() - scroll_step
            )
            self.scroll_timer.start(25)

        if scene_pos.y() + height_threshold > view_rect.height():
            self.is_scrolling = True
            self.view.verticalScrollBar().setValue(
            self.view.verticalScrollBar().value() + scroll_step
            )
            self.scroll_timer.start(25)
        elif scene_pos.y() < height_threshold:
            self.is_scrolling = True
            self.view.verticalScrollBar().setValue(
                self.view.verticalScrollBar().value() - scroll_step
            )
            self.scroll_timer.start(25)

        # Aktualisiere den gesamten View nach jedem Scrollschritt
        self.view.update()

    def resume_movement(self):
        self.is_scrolling = False

    def restrict_cursor_within_window(self):
        cursor_pos = self.view.mapFromGlobal(QCursor.pos())
        view_rect = self.view.viewport().rect()

        if cursor_pos.x() < 0:
            cursor_pos.setX(0)
        elif cursor_pos.x() > view_rect.width():
            cursor_pos.setX(view_rect.width())

        if cursor_pos.y() < 0:
            cursor_pos.setY(0)
        elif cursor_pos.y() > view_rect.height():
            cursor_pos.setY(view_rect.height())

        QCursor.setPos(self.view.mapToGlobal(cursor_pos))

class AndGateSymbol2(QGraphicsItem):
    def __init__(self, width=20, height=20, parent=None):
        super().__init__(parent)
        self.width  = width
        self.height = height
        self.setAcceptedMouseButtons(Qt.AllButtons) 
        
        self.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.ItemIsFocusable, False)
        
    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)
    
    def paint(self, painter, option, widget):
        painter.setPen(QPen(Qt.black, 1.5))
        painter.setBrush(QBrush(Qt.lightGray))
        
        rect = QRectF(0, 0, self.width, self.height)
        radius = self.width / 2
        
        # Rechte Seite Bogen (AND)
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(radius, 0)
        path.arcTo(0, 0, self.width, self.height, 90, -180)
        path.lineTo(0, self.height)
        path.lineTo(0, 0)
        
        painter.drawPath(path)
        
        # AND Gatter Labels
        painter.setFont(QFont('Small', 8))
        painter.setPen(Qt.black)
        label_rect = QRectF(2, 4, 19, 14)
        painter.drawText(label_rect, Qt.AlignLeft, 'AND')
    
    def mousePressEvent(self, event):
        event.ignore() 

class ConnectionLine(QGraphicsPathItem):
    def __init__(self, points, parent=None):
        super().__init__(parent)
        path = QPainterPath()
        path.moveTo(points[0])
        for pt in points[1:]:
            path.lineTo(pt)
        self.setPath(path)
        self.setPen(QPen(Qt.black, 1.5))

class Chip7408Component(DraggableComponent):
    def __init__(self, name="7408", x=0, y=0, width=300, height=150, view=None, label="7408", connections=[], resizable_horizontal=False):
        super().__init__(name, x, y, width, height, view, label, connections, resizable_horizontal)
        self.setBrush(QColor(220, 220, 220))  # hellgrau Chipfarbe
        
        # Positionen für 4 Gatter (2 oben, 2 unten)
        gate_width = 24
        gate_height = 21
        spacing_x = 10
        spacing_y = 10
        
        # Oben links
        g1 = AndGateSymbol2(gate_width, gate_height, self)
        g1.setPos(65, 25)
        
        # Oben rechts
        g2 = AndGateSymbol2(gate_width, gate_height, self)
        g2.setPos(self.rect().width() - gate_width - 31, 25)
        
        # Unten links
        g3 = AndGateSymbol2(gate_width, gate_height, self)
        g3.setPos(40, self.rect().height() - gate_height - 25)
        
        # Unten rechts
        g4 = AndGateSymbol2(gate_width, gate_height, self)
        g4.setPos(self.rect().width() - gate_width - 60, self.rect().height() - gate_height - 25)
        
        # Als Kindobjekte hinzufügen (damit sie mitverschoben werden)
        for g in [g1, g2, g3, g4]:
            g.setParentItem(self)
    
    def paint(self, painter: QPainter, option, widget=None):
        rect = self.rect()

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(QColor(220, 220, 220))
        painter.drawRoundedRect(rect, 10, 10)

        pin_size = QSizeF(20, 20)
        spacing = (rect.width() - 40) / 6  # für 7 Pins → 6 Lücken
        pin_x_offset = -10  # alle Pins 10px nach links verschieben
        pin_y_adjust = 5     # Y-Anpassung für Pins

        # Obere Pins (14 bis 8)
        for i, pin in enumerate(range(14, 7, -1)):
            x = 20 + i * spacing + pin_x_offset
            y = rect.top() - pin_size.height() + pin_y_adjust
            pin_rect = QRectF(x, y, pin_size.width(), pin_size.height())
            painter.setPen(QPen(Qt.black, 1))
            painter.setBrush(Qt.white)
            painter.drawRect(pin_rect)
            painter.drawText(pin_rect, Qt.AlignCenter, str(pin))

        # Untere Pins (1 bis 7)
        for i, pin in enumerate(range(1, 8)):
            x = 20 + i * spacing + pin_x_offset
            y = rect.bottom() - pin_y_adjust
            pin_rect = QRectF(x, y, pin_size.width(), pin_size.height())
            painter.setPen(QPen(Qt.black, 1))
            painter.setBrush(Qt.white)
            painter.drawRect(pin_rect)
            painter.drawText(pin_rect, Qt.AlignCenter, str(pin))

        # Linke Wölbung (Halbkreis nach innen rechts)
        radius = 15
        center_y = rect.center().y()
        path = QPainterPath()
        arc_rect = QRectF(rect.left() - radius, center_y - radius, 2 * radius, 2 * radius)
        path.moveTo(rect.left(), center_y - radius)
        path.arcTo(arc_rect, 90, -180)
        painter.setBrush(QColor(220, 220, 220))
        painter.drawPath(path)

        # Vcc-Text (Pin 14)
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.setPen(Qt.black)
        vcc_rect = QRectF(rect.left() + 10, rect.top() + 5, 50, 20)
        painter.drawText(vcc_rect, Qt.AlignLeft, "Vcc")

        # GND-Text (Pin 7)
        gnd_rect = QRectF(rect.right() - 38, rect.bottom() - 25, 50, 20)
        painter.drawText(gnd_rect, Qt.AlignLeft, "GND")
        
        pen = QPen(Qt.black, 1.2)
        painter.setPen(pen)
        
        # Beispiel: Gatter unten links (Pin 1, 2 → Eingang, Pin 3 → Ausgang)
        # Positionen anpassen an tatsächliche Gatter/Pin-Kästchen
        
        # --- Eingang 1 (Pin 1 zu Gatter-Eingang)
        painter.drawLine(QPointF(21, 62), QPointF(40, 62))
        painter.drawLine(QPointF(21, 62), QPointF(21, 94))
        # --- Eingang 2 (Pin 2 zu Gatter-Eingang)
        painter.drawLine(QPointF(30, 70), QPointF(40, 70))
        painter.drawLine(QPointF(30, 70), QPointF(30, 84))
        painter.drawLine(QPointF(30, 84), QPointF(46, 84))
        painter.drawLine(QPointF(46, 84), QPointF(46, 94))
        # --- Ausgang (Gatter zu Pin 3)
        painter.drawLine(QPointF(65, 65), QPointF(74, 65))
        painter.drawLine(QPointF(74, 65), QPointF(74, 94))  # rechts raus zum Pin 3
        
        
        # --- Eingang 1 (Pin 6 zu Gatter-Eingang)
        painter.drawLine(QPointF(21+ 79, 62), QPointF(40+ 95, 62))
        painter.drawLine(QPointF(21+ 79, 62), QPointF(21+ 79, 94))
        # --- Eingang 2 (Pin 7 zu Gatter-Eingang)
        painter.drawLine(QPointF(110, 70), QPointF(115, 70))
        painter.drawLine(QPointF(110, 70), QPointF(110, 84))
        painter.drawLine(QPointF(110, 84), QPointF(125, 84))
        painter.drawLine(QPointF(125, 84), QPointF(125, 94))
        # --- Ausgang (Gatter zu Pin 8)
        painter.drawLine(QPointF(21+110, 65), QPointF(40+115, 65))
        painter.drawLine(QPointF(40+115, 65), QPointF(40+115, 94))
        
        
        # --- Eingang 1 (Pin 13 zu Gatter-Eingang)
        painter.drawLine(QPointF(47, 41), QPointF(66, 41))
        painter.drawLine(QPointF(47, 41), QPointF(47,  7))
        # --- Eingang 2 (Pin 12 zu Gatter-Eingang)
        painter.drawLine(QPointF(57, 32), QPointF(66, 32))
        painter.drawLine(QPointF(57, 32), QPointF(57, 18))
        painter.drawLine(QPointF(57, 18), QPointF(74, 18))
        painter.drawLine(QPointF(74, 18), QPointF(74,  7))
        # --- Ausgang (Gatter zu Pin 11)
        painter.drawLine(QPointF( 90, 37), QPointF(100, 37))
        painter.drawLine(QPointF(100, 37), QPointF(100,  7))
        
        
        # --- Eingang 1 (Pin 10 zu Gatter-Eingang)
        painter.drawLine(QPointF(125, 41), QPointF(144, 41))
        painter.drawLine(QPointF(125, 41), QPointF(125,  7))
        # --- Eingang 2 (Pin 9 zu Gatter-Eingang)
        painter.drawLine(QPointF(135, 32), QPointF(144, 32))
        painter.drawLine(QPointF(135, 32), QPointF(135, 18))
        painter.drawLine(QPointF(135, 18), QPointF(152, 18))
        painter.drawLine(QPointF(152, 18), QPointF(152,  7))
        # --- Ausgang (Gatter zu Pin 8)
        painter.drawLine(QPointF(174, 37), QPointF(180, 37))
        painter.drawLine(QPointF(180, 37), QPointF(180,  7))
        
        # Chip-Label (zentral im Chip)
        if self.label:
            painter.setFont(QFont("Arial", 12, QFont.Bold))
            painter.setPen(Qt.black)
            label_rect = QRectF(rect.left(), rect.center().y() - 10, rect.width(), 20)
            painter.drawText(label_rect, Qt.AlignCenter, self.label)

class CircuitDesigner(QWidget):
    def __init__(self):
        super().__init__()
        
        # QGraphicsScene und GridGraphicsView erstellen
        window_size = QSize(800, 600)
        self.scene  = QGraphicsScene()
        self.view   = GridGraphicsViewFormDesigner(self.scene, window_size)
        
        # Layout für das QWidget
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)
        
        
        #self.setCentralWidget(self.view)
        #self.resize(window_size)
        self.init_components()

    def init_components(self):
        chip7408 = Chip7408Component(self, x=50, y=50, width=200, height=100, view=self.view,
        resizable_horizontal=False)
        chip7408.setScale(0.95)
        
        self.scene.addItem(chip7408)
