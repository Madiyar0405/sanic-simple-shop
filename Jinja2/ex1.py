import secrets

# Генерируем случайную строку из 64 символов (512 бит) в шестнадцатеричном формате
random_secret_key = secrets.token_hex(32)
print(random_secret_key)
