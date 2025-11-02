# rpa_suite/core/artemis.py

# imports standard
from pathlib import Path
from time import sleep, time
from typing import Optional, Tuple, Union

# imports external
import pyautogui as artemis_engine

# imports internal
from rpa_suite.functions._printer import alert_print, success_print

# constantes
OPENCV_AVAILABLE_FROM_ARTEMIS = False


class ArtemisError(Exception):
    """Custom exception for Artemis errors."""

    def __init__(self, message):
        clean_message = message.replace("ArtemisError:", "").strip()
        super().__init__(f"ArtemisError: {clean_message}")


class Artemis:
    """
    Artemis:
    ----------
    Intelligent desktop automation based on computer vision.

    Specialized in locating and interacting with visual elements
    in the graphical interface, optimized for robust RPA automation.
    """

    def __init__(self):
        """
        Artemis:
        ----------
        Intelligent desktop automation based on computer vision.

        Specialized in locating and interacting with visual elements
        in the graphical interface, optimized for robust RPA automation.
        """
        artemis_engine.FAILSAFE = True  # Move mouse to top-left corner to stop
        artemis_engine.PAUSE = 0.1  # Default pause between commands
        global OPENCV_AVAILABLE_FROM_ARTEMIS  # pylint: disable=global-statement
        OPENCV_AVAILABLE_FROM_ARTEMIS = self.__check_opencv_availability()

    # pylint: disable=import-outside-toplevel
    def __check_opencv_availability(self) -> bool:
        """Checks if OpenCV is available in the system."""
        try:
            # pylint: disable=import-outside-toplevel
            import cv2  # pylint: disable=unused-import

            return True
        except ImportError:
            return False

    def click_image(  # pylint: disable=too-many-positional-arguments,too-many-locals
        self,
        image_label: str,
        images_folder: Union[str, Path] = "resource",
        confidence: float = 0.78,
        timeout: float = 10.0,
        click_center: bool = True,
        click_button: str = "left",
        double_click: bool = False,
        search_interval: float = 0.5,
        region: Optional[Tuple[int, int, int, int]] = None,
        grayscale: bool = True,
        display_details: bool = False,
        verbose: bool = False,
    ) -> Union[Tuple[int, int], bool]:
        """
        Locates an image on the screen and clicks on it.

        This function searches for a specific image on the screen using PyAutoGUI
        and performs a click at the found position. Implements search with timeout
        and different confidence levels for better accuracy (when OpenCV is available).

        Args:
            image_label (str): Image file name (with or without extension).
                            Ex: 'ok_button' or 'ok_button.png'
            images_folder (Union[str, Path], optional): Path to images folder.
                                                    Default: "resource"
            confidence (float, optional): Confidence level for location (0.0-1.0).
                                        Requires OpenCV installed. If not available, will be ignored.
                                        High values = higher precision, lower tolerance.
                                        Default: 0.78
            timeout (float, optional): Time limit in seconds for search.
                                    Default: 10.0
            click_center (bool, optional): If True, clicks at the center of the image.
                                        If False, clicks at the top-left corner.
                                        Default: True
            click_button (str, optional): Mouse button ('left', 'right', 'middle').
                                        Default: 'left'
            double_click (bool, optional): If True, performs double click.
                                        Default: False
            search_interval (float, optional): Interval between search attempts.
                                            Default: 0.5 seconds
            region (Optional[Tuple[int, int, int, int]], optional): Screen region to search.
                                                                Format: (x, y, width, height)
                                                                Default: None (entire screen)
            grayscale (bool, optional): If True, searches in grayscale (faster).
                                    Default: True
            display_details (bool, optional): If True, displays details.
                                    Default: False
            verbose (bool, optional): If True, displays verbose output.
                                    Default: False

        Returns:
            Union[Tuple[int, int], bool]: Coordinates (x, y) of the image center if found
                                        or False if not found within timeout.

        Raises:
            ImageClickError: If there's an error in configuration or execution.
            FileNotFoundError: If the image file is not found.
            ValueError: If parameters are invalid.

        Note:
            To use the confidence parameter, install OpenCV: pip install opencv-python
            Without OpenCV, the function will work with exact pixel matching.

        Example:
            >>> # Search and click on a button
            >>> position = click_image('save_button.png', confidence=0.9, timeout=5.0)
            >>> if position:
            ...     print(f"Clicked at position: {position}")
            ... else:
            ...     print("Image not found")

            >>> # Search in specific screen region
            >>> region_result = click_image(
            ...     'menu_icon',
            ...     region=(0, 0, 500, 300),  # Search only in top-left corner
            ...     confidence=0.7
            ... )
        """

        # Parameter validation
        self._validate_parameters(confidence, timeout, search_interval, click_button, region)

        # Resolve full image path
        image_path = self._resolve_image_path(image_label, images_folder)

        # Warning if confidence will be ignored
        if confidence != 0.8 and not OPENCV_AVAILABLE_FROM_ARTEMIS:
            if verbose:
                alert_print(
                    f"Parameter confidence={confidence} will be ignored. " + "Install OpenCV: pip install opencv-python"
                )

        if verbose:
            print(f"Starting image search: {image_path}")
        if display_details:
            if verbose:
                print(
                    f"Settings: confidence={'N/A' if not OPENCV_AVAILABLE_FROM_ARTEMIS else confidence}, "
                    + f"timeout={timeout}s, region={region}"
                )

        # Temporary PyAutoGUI settings
        original_pause = artemis_engine.PAUSE
        artemis_engine.PAUSE = 0.05  # Reduce pause for faster search

        try:
            # Execute search with timeout
            position = self._search_image_with_timeout(
                image_path=image_path,
                confidence=confidence,
                timeout=timeout,
                search_interval=search_interval,
                region=region,
                grayscale=grayscale,
                verbose=verbose,
            )

            if not position:
                if verbose:
                    alert_print(f"Image not found after {timeout}s: {image_path.name}")
                return False

            # Calculate click position
            click_position = self._calculate_click_position(position, click_center)

            # Perform click
            self._perform_click(click_position, click_button, double_click, verbose)

            # print(f"Click performed!")
            return click_position

        except Exception as e:
            error_msg = f"Error processing image click {image_path.name}: {str(e)}"
            raise ArtemisError(error_msg) from e

        finally:
            # Restore original settings
            artemis_engine.PAUSE = original_pause

    def find_image_position(  # pylint: disable=too-many-positional-arguments
        self,
        image_label: str,
        images_folder: Union[str, Path] = "resource",
        confidence: float = 0.8,
        timeout: float = 5.0,
        region: Optional[Tuple[int, int, int, int]] = None,
        grayscale: bool = False,
        verbose: bool = False,
    ) -> Union[Tuple[int, int], bool]:
        """
        Finds the position of an image on the screen without clicking.

        Utility function to only locate an image without performing a click.
        Useful for checking element presence or getting coordinates.

        Args:
            image_label (str): Image file name.
            images_folder (Union[str, Path], optional): Images folder. Default: "images"
            confidence (float, optional): Confidence level. Default: 0.8
            timeout (float, optional): Timeout in seconds. Default: 5.0
            region (Optional[Tuple], optional): Search region. Default: None
            grayscale (bool, optional): Search in grayscale. Default: False

        Returns:
            Union[Tuple[int, int], bool]: Image center coordinates or False.
        """

        self._validate_parameters(confidence, timeout, 0.5, "left", region)
        image_path = self._resolve_image_path(image_label, images_folder)

        try:
            position = self._search_image_with_timeout(
                image_path=image_path,
                confidence=confidence,
                timeout=timeout,
                search_interval=0.5,
                region=region,
                grayscale=grayscale,
                verbose=verbose,
            )

            if position:
                if verbose:
                    success_print(f"Image found on position: {position}.")
                return self._calculate_click_position(position, click_center=True)
            return False

        except Exception as e:
            error_msg = f"Error searching for image {image_path.name}: {str(e)}"
            raise ArtemisError(error_msg) from e

    def _validate_parameters(  # pylint: disable=too-many-positional-arguments
        self,
        confidence: float,
        timeout: float,
        search_interval: float,
        click_button: str,
        region: Optional[Tuple[int, int, int, int]],
    ) -> None:
        """Validates function input parameters."""

        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, received: {confidence}")

        if timeout <= 0:
            raise ValueError(f"Timeout must be positive, received: {timeout}")

        if search_interval <= 0:
            raise ValueError(f"Search interval must be positive, received: {search_interval}")

        if click_button not in ["left", "right", "middle"]:
            raise ValueError(f"Click button must be 'left', 'right' or 'middle', received: {click_button}")

        if region is not None:
            if not isinstance(region, (tuple, list)) or len(region) != 4:
                raise ValueError("Region must be a tuple with 4 elements: (x, y, width, height)")

            if any(not isinstance(val, int) or val < 0 for val in region):
                raise ValueError("All region values must be non-negative integers")

    def _resolve_image_path(self, image_label: str, images_folder: Union[str, Path]) -> Path:
        """Resolves the full path to the image file."""

        folder_path = Path(images_folder)

        # If image_label already has extension, use directly
        if "." in image_label:
            image_path = folder_path / image_label
        else:
            # Try different common extensions
            extensions = [".png", ".jpg", ".jpeg", ".bmp", ".gif"]
            image_path = None

            for ext in extensions:
                candidate = folder_path / f"{image_label}{ext}"
                if candidate.exists():
                    image_path = candidate
                    break

            if not image_path:
                # If not found, use .png as default for clearer error
                image_path = folder_path / f"{image_label}.png"

        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        return image_path

    def _search_image_with_timeout(  # pylint: disable=too-many-branches,too-many-positional-arguments
        self,
        image_path: Path,
        confidence: float,
        timeout: float,
        search_interval: float,
        region: Optional[Tuple[int, int, int, int]],
        grayscale: bool,
        verbose: bool = False,
    ) -> Optional[any]:
        """Searches for image on screen with timeout, considering OpenCV availability."""

        start_time = time()
        attempts = 0

        while time() - start_time < timeout:
            attempts += 1

            try:
                # Build arguments for locateOnScreen based on OpenCV availability
                locate_args = {"image": str(image_path), "region": region, "grayscale": grayscale}

                # Add confidence only if OpenCV is available
                if OPENCV_AVAILABLE_FROM_ARTEMIS:
                    locate_args["confidence"] = confidence

                # Search for image on screen
                location = artemis_engine.locateOnScreen(**locate_args)

                if location:
                    if verbose:
                        print(f"Image found on attempt {attempts}.")
                    return location

            except artemis_engine.ImageNotFoundException:
                # Image not found in this attempt
                pass
            except TypeError as e:
                if "confidence" in str(e):
                    # Fallback if confidence error still occurs
                    alert_print("Confidence error detected, trying without parameter...")
                    try:
                        location = artemis_engine.locateOnScreen(str(image_path), region=region, grayscale=grayscale)
                        if location:
                            if verbose:
                                print(f"Image found on attempt {attempts} (without confidence): {location}")
                            return location
                    except Exception as error:
                        raise ArtemisError(f"Failed attempt without confidence: {error}.") from e
                else:
                    raise ArtemisError(f"Error during image search (attempt {attempts}): {e}") from e
            except Exception as e:
                raise ArtemisError(f"Error during image search (attempt {attempts}): {e}") from e

            # Wait before next attempt
            if time() - start_time < timeout:
                sleep(search_interval)

        if verbose:
            success_print(f"Search completed after {attempts} attempts in {timeout}s")
        return None

    def _calculate_click_position(self, image_box: any, click_center: bool) -> Tuple[int, int]:
        """Calculates the exact click position based on image location."""

        if click_center:
            # Click at image center
            center_x = image_box.left + image_box.width // 2
            center_y = image_box.top + image_box.height // 2
            return (center_x, center_y)
        # Click at top-left corner
        return (image_box.left, image_box.top)

    def _perform_click(
        self, position: Tuple[int, int], click_button: str, double_click: bool, verbose: bool = False
    ) -> None:
        """Performs click at specified position."""

        try:
            x, y = position

            # Move mouse to position (optional, but helps with visualization)
            artemis_engine.moveTo(x, y, duration=0.1)

            # Perform click
            if double_click:
                artemis_engine.doubleClick(x, y, button=click_button)
                if verbose:
                    success_print(f"Double click performed at ({x}, {y}) with {click_button} button.")
            else:
                artemis_engine.click(x, y, button=click_button)
                if verbose:
                    success_print(f"Click performed at ({x}, {y}) with {click_button} button.")
        except Exception as e:
            raise ArtemisError(f"Error performing click: {str(e)}.") from e

    # Convenience functions for specific cases
    def wait_and_click(  # pylint: disable=too-many-positional-arguments
        self,
        image_label: str,
        images_folder: Union[str, Path] = "resource",
        confidence: float = 0.8,
        timeout: float = 30.0,
        verbose: bool = False,
    ) -> Union[Tuple[int, int], bool]:
        """
        Waits for an image to appear on screen and clicks on it.

        Convenience function for waiting for elements that may take time to appear.
        """
        try:
            return self.click_image(
                image_label=image_label,
                images_folder=images_folder,
                confidence=confidence,
                timeout=timeout,
                search_interval=1.0,  # Longer interval for waiting
                verbose=verbose,
            )
        except Exception as e:
            raise ArtemisError(f"Error waiting and clicking: {str(e)}.") from e

    def quick_click(
        self, image_label: str, images_folder: Union[str, Path] = "resource", verbose: bool = False
    ) -> Union[Tuple[int, int], bool]:
        """
        Quick click with optimized default settings.

        Convenience function for fast clicks with balanced settings.
        """

        try:
            return self.click_image(
                image_label=image_label,
                images_folder=images_folder,
                confidence=0.8,
                timeout=3.0,
                search_interval=0.2,
                grayscale=True,  # Faster
                verbose=verbose,
            )
        except Exception as e:
            raise ArtemisError(f"Error performing quick click: {str(e)}.") from e
