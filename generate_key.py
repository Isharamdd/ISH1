from cryptography.fernet import Fernet

# Generate encryption key
key = Fernet.generate_key()

# Save the key to a file
with open("encryption_key_user1.key", "wb") as key_file:
    key_file.write(key)

print("Encryption key generated and saved as 'encryption_key_user1.key'")
