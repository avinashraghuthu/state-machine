from django.http.response import JsonResponse


def init_response(res_str=None, data=None):
    """
    Initializes the response object
    both arguments are optional.
    """
    response = {}
    response["res_str"] = ""
    response["res_data"] = {}
    if res_str is not None:
        response["res_str"] = res_str
    if data is not None:
        response["res_data"] = data
    return response


def _send(data, status_code):
    return JsonResponse(data=data, status=status_code)


def send_200(data, res_str=''):
    if res_str:
        data['res_str'] = res_str
    return _send(data, 200)


def send_201(data):
    return _send(data, 201)


def send_400(data, res_str=''):
    if res_str:
        data['res_str'] = res_str
    return _send(data, 400)


def send_401(data):
    return _send(data, 401)

