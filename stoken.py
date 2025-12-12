from itsdangerous import URLSafeTimedSerializer

secret_key = "Daimondsai"
salt = "saicharan"

def generate_token(payload):
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(payload, salt=salt)

def verify_token(token):
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.loads(token, salt=salt)
