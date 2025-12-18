# submit-workflow Specification

## Purpose
TBD - created by archiving change add-responsive-ui-folder-import. Update Purpose after archive.
## Requirements
### Requirement: Submit Button State Management
The application SHALL provide a "Submit" button that is enabled only when all required analysis parameters are valid.

#### Scenario: Valid analysis parameters
- **WHEN** an image is loaded
- **AND** all layer identification settings are complete and valid
- **THEN** the Submit button is enabled
- **AND** clicking Submit triggers the analysis and save workflow

#### Scenario: Incomplete parameters
- **WHEN** an image is loaded
- **AND** one or more required analysis parameters are missing or invalid
- **THEN** the Submit button is disabled (grayed out)
- **AND** the user cannot submit the analysis

#### Scenario: No image loaded
- **WHEN** no image is currently displayed
- **THEN** the Submit button is disabled
- **AND** no submit action can be triggered

### Requirement: Analyzed Image Output
When Submit is clicked, the application SHALL generate and save a processed image with overlay colors in the same folder as the original image.

#### Scenario: Submit single image analysis
- **WHEN** the user clicks Submit for "sample1.png"
- **AND** analysis completes successfully
- **THEN** a file "sample1_analyzed.png" is created in the source folder
- **AND** the analyzed image contains the color-coded layer overlay
- **AND** the output format matches the original format

#### Scenario: Submit TIFF image
- **WHEN** the user submits "experiment_042.tif"
- **THEN** the output file is "experiment_042_analyzed.tif"
- **AND** the TIFF format is preserved

#### Scenario: Submit JPEG image
- **WHEN** the user submits "photo.jpg"
- **THEN** the output file is "photo_analyzed.jpg"
- **AND** the JPEG format is preserved

### Requirement: Results File Format
For each submitted image, the application SHALL write one row to a tab-delimited text file with exactly five columns: filename, coverage, monolayer_coverage, bilayer_coverage, trilayer_coverage.

#### Scenario: First submission creates file
- **WHEN** the user submits the first image from folder "Experiment_A"
- **THEN** a file "Experiment_A_Analyzed.txt" is created in the same folder
- **AND** the file contains a header row with tab-separated columns
- **AND** the file contains one data row with the analysis results

#### Scenario: Subsequent submissions append data
- **WHEN** the user submits additional images from the same folder
- **THEN** new rows are appended to the existing results file
- **AND** the header row is not duplicated
- **AND** each row contains the correct tab-separated values

#### Scenario: Results file format validation
- **WHEN** the results file is created
- **THEN** the header row is exactly: "filename\tcoverage\tmonolayer_coverage\tbilayer_coverage\ttrilayer_coverage"
- **AND** each data row contains five tab-separated values
- **AND** the file uses UTF-8 encoding
- **AND** the file can be opened correctly in Microsoft Excel

### Requirement: Results File Naming and Location
The results file SHALL be named `[FolderName]_Analyzed.txt` and saved in the same folder selected by the user.

#### Scenario: Folder name in results filename
- **WHEN** the user loads images from folder "Test_Batch_2024"
- **AND** submits an analysis
- **THEN** the results file is named "Test_Batch_2024_Analyzed.txt"
- **AND** the file is located in the "Test_Batch_2024" folder

#### Scenario: Folder with spaces in name
- **WHEN** the user loads images from folder "My Test Folder"
- **THEN** the results file is "My Test Folder_Analyzed.txt"
- **AND** spaces are preserved in the filename

### Requirement: Duplicate Submission Handling
If a result for the same image already exists in the results file, the application SHALL display a dialog with overwrite, append, or cancel options.

#### Scenario: Re-submitting analyzed image
- **WHEN** the user submits "image1.png"
- **AND** a result row for "image1.png" already exists
- **THEN** a dialog appears asking "Results for this image already exist. What would you like to do?"
- **AND** three buttons are provided: Overwrite, Append new row, Cancel

#### Scenario: User chooses Overwrite
- **WHEN** the duplicate dialog is shown
- **AND** the user clicks "Overwrite"
- **THEN** the existing result row is replaced with new values
- **AND** the analyzed image file is overwritten
- **AND** no duplicate rows exist for that filename

#### Scenario: User chooses Append new row
- **WHEN** the duplicate dialog is shown
- **AND** the user clicks "Append new row"
- **THEN** a new row is added to the results file
- **AND** the new row may include a timestamp or iteration marker
- **AND** the analyzed image file is overwritten with new analysis

#### Scenario: User chooses Cancel
- **WHEN** the duplicate dialog is shown
- **AND** the user clicks "Cancel"
- **THEN** no changes are made to the results file
- **AND** the analyzed image file is not modified
- **AND** the dialog closes

### Requirement: Visual Feedback
After successful Submit, the application SHALL provide clear feedback to the user.

#### Scenario: Successful submission
- **WHEN** Submit completes successfully
- **THEN** a status message or toast notification appears
- **AND** the message indicates the analyzed image was saved
- **AND** the filename of the saved image is displayed
- **AND** confirmation that results were written to the text file

#### Scenario: Visual indicators
- **WHEN** submission is in progress
- **THEN** a processing indicator is shown
- **AND** when complete, a success icon or message appears
- **AND** the feedback is visible for at least 2-3 seconds

### Requirement: Error Handling
The application SHALL handle file write errors gracefully and provide actionable error messages.

#### Scenario: Analyzed image save failure
- **WHEN** saving the analyzed image fails (e.g., disk full, permissions issue)
- **THEN** an error dialog appears with a clear message
- **AND** the corresponding results row is NOT written to the text file
- **AND** the error message includes actionable information (e.g., "Check folder permissions")

#### Scenario: Results file write failure
- **WHEN** appending to the results file fails
- **THEN** an error dialog appears
- **AND** the analyzed image file remains saved (if it was successfully written)
- **AND** the error message suggests checking disk space or permissions

#### Scenario: Folder write-protected
- **WHEN** the source folder is read-only or write-protected
- **AND** the user attempts to submit
- **THEN** an error message indicates the folder is write-protected
- **AND** the user is advised to check folder permissions or select a different folder

