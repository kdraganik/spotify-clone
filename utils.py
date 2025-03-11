import bcrypt

def get_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_hash(password, hashed):
    return bcrypt.checkpw(password, hashed)