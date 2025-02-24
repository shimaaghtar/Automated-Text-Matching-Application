
''''
class ProjectException(Exception):
    def __init__(self,error_message,error_datails:sys):
        self.error_message = error_message
        _,_,exec_tb = error_datails.exc_info()

        self.lineno = exec_tb.tb_lineno
        self.file_name = exec_tb.tb_frame.f_code.co_filename

    def __str__(self):
        return "Error occured in python script name [{0}] line number [{1}] error message [{2}]".format(
        self.file_name, self.lineno, str(self.error_message))
''' 
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