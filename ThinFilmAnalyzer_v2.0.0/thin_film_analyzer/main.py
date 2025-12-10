"""
Main entry point for the Thin Film Coverage Analyzer application.
"""

import sys
from pathlib import Path

# Add parent directory to path to allow running as script
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from thin_film_analyzer.ui.main_window import MainWindow
from thin_film_analyzer.config.defaults import get_settings_dir, APP_NAME, APP_VERSION
from thin_film_analyzer.core.logger import get_logger


def main():
    """
    Application entry point.
    """
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    # Set application-wide style
    app.setStyle("Fusion")

    # Initialize logger
    logger = get_logger()
    settings_dir = get_settings_dir()

    print(f"{APP_NAME} v{APP_VERSION}")
    print(f"Settings directory: {settings_dir}")
    print(f"Loading settings from: {settings_dir / 'settings.json'}")

    try:
        # Create and show main window
        window = MainWindow()
        window.show()

        print("Application started successfully.")

        # Run event loop
        sys.exit(app.exec())

    except Exception as e:
        logger.log_error(
            "ApplicationStartupError",
            str(e),
            stack_trace=str(e.__traceback__)
        )
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
