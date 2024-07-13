from OpenSSL import crypto
from cryptography.hazmat.primitives import serialization

# Create a new PKey object
secret_key = crypto.PKey()

# Generate a key pair of type RSA with 2048 bits
secret_key.generate_key(crypto.TYPE_RSA, 2048)

# Convert the PKey to a cryptography key
cryptography_key = secret_key.to_cryptography_key()

# Serialize the private key to PEM format
pem_private_key = cryptography_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)

# Print the private key in PEM format
print(pem_private_key.decode('utf-8'))

# Serialize the public key to PEM format
public_key = cryptography_key.public_key()
pem_public_key = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Print the public key in PEM format
print(pem_public_key.decode('utf-8'))
