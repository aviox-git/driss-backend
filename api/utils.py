from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Custom exception handler for Django Rest Framework that adds
    the `status_code` to the response and renames the `detail` key to `error`.
    """
    response = exception_handler(exc, context)

    if response is not None:
        response.data['status'] = "error"
        response.data['message'] = response.data['detail']
        del response.data['detail']

    return response