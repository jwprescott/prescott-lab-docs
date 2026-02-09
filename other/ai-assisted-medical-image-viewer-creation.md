# AI-assisted medical image viewer creation

Below is the final image viewer code for the YouTube video at: [https://youtu.be/ce1jSoMmRi0](https://youtu.be/ce1jSoMmRi0)

\=======================

```python
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QToolBar, QSplitter, QVBoxLayout, QWidget, QFileDialog, QLabel
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QImage, QPixmap
import pydicom
import numpy as np
from datetime import datetime

class DicomTreeItem:
    def __init__(self, name, path, item_type):
        self.name = str(name)
        self.path = path
        self.item_type = item_type
        self.children = []
        self.sort_key = None

class DicomViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dicom_data = None
        self.current_series = None
        self.current_image_index = 0
        self.current_image = None
        self.window_center = 0
        self.window_width = 0
        self.dragging = False
        self.last_mouse_pos = QPoint()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('DICOM Image Viewer')
        self.setGeometry(100, 100, 1000, 600)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        toolbar = QToolBar()
        self.addToolBar(toolbar)
        toolbar.addAction('Load Directory', self.load_directory)

        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        self.tree_view = QTreeView()
        self.tree_model = QStandardItemModel()
        self.tree_view.setModel(self.tree_model)
        self.tree_view.doubleClicked.connect(self.on_tree_item_double_clicked)
        splitter.addWidget(self.tree_view)

        self.image_widget = QLabel()
        self.image_widget.setAlignment(Qt.AlignCenter)
        self.image_widget.setMouseTracking(True)
        self.image_widget.mousePressEvent = self.start_window_level_adjustment
        self.image_widget.mouseReleaseEvent = self.stop_window_level_adjustment
        self.image_widget.mouseMoveEvent = self.adjust_window_level
        splitter.addWidget(self.image_widget)

        splitter.setSizes([200, 800])

        self.image_widget.wheelEvent = self.on_mouse_wheel

    def load_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.dicom_data = self.search_dicom_files(directory)
            self.update_tree_view()

    def search_dicom_files(self, directory):
        dicom_data = DicomTreeItem("Root", directory, "root")
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.dcm'):
                    try:
                        ds = pydicom.dcmread(os.path.join(root, file))
                        patient_name = str(ds.PatientName) if hasattr(ds, 'PatientName') else "Unknown Patient"
                        study_description = str(ds.StudyDescription) if hasattr(ds, 'StudyDescription') else "Unknown Study"
                        series_description = str(ds.SeriesDescription) if hasattr(ds, 'SeriesDescription') else "Unknown Series"

                        patient_item = self.find_or_create_child(dicom_data, patient_name, "patient")
                        study_item = self.find_or_create_child(patient_item, study_description, "study")
                        series_item = self.find_or_create_child(study_item, series_description, "series")
                        
                        image_item = self.find_or_create_child(series_item, file, "image", os.path.join(root, file))
                        image_item.sort_key = self.get_sort_key(ds)
                    except Exception as e:
                        print(f"Error reading DICOM file: {file}. Error: {str(e)}")
        
        self.sort_series_images(dicom_data)
        return dicom_data

    def get_sort_key(self, ds):
        if hasattr(ds, 'InstanceNumber'):
            return int(ds.InstanceNumber)
        elif hasattr(ds, 'AcquisitionTime'):
            return datetime.strptime(ds.AcquisitionTime, '%H%M%S.%f')
        else:
            return 0

    def sort_series_images(self, item):
        if item.item_type == "series":
            item.children.sort(key=lambda x: x.sort_key)
        for child in item.children:
            self.sort_series_images(child)

    def find_or_create_child(self, parent, name, item_type, path=None):
        for child in parent.children:
            if child.name == name and child.item_type == item_type:
                return child
        new_child = DicomTreeItem(name, path or parent.path, item_type)
        parent.children.append(new_child)
        return new_child

    def update_tree_view(self):
        self.tree_model.clear()
        root_item = self.tree_model.invisibleRootItem()
        self.add_tree_items(root_item, self.dicom_data)

    def add_tree_items(self, parent_item, dicom_item):
        item = QStandardItem(dicom_item.name)
        item.setData(dicom_item)
        parent_item.appendRow(item)
        for child in dicom_item.children:
            self.add_tree_items(item, child)

    def on_tree_item_double_clicked(self, index):
        item = self.tree_model.itemFromIndex(index)
        dicom_item = item.data()
        if dicom_item.item_type == "series":
            self.load_series(dicom_item)
        elif dicom_item.item_type == "image":
            self.display_image(dicom_item.path)

    def load_series(self, series_item):
        self.current_series = series_item
        self.current_image_index = 0
        if self.current_series.children:
            self.display_image(self.current_series.children[0].path)

    def display_image(self, image_path):
        try:
            ds = pydicom.dcmread(image_path)
            self.current_image = ds
            self.window_center = ds.WindowCenter if hasattr(ds, 'WindowCenter') else ds.pixel_array.mean()
            self.window_width = ds.WindowWidth if hasattr(ds, 'WindowWidth') else ds.pixel_array.std() * 2
            
            if isinstance(self.window_center, pydicom.multival.MultiValue):
                self.window_center = self.window_center[0]
            if isinstance(self.window_width, pydicom.multival.MultiValue):
                self.window_width = self.window_width[0]
            
            self.update_image()
        except Exception as e:
            print(f"Error displaying image: {image_path}. Error: {str(e)}")

    def update_image(self):
        if self.current_image is None:
            return

        arr = self.current_image.pixel_array.astype(np.float32)
        arr = self.apply_window_level(arr, self.window_center, self.window_width)
        arr = (arr * 255).astype(np.uint8)

        if len(arr.shape) == 3 and arr.shape[2] == 3:  # RGB image
            qimage = QImage(arr.data, arr.shape[1], arr.shape[0], arr.strides[0], QImage.Format_RGB888)
        else:  # Grayscale image
            qimage = QImage(arr.data, arr.shape[1], arr.shape[0], arr.strides[0], QImage.Format_Grayscale8)
        
        pixmap = QPixmap.fromImage(qimage)
        self.image_widget.setPixmap(pixmap.scaled(self.image_widget.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def apply_window_level(self, image, center, width):
        img_min = center - width // 2
        img_max = center + width // 2
        image = np.clip(image, img_min, img_max)
        image = (image - img_min) / (img_max - img_min)
        return image

    def start_window_level_adjustment(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.last_mouse_pos = event.pos()

    def stop_window_level_adjustment(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def adjust_window_level(self, event):
        if self.dragging and self.current_image is not None:
            delta = event.pos() - self.last_mouse_pos
            self.window_width += delta.x()
            self.window_center += delta.y()
            
            # Ensure window width is always positive
            self.window_width = max(1, self.window_width)
            
            self.update_image()
            self.last_mouse_pos = event.pos()

    def on_mouse_wheel(self, event):
        if self.current_series:
            delta = event.angleDelta().y()
            if delta > 0:
                self.current_image_index = max(0, self.current_image_index - 1)
            else:
                self.current_image_index = min(len(self.current_series.children) - 1, self.current_image_index + 1)
            self.display_image(self.current_series.children[self.current_image_index].path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = DicomViewer()
    viewer.show()
    sys.exit(app.exec_())
```
