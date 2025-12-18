# Capability: Folder Import

## ADDED Requirements

### Requirement: Folder Selection Control
The application SHALL provide a "Select Folder" button or menu item that opens a system folder picker dialog.

#### Scenario: User clicks Select Folder button
- **WHEN** the user clicks "Select Folder" in the toolbar or menu
- **THEN** a standard system folder picker dialog opens
- **AND** the user can navigate to any accessible folder

#### Scenario: User cancels folder selection
- **WHEN** the folder picker dialog is canceled
- **THEN** no images are loaded
- **AND** the current state is preserved

### Requirement: Automatic Image Loading
After folder selection, the application SHALL automatically scan only the selected folder (non-recursive) and load all supported image files.

#### Scenario: Folder with supported images selected
- **WHEN** the user selects a folder containing 10 PNG and 5 JPEG files
- **THEN** all 15 images are automatically loaded
- **AND** the images appear in the image navigation dropdown
- **AND** the first image is displayed

#### Scenario: Folder with mixed file types
- **WHEN** the user selects a folder with images, text files, and other documents
- **THEN** only supported image formats are loaded
- **AND** non-image files are ignored without error messages

#### Scenario: Empty folder selected
- **WHEN** the user selects a folder with no supported images
- **THEN** a message indicates no images were found
- **AND** the current state remains unchanged

### Requirement: Supported Image Formats
The folder scanner SHALL support PNG (.png), JPEG (.jpg, .jpeg), TIFF (.tif, .tiff), and BMP (.bmp) image formats at minimum.

#### Scenario: Folder with various formats
- **WHEN** a folder contains image1.png, image2.jpg, image3.tif, and image4.bmp
- **THEN** all four images are loaded successfully
- **AND** each image can be viewed and analyzed

### Requirement: Analyzed Image Exclusion
The folder scanner SHALL ignore files with `_analyzed` suffix to avoid loading previously processed images.

#### Scenario: Folder with analyzed images
- **WHEN** a folder contains "sample1.png" and "sample1_analyzed.png"
- **THEN** only "sample1.png" is loaded
- **AND** "sample1_analyzed.png" is excluded from the image list

#### Scenario: Multiple analyzed variants
- **WHEN** a folder contains original images and their analyzed versions
- **THEN** only original images without `_analyzed` suffix are loaded
- **AND** the image count reflects only original images

### Requirement: Progress Indicator
The application SHALL display a progress indicator while loading images from the folder.

#### Scenario: Loading large batch
- **WHEN** the user selects a folder with 220 images
- **THEN** a progress dialog displays "Loading images: [current] / [total]"
- **AND** a progress bar shows visual feedback
- **AND** the current count increments as each image is loaded

#### Scenario: User cancels loading
- **WHEN** the progress dialog is displayed with a cancel button
- **AND** the user clicks cancel during loading
- **THEN** loading stops immediately
- **AND** already-loaded images remain available
- **AND** the progress dialog closes

### Requirement: Image List Display
All loaded images SHALL be displayed in the UI with navigation controls.

#### Scenario: Successful folder load
- **WHEN** a folder with images is loaded successfully
- **THEN** all images appear in the navigation dropdown
- **AND** prev/next navigation buttons are enabled
- **AND** the image counter displays "Image 1 of [total]"

#### Scenario: Navigate through loaded images
- **WHEN** multiple images are loaded
- **THEN** the user can navigate between them using dropdown, prev/next buttons
- **AND** the current image index updates correctly
- **AND** the image viewer displays the selected image

### Requirement: File Preservation
The application SHALL NOT modify, move, or delete any original images in the selected folder.

#### Scenario: Folder loaded and analyzed
- **WHEN** images are loaded from a folder and analysis is performed
- **THEN** original image files remain unchanged
- **AND** all processing output is written as new files
- **AND** original file timestamps are preserved

### Requirement: Drag-and-Drop Removal
The existing drag-and-drop upload interaction SHALL be removed from the UI.

#### Scenario: User attempts to drag files
- **WHEN** the user drags image files onto the application window
- **THEN** no drag-and-drop cursor or visual feedback appears
- **AND** files are not loaded via drag-and-drop
