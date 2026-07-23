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

    The Date class is part of RPA Suite and can be accessed through the rpa object:
        >>> from rpa_suite import rpa
        >>> hour, minute, second = rpa.date.get_hms()

    """

    def __init__(self) -> None:
        """
        Class that provides utilities for date manipulation and formatting.

        This class offers functionalities for:
            - Getting current time components (hours, minutes, seconds)
            - Date formatting and manipulation
            - Date validation and conversion

        Methods:
            get_hms: Returns current time as tuple of hour, minute, second

        The Date class is part of RPA Suite and can be accessed through the rpa object:
            >>> from rpa_suite import rpa
            >>> hour, minute, second = rpa.date.get_hms()

        """

    def get_hms(self) -> Tuple[Op[str], Op[str], Op[str]]:
        """
        Function to return hour, minute and second. The return is in the form of a tuple with strings being able to store and use the values individually.

        Treatment:
        ----------
        The function already does the treatment for values below 10 always keeping 2 decimal places in all results, the individual values are always in string format

        Return:
        ----------
        >>> type:tuple
            * tuple('hh', 'mm', 'ss') - tuple with the values of hour, minute and second being able to be stored individually, the values are in string

        Example:
        ---------
        >>> hour, minute, second = get_hms() \n
            * NOTE:  Note that it is possible to destructure the return to store simultaneously.

        """

        try:
            now = dt.datetime.now()
            hours = f"{now.hour:02d}"
            minutes = f"{now.minute:02d}"
            seconds = f"{now.second:02d}"
            return hours, minutes, seconds
        except Exception as e:
            raise DateError(f"Error function: {self.get_hms.__name__}! {str(e)}.") from e

    def get_dmy(self) -> Tuple[Op[str], Op[str], Op[str]]:
        """
        Function to return day, month and year. The return is in the form of a tuple with strings being able to store and use the values individually.

        Return:
        ----------
        >>> type:tuple
            * tuple('dd', 'mm', 'yy') - tuple with the values of day, month and year being able to be stored individually

        Example:
        ---------
        >>> day, month, year = get_dmy() \n
            * NOTE:  Note that it is possible to destructure the return to store simultaneously.

        """
        try:
            now = dt.datetime.now()
            day_got = f"{now.day:02d}"
            month_got = f"{now.month:02d}"
            year_got = f"{now.year:04d}"
            return day_got, month_got, year_got
        except Exception as e:
            raise DateError(f"Error function: {self.get_dmy.__name__}! {str(e)}.") from e
