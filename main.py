import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QComboBox,  QHBoxLayout, QPushButton, QLabel, QListWidgetItem, QFileDialog, QScrollArea, QListWidget, QCheckBox, QStatusBar, QMessageBox, QShortcut, QTreeWidget, QTreeWidgetItem
from PyQt5.QtGui import QIcon, QPixmap, QPalette, QColor, QKeySequence
from PyQt5.QtCore import Qt, QSize
import os
from PIL import Image

class SettingsPopup(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Settings')
        self.setGeometry(100, 100, 400, 300)
        layout = QVBoxLayout()

        # Add your settings widgets here
        # Example: layout.addWidget(QLabel('Setting 1'))

        self.setLayout(layout)


class ImageMetadataViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Meta Extractor')
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Initialize the imageMetadata dictionary here
        self.imageMetadata = {}

        # Initialize an additional attribute to track selected images
        self.selectedImages = set()

        # Initialize orderedImagePaths here to ensure it's always defined.
        self.orderedImagePaths = []

        self.allSelected = False 

        self.applyStyling()

        self.layout = QHBoxLayout(self.central_widget)

        self.setupControlPanel()  # This needs to be called before setupImageDisplayArea
        self.setupImageDisplayArea()
        self.imageDisplayArea.setMaximumWidth(120)
        self.setupMetadataDisplayArea()
        self.setupStatusBar()
        

    def applyStyling(self):
        # Palette definition for the main window
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        self.setPalette(palette)

        # If you have already created the imageDisplayArea, set its palette here
        if hasattr(self, 'imageDisplayArea'):
            # Define QListWidget specific colors
            listWidgetBgColor = QColor(53, 53, 53)  # Adjust the color as needed
            listWidgetTextColor = Qt.white  # Adjust the color as needed

            # Set QListWidget specific palette settings
            listWidgetPalette = self.imageDisplayArea.palette()  # Get the current palette of the QListWidget
            listWidgetPalette.setColor(QPalette.Base, listWidgetBgColor)  # Set the background color
            listWidgetPalette.setColor(QPalette.Text, listWidgetTextColor)  # Set the text color
            self.imageDisplayArea.setPalette(listWidgetPalette)  # Apply the palette to imageDisplayArea

    def create_button(self, icon_path, tooltip_text, shortcut_key, callback):
        button = QPushButton()
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(60, 60))  # Adjust icon size as needed
        button.setMaximumSize(QSize(60, 60))
        button.setStyleSheet("""
            QPushButton {
                background: transparent; 
                border: none; 
                padding: 4px;
            }
            QPushButton:hover {
                border: 2px solid white;
                border-radius: 5px;
            }
        """)
        button.setCursor(Qt.PointingHandCursor)  # Change the cursor to a hand when hovering
        button.clicked.connect(callback)
        if shortcut_key:
            shortcut = QShortcut(QKeySequence(shortcut_key), self)
            shortcut.activated.connect(callback)
        return button

    def setupImageDisplayArea(self):
        self.imageDisplayArea = QListWidget(self.central_widget)
        self.imageDisplayArea.setSelectionMode(QListWidget.ExtendedSelection)
        self.imageDisplayArea.itemSelectionChanged.connect(self.onImagesSelectionChanged)

        # Ensure the widget inherits the parent style
        self.imageDisplayArea.setAutoFillBackground(True)

        # Updated stylesheet for imageDisplayArea
        self.imageDisplayArea.setStyleSheet("""
        QListWidget {
            background-color: #353535;  /* Match the app's bg color */
            color: white;  /* Text color */
        }
        QListWidget::item {
            background-color: #353535;  /* Match the app's bg color */
            color: white;
            border: none;
        }
        QListWidget::item:selected {
            background-color: #000000;  /* Color for selected items (adjustable) */
            color: black;  /* Text color for selected items */
        }
        QListWidget::item:hover {
            background-color: #000000;  /* Hover color (adjustable) */
        }
        """)
        
        #print(self.imageDisplayArea.palette().color(QPalette.Base).name())
        #print(self.imageDisplayArea.styleSheet())

        self.layout.addWidget(self.imageDisplayArea)
        self.imageDisplayArea.update()  # Force style update


    def onImagesSelectionChanged(self):
        from PyQt5.QtGui import QBrush, QColor  # Import QBrush and QColor

        # Initialize the selectedImages as an empty set
        self.selectedImages = set()
        
        # Iterate over all items in the imageDisplayArea
        for index in range(self.imageDisplayArea.count()):
            item = self.imageDisplayArea.item(index)
            widget = self.imageDisplayArea.itemWidget(item)

            # Check if the widget is not None
            if widget is not None:
                imagePath = widget.property("imagePath")
                if imagePath:
                    # Check if the item is selected
                    if item.isSelected():
                        # Add the imagePath to selectedImages
                        self.selectedImages.add(imagePath)
                        
                        # Change background color to black for selected items
                        item.setBackground(QBrush(QColor(Qt.white)))
                        item.setForeground(QColor(Qt.black))  # Change text color to white
                    else:
                        # Reset background color to default (None) for deselected items
                        item.setBackground(QBrush(QColor(Qt.black)))
                        item.setForeground(QColor(Qt.white))  # Reset text color to default (black)
        
        self.updateMetadataDisplay()
        

    def setupMetadataDisplayArea(self):
        self.metadataDisplayArea = QTreeWidget()
        self.metadataDisplayArea.setHeaderLabels(['Field', 'Data'])  # Change the header labels here
        self.metadataDisplayArea.itemDoubleClicked.connect(self.onItemDoubleClicked)  # Connect the signal to the slot

        # Style the header to match the dark theme
        header = self.metadataDisplayArea.header()
        header.setStyleSheet("""
            QHeaderView::section {
                Background-color: #353535;  /* Match the app's bg color */
                color: white;  /* Text color */
                border: none;  /* No border for a cleaner look */
                padding-left: 4px;  /* Padding to align text properly, adjust as needed */
                font-size: 12px;  /* Adjust font size as needed */
            }
        """)

        self.layout.addWidget(self.metadataDisplayArea)


    def onItemDoubleClicked(self, item, column):
        QApplication.clipboard().setText(item.text(column))
        self.statusBar.showMessage("Field copied to clipboard", 3000)  # Show a message for 3 seconds

    def setupControlPanel(self):
        self.controlPanel = QVBoxLayout()

        # Create buttons using the create_button method
        self.loadImagesButton = self.create_button('images/add.png', 'Load Images', 'Ctrl+L', self.loadImages)
        self.copyClipboardButton = self.create_button('images/copy.png', 'Copy to Clipboard', 'Ctrl+C', self.copyToClipboard)
        self.saveFileButton = self.create_button('images/save.png', 'Save to File', 'Ctrl+S', self.saveToFile)
        self.toggleSelectButton = self.create_button('images/select.png', 'Toggle Select', 'Ctrl+T', self.toggleSelectImages)
        self.deleteButton = self.create_button('images/delete.png', 'Delete Selected', 'Ctrl+D', self.deleteSelectedImages)
        #self.settingsButton = self.create_button('images/settings.png', 'Settings', 'Ctrl+Shift+S', self.openSettings)

        # Add buttons to the control panel
        self.controlPanel.addWidget(self.loadImagesButton)
        self.controlPanel.addWidget(self.copyClipboardButton)
        self.controlPanel.addWidget(self.saveFileButton)
        self.controlPanel.addWidget(self.toggleSelectButton)
        self.controlPanel.addWidget(self.deleteButton)
        #self.controlPanel.addWidget(self.settingsButton)

        self.layout.addLayout(self.controlPanel)


    def openSettings(self):
        self.settingsPopup = SettingsPopup()
        self.settingsPopup.show()


    def deleteSelectedImages(self):
        confirmDelete = QMessageBox.question(self, 'Confirm Delete', 'Are you sure you want to remove the selected image(s)?',
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if confirmDelete == QMessageBox.Yes:
            for imagePath in list(self.selectedImages):  # Use list to avoid modifying the set during iteration
                # Remove from orderedImagePaths and imageMetadata
                self.orderedImagePaths.remove(imagePath)
                if imagePath in self.imageMetadata:
                    del self.imageMetadata[imagePath]
                
                # Find and remove the corresponding QListWidgetItem
                for index in range(self.imageDisplayArea.count()):
                    item = self.imageDisplayArea.item(index)
                    widget = self.imageDisplayArea.itemWidget(item)
                    if widget.property("imagePath") == imagePath:
                        self.imageDisplayArea.takeItem(index)
                        break
            
            # Clear the selection and update the display
            self.selectedImages.clear()
            self.updateMetadataDisplay()
            self.statusBar.showMessage("Selected images removed from the app", 5000)


    def toggleSelectImages(self):
        if self.allSelected:
            # If all were selected, deselect all and update the button text
            self.imageDisplayArea.clearSelection()
            #self.toggleSelectButton.setText('Select All')
            self.allSelected = False
        else:
            # If not all were selected, select all and update the button text
            self.imageDisplayArea.selectAll()
            #self.toggleSelectButton.setText('Deselect All')
            self.allSelected = True

        # Update metadata display to reflect the selection change
        self.updateMetadataDisplay()

    def saveToFile(self):
        defaultFileName = "metadata.txt"  # Define the default file name
        # Include the default file name in the getSaveFileName call
        filePath, _ = QFileDialog.getSaveFileName(self, "Save File", defaultFileName, "Text Files (*.txt)")
        if filePath:
            with open(filePath, 'w') as file:
                for imagePath in self.orderedImagePaths:
                    if imagePath in self.selectedImages:
                        # Write the filename
                        file.write(f"Filename: {os.path.basename(imagePath)}\n")

                        # Write the metadata for the image
                        metadata = self.imageMetadata.get(imagePath, {})
                        for key, value in metadata.items():
                            display_key = key.replace('parameters', 'Positive Prompt') if 'parameters' in key else key
                            file.write(f"{display_key}: {value}\n")

                        # Write a visual separator
                        file.write("\n")

            self.statusBar.showMessage("Metadata saved to file", 5000)  # Display a message for 5 seconds


    def copyToClipboard(self):
        selectedMetadata = []
        for imagePath in self.orderedImagePaths:
            if imagePath in self.selectedImages:
                # Append the filename
                selectedMetadata.append(f"Filename: {os.path.basename(imagePath)}")

                # Append the metadata for the image
                metadata = self.imageMetadata.get(imagePath, {})
                for key, value in metadata.items():
                    display_key = key.replace('parameters', 'Positive Prompt') if 'parameters' in key else key
                    selectedMetadata.append(f"{display_key}: {value}")

                # Append a visual separator
                selectedMetadata.append("")

        # Join the metadata with newline characters
        clipboardText = "\n".join(selectedMetadata)
        QApplication.clipboard().setText(clipboardText)
        self.statusBar.showMessage("Metadata copied to clipboard", 5000)  # Display a message for 5 seconds





    def setupStatusBar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

    def loadImages(self):
        fileDialog = QFileDialog()
        fileDialog.setFileMode(QFileDialog.ExistingFiles)
        fileDialog.setNameFilter("Images (*.png)")
        if fileDialog.exec_():
            newImagePaths = fileDialog.selectedFiles()
            
            # Sort new image paths alphabetically
            newImagePaths.sort()
            
            # Append new image paths to the orderedImagePaths, avoiding duplicates
            for path in newImagePaths:
                if path not in self.orderedImagePaths:
                    self.orderedImagePaths.append(path)

                    with Image.open(path) as img:
                        self.imageMetadata[path] = img.info  # Store the metadata

            # Sort orderedImagePaths alphabetically to ensure the order is always correct
            self.orderedImagePaths.sort()

            # Clear existing thumbnails to re-add them in sorted order
            self.imageDisplayArea.clear()

            # Add thumbnails in sorted order
            for path in self.orderedImagePaths:
                item = QListWidgetItem()
                pixmap = QPixmap(path)
                
                # Scale pixmap to have a maximum width of 100px, maintaining aspect ratio
                pixmap = pixmap.scaledToWidth(100, Qt.SmoothTransformation)

                self.imageDisplayArea.setMaximumWidth(120)
                
                label = QLabel()
                label.setPixmap(pixmap)
                label.setProperty("imagePath", path)  # Store the image path
                
                item.setSizeHint(label.sizeHint())  # Set the item size to match the label
                
                self.imageDisplayArea.addItem(item)
                self.imageDisplayArea.setItemWidget(item, label)

            # Update metadata display after all images and their metadata are loaded
            self.updateMetadataDisplay()

            # Select all items after adding them to the list
            self.imageDisplayArea.selectAll()
            #self.toggleSelectButton.setText('Deselect All')
            self.allSelected = True


    def updateMetadataDisplay(self):
        self.metadataDisplayArea.clear()  # Clear previous metadata

        # Proceed only if orderedImagePaths is not empty
        if self.orderedImagePaths:
            for imagePath in self.orderedImagePaths:
                if imagePath in self.selectedImages:
                    metadata = self.imageMetadata.get(imagePath, {})
                    imageItem = QTreeWidgetItem(self.metadataDisplayArea, [os.path.basename(imagePath)])
                    imageItem.setExpanded(True)  # Automatically expand the item to show child items

                    # Display metadata for the current image as individual selectable items
                    for key, value in sorted(metadata.items()):
                        # If the value is a string, split it into lines for separate entries
                        if isinstance(value, str):
                            entries = value.split('\n')  # Split the string into lines
                            for entry in entries:
                                # Split each line into key and value
                                parts = entry.split(': ', 1)
                                if len(parts) == 2:
                                    k, v = parts
                                    childItem = QTreeWidgetItem(imageItem, [k, v])
                                else:
                                    # If there's no ': ' in the line, use the whole line as the value for the current key
                                    childItem = QTreeWidgetItem(imageItem, [key, entry])
                        else:
                            # The value is a single entry, not a compound string
                            childItem = QTreeWidgetItem(imageItem, [key, str(value)])

                    # Add a visual separator item after each image's metadata
                    separatorItem = QTreeWidgetItem(self.metadataDisplayArea, ['', ''])
                    separatorItem.setFlags(Qt.NoItemFlags)  # Make the separator non-selectable and non-interactive

        self.metadataDisplayArea.repaint()  # Force the metadata display area to update its contents


    def onCheckboxStateChanged(self, state):
        checkbox = self.sender()
        key = checkbox.text().split(':')[0]
        # Update the selected state of this metadata for all selected images
        for imagePath in self.selectedImages:
            self.imageMetadata[imagePath][key] = checkbox.isChecked()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = ImageMetadataViewer()
    viewer.show()
    sys.exit(app.exec_())