# Capability: Responsive UI

## ADDED Requirements

### Requirement: Minimum Window Size
The application window SHALL enforce a minimum size of 1280×720 pixels.

#### Scenario: Window opens on standard display
- **WHEN** the application launches on a display with resolution >= 1280×720
- **THEN** the window opens at the last saved size or default size (1200×800)
- **AND** all UI elements are visible and functional

#### Scenario: Window opens on small display
- **WHEN** the application launches on a display smaller than 1280×720
- **THEN** the window opens at maximum available size
- **AND** scrolling is provided if necessary to access all controls

#### Scenario: User attempts to resize below minimum
- **WHEN** the user tries to resize the window below 1280×720
- **THEN** the window stops resizing at the minimum dimensions
- **AND** all critical UI elements remain visible

### Requirement: Dynamic Layout Scaling
The UI SHALL automatically reflow and scale when the user resizes the application window.

#### Scenario: User maximizes window
- **WHEN** the user clicks the maximize button
- **THEN** the layout expands to fill the entire screen
- **AND** the image viewing area grows proportionally
- **AND** control panels remain within maximum width constraints

#### Scenario: User manually resizes window
- **WHEN** the user drags window borders to resize
- **THEN** the UI updates in real-time
- **AND** spacing and margins adjust appropriately
- **AND** no UI elements are clipped or hidden

#### Scenario: Window restored from maximized
- **WHEN** the user restores the window from maximized state
- **THEN** the layout scales back to the restored size
- **AND** all controls remain accessible

### Requirement: Image Viewing Area Expansion
The image viewing area SHALL expand to fill available space as the window grows.

#### Scenario: Window width increases
- **WHEN** the user widens the application window
- **THEN** the image viewer width increases proportionally
- **AND** the displayed image scales to fit the larger viewing area

#### Scenario: Window height increases
- **WHEN** the user increases window height
- **THEN** the image viewer height increases
- **AND** the image scales vertically while maintaining aspect ratio

### Requirement: Control Panel Width Constraints
Control panels (left sidebar) SHALL have a maximum width of 400-500 pixels to prevent excessive stretching on ultra-wide displays.

#### Scenario: Window opened on ultra-wide display
- **WHEN** the application opens on a display wider than 3000 pixels
- **THEN** control panels maintain maximum width of 500 pixels
- **AND** extra horizontal space becomes margins or expands the image viewing area
- **AND** controls remain readable and properly sized

#### Scenario: Window width at minimum
- **WHEN** the window is at minimum width (1280 pixels)
- **THEN** control panels scale down appropriately
- **AND** all controls remain accessible and usable

### Requirement: Readable Text and Icon Sizes
Text and icons SHALL maintain readable sizes across all supported window sizes and SHALL NOT scale excessively on large displays.

#### Scenario: Display on 4K monitor
- **WHEN** the application runs on a 4K (3840×2160) display
- **THEN** text remains readable (not too small)
- **AND** icons maintain appropriate size
- **AND** fonts do not scale excessively large

#### Scenario: Display on 1280×720 minimum
- **WHEN** the window is at minimum size
- **THEN** all text labels are readable
- **AND** button text is not truncated
- **AND** icons are properly sized for controls
