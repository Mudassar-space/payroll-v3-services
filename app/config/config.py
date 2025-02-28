
from decouple import config
from jwcrypto import jwk



PROJECT_NAME = "Payroll API"

# Load environment variable from .env file
MONGODB_CON_STR = config('MONGODB_CON_STR')
DATABASE_NAME = config('DATABASE_NAME')


JWT_SECRET = config('JWT_SECRET')
JWT_TOKEN_EXPIRE_MINUTES = 60 * 24 * 1  # 24 Hours or 1 day
JWT_ALGORITHM = config("JWT_ALGORITHM")
JWT_HEADER_ALGORITHM = config("JWT_HEADER_ALGORITHM")
JWT_HEADER_ENCODING = config("JWT_HEADER_ENCODING")
JWT_KEY = jwk.JWK(**{"k":JWT_SECRET,"kty":"oct"})


EMAIL_SENDER = config('email_sender')
EMAIL_PASSWORD = config('email_password')
SMTP_EMAIL = config('smtp_email')
SMTP_PORT = config('smtp_port')
FROM_EMAIL = config('from_email')

