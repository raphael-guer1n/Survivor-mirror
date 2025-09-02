import os

# Lis d'abord les variables d'env si tu veux (ex: via docker compose `environment:`)
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3327"))
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "jeb_incubator")

# Sécurité (tu pourras les réutiliser quand tu feras les JWT)
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))
