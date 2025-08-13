import base64
import uuid
from cryptography.hazmat.primitives import serialization



def generate_uuid():
    return str(uuid.uuid4())

def _b64url_nopad(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')


def generate_jwk(private_key, key_id: str):
    '''Generate a JWK (JSON Web Key) from a private key.

    Example usage:
    private = ed25519.Ed25519PrivateKey.generate()
    public_key_pem = private.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    # Export private key in PEM (PKCS8)
    private_key_pem = private.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    with open(f"keys/{wallet_id}/private_key.pem", "w") as f:
        f.write(private_key_pem)
        f.close()
    with open(f"keys/{wallet_id}/public_key.pem", "w") as f:
        f.write(public_key_pem)
        f.close()
    kid = uuid.uuid4()
    result_jwk = generate_jwk(private, f'keyid-{kid}')
    '''
    if not key_id.strip():
        raise ValueError('KeyId cannot be empty')
    if private_key is None:
        raise ValueError('private key cannot be empty')

    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    jwk = {
        'kty': 'OKP',
        'crv': 'Ed25519',
        'x': _b64url_nopad(public_bytes)
    }
    if jwk.get('x') is None:
        raise ValueError('Failed to derive public key')
    if jwk['crv'] != 'Ed25519' or jwk['kty'] != 'OKP' or not jwk['x']:
        raise ValueError('Key is not EdDSA-Ed25519')

    return {
        'alg': 'EdDSA',  # Alg.EdDsa
        'kid': key_id,
        'kty': 'OKP',  # Kty.Okp
        'crv': 'Ed25519',  # Crv.Ed25519
        'x': jwk['x']
    }




