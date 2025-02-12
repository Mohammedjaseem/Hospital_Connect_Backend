import sys
from rest_framework.response import Response
from rest_framework import status
def handle_exception(e):
    exc_type, exc_obj, tb = sys.exc_info()
    line_no = tb.tb_lineno
    return Response({"status": False, "message": f"Error: {str(e)} at line {line_no}"}, status=status.HTTP_400_BAD_REQUEST)