# utility class for decrypt partner CIPRES's user password
# install dependency: pip install pycrypto

from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256, SHA512, HMAC
from Crypto.Cipher import AES
from Crypto import Random
from paywall2 import settings

import base64, hmac, hashlib, codecs

class AESCipher(object):

    def __init__(self): 
        # constants for secret key
        self.clientSecret = settings.CIPHER_CLIENT_SECRET
        self.salt = settings.CIPHER_SALT
        self.iteration = settings.CIPHER_ITERATION
        self.keyLength = 32 # in bytes, = 256 bits
        # constants for decrpytion
        self.mode = AES.MODE_CBC
        self.blockSize = AES.block_size # 16 bytes

    def getKey(self):
        key = hashlib.pbkdf2_hmac(
            'sha512', # The hash digest algorithm for HMAC
            bytearray(self.clientSecret),
            base64.urlsafe_b64decode(self.salt + b'==='), # handles padding issue
            self.iteration, # It is recommended to use at least 100,000 iterations of SHA-256 
            self.keyLength # Get a 128 byte key
        )
        # print base64.b64encode(key)
        return key

    def encrypt(self, raw):
        secretKey = self.getKey()
        raw = self._pad(raw)
        iv = Random.new().read(self.blockSize)
        cipher = AES.new(secretKey, self.mode, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode('utf-8')))

    # throws TypeError for incorrect padded encryptedMsg
    def decrypt(self, encryptedMsg):
        secretKey = self.getKey()
        msgArray = base64.b64decode(encryptedMsg + b'===') # handles padding issue
        iv = msgArray[:self.blockSize]
        cipher = AES.new(secretKey, self.mode, iv)

        return self._unpad(cipher.decrypt(msgArray[self.blockSize:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.blockSize - len(s) % self.blockSize) * chr(self.blockSize - len(s) % self.blockSize)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

def test():
    cipher = AESCipher()
    # test encryption
    raw = "PW@666.cipres"
    encryptedMsg = cipher.encrypt(raw)
    print raw
    print encryptedMsg
    print cipher.decrypt(encryptedMsg)




