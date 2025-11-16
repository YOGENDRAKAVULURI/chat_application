from itsdangerous import URLSafeTimedSerializer
secret_key='Daimondsai'
salt='saicharan'

def generate_token(data):
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(data, salt=salt)

def verify_token(data):
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.loads(data, salt=salt)