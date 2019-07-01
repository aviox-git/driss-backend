from django.contrib.auth import authenticate

def jwt_get_username_from_payload_handler(payload):
    email = payload.get('email')
    authenticate(remote_user=email)
    return email