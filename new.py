import bcrypt
bcrypt.hashpw(b"12345", bcrypt.gensalt())
