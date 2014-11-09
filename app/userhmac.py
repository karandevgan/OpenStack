import hmac
from hashlib import sha1

def calculateHMACSignature(path, redirect, max_file_count, max_file_size, expires):
    key = 'secretkey'
    hmac_body = '%s\n%s\n%s\n%s\n%s' % (path, redirect, max_file_size, max_file_count, expires)
    return hmac.new(key, hmac_body, sha1).hexdigest()