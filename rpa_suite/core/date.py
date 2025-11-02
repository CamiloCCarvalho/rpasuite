# rpa_suite/core/date.py

# imports standard
import datetime as dt
from typing import Optional as Op
from typing import Tuple


class DateError(Exception):
    """Custom exception for Date errors."""

    def __init__(self, message):
        clean_message = message.replace("DateError:", "").strip()
        super().__init__(f"DateError: {clean_message}")


class Date:
    """
    Class that provides utilities for date manipulation and formatting.

    This class offers functionalities for:
        - Getting current time components (hours, minutes, seconds)
        - Date formatting and manipulation
        - Date validation and conversion

    Methods:
        get_hms: Returns current time as tuple of hour, minute, second
        get_dmy: Returns current date as tuple of day, month, year

    The Date class is part of RPA Suite and can be accessed through the rpa object:
        >>> from rpa_suite import rpa
        >>> hour, minute, second = rpa.date.get_hms()
        >>> day, month, year = rpa.date.get_dmy()
    """

    def __init__(self) -> None:
        """Initialize the Date class."""

    def get_hms(self) -> Tuple[Op[str], Op[str], Op[str]]:
        """
        Returns the current hour, minute, and second as a tuple of strings.

        The function formats values below 10 with leading zeros (e.g., "09" instead of "9").
        All individual values are returned as strings in two-digit format.

        Returns:
        --------
        Tuple[str, str, str]
            Tuple containing (hour, minute, second) as strings in format ('HH', 'MM', 'SS').

        Example:
        --------
        >>> hour, minute, second = get_hms()
        >>> print(f"{hour}:{minute}:{second}")  # Output: "14:30:45"
        """

        # Local Variables
        hours: str
        minutes: str
        seconds: str

        try:
            # Preprocessing
            now = dt.datetime.now()
            hours: str = str(now.hour) if now.hour >= 10 else f"0{now.hour}"
            minutes: str = str(now.minute) if now.minute >= 10 else f"0{now.minute}"
            seconds: str = str(now.second) if now.second >= 10 else f"0{now.second}"

            # Process
            try:
                if len(hours) == 3 or len(minutes) == 3 or len(seconds) == 3:
                    if len(seconds) == 3:
                        seconds[1:]  # pylint: disable=pointless-statement
                    if len(minutes) == 3:
                        minutes[1:]  # pylint: disable=pointless-statement
                    if len(hours) == 3:
                        hours[1:]  # pylint: disable=pointless-statement

                return hours, minutes, seconds

            except Exception as e:
                raise DateError(
                    f"Error trying process hours, minutes or seconds convert strings: [{hours}, {minutes}, {seconds}]! {str(e)}."
                ) from e
        except Exception as e:
            raise DateError(f"Error function: {self.get_hms.__name__}! {str(e)}.") from e

    def get_dmy(self) -> Tuple[Op[str], Op[str], Op[str]]:
        """
        Returns the current day, month, and year as a tuple of strings.

        The function formats values below 10 with leading zeros (e.g., "09" instead of "9").
        All individual values are returned as strings.

        Returns:
        --------
        Tuple[str, str, str]
            Tuple containing (day, month, year) as strings in format ('DD', 'MM', 'YYYY').

        Example:
        --------
        >>> day, month, year = get_dmy()
        >>> print(f"{day}/{month}/{year}")  # Output: "02/11/2024"
        """
        try:
            # Local Variables
            day_got: str
            month_got: str
            year_got: str

            # Preprocessing
            now = dt.datetime.now()

            # Process
            try:
                day_got: str = str(now.day) if now.day >= 10 else f"0{now.day}"
                month_got: str = str(now.month) if now.month >= 10 else f"0{now.month}"
                year_got: str = str(now.year) if now.year >= 10 else f"0{now.year}"

                return day_got, month_got, year_got

            except Exception as e:
                raise DateError(
                    f"Error trying process day, month or year convert strings: [{day_got}, {month_got}, {year_got}]! {str(e)}."
                ) from e
        except Exception as e:
            raise DateError(f"Error in function: {self.get_dmy.__name__}! {str(e)}.") from e
