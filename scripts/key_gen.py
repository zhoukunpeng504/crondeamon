#coding:utf-8
# write  by  zhou

import StringIO
from paramiko import  RSAKey,SSHException
import os

def gen_keys(key=""):
    """
    生成公钥 私钥
    """
    output = StringIO.StringIO()
    sbuffer = StringIO.StringIO()
    key_content = {}
    if not key:
        try:
            key = RSAKey.generate(2048)
            key.write_private_key(output)
            private_key = output.getvalue()
        except IOError:
            raise IOError('gen_keys: there was an error writing to the file')
        except SSHException:
            raise SSHException('gen_keys: the key is invalid')
    else:
        private_key = key
        output.write(key)
        try:
            key = RSAKey.from_private_key(output)
        except SSHException, e:
            raise SSHException(e)

    for data in [key.get_name(),
                 " ",
                 key.get_base64(),
                 " %s@%s" % ("magicstack", os.uname()[1])]:
        sbuffer.write(data)
    public_key = sbuffer.getvalue()
    key_content['public_key'] = public_key
    key_content['private_key'] = private_key
    return key_content

if __name__=="__main__":
    print gen_keys()