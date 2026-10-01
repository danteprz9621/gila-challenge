import os

ENVIRONMENTS = ("dev", "prod")
API_URL = os.getenv("API_URL", "http://localhost:3000")
TARGET_ENV = os.getenv("TARGET_ENV", "dev")
VALID_TOKEN = os.getenv("API_TOKEN", "mysecrettoken")
