# utils/datetime_helper.py
from datetime import datetime
import re
import os

class DateTimeHelper:
    """Helper class for datetime operations and filename sanitization"""

    @staticmethod
    def get_timestamp(format="%d-%m-%Y %H:%M:%S"):
        """Returns current timestamp in specified format"""
        return datetime.now().strftime(format)

    @staticmethod
    def get_filename_timestamp():
        """Returns timestamp formatted for filenames"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")