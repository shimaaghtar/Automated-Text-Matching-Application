
import sys

class ProjectException(Exception):
    def __init__(self, message, error):
        """
        Custom exception class that captures and formats error messages.
        
        :param message: Custom error message
        :param error: Original exception instance
        """
        super().__init__(message)
        self.error = error  # Store the original exception

    def __str__(self):
        """
        Returns a formatted string representation of the exception.
        """
        return f"{self.__class__.__name__}: {self.args[0]} | Original Error: {str(self.error)}"

    def get_exception_details(self):
        """
        Returns the full exception details, including type and traceback.
        """
        return f"{self.__class__.__name__}: {self.args[0]} | Type: {type(self.error).__name__} | Traceback: {str(self.error)}"       
