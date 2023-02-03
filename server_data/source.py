import base64
import codecs
import hashlib
import sqlite3

from Crypto import Random
from Crypto.Cipher import AES
from flask import Flask, request

app = Flask(__name__)


@app.route("/", methods=["GET"])
def main():
    return "<b>Welcome to the Picus Cyber Talent Academy Homework!<br>" \
           "Find the bugs and create an exploit that can automatically get RCE.</b>"


@app.route("/<string:torch>", methods=["GET"])
def picus_torch(torch):
    return "Picus loves to go the MOON with " + torch


@app.route("/", methods=["POST"])
def old_torch_was_not_too_hot():
    try:
        value = request.form.get('fire')
        if value is not None:
            rot13_value = codecs.encode(value, 'rot_13')
            print(rot13_value)
            if rot13_value == "ayberk":
                return "Not like this :)"
            my_password = get_password(rot13_value)
            return "Picus loves to go the MOON with " + str(my_password)
    except Exception as exp:
        return str(exp)
    return "Try more to find users password :)"


def get_password(name):
    con = sqlite3.connect("picus.db")
    cur = con.cursor()
    #cur.execute("select password from users where name = '%s';" % name)
    cur.execute("select password from users where name = ?;", (name,))

    password = str(cur.fetchall())
    con.close()
    return password


@app.route("/add_user", methods=["GET"])
def save_user():
    id = request.args.get('id')
    username = request.args.get('username')
    password = request.args.get('password')
    file = open('./key.txt', "r")
    data = file.read()
    file.close()
    if data != "":
        encryptor = AESCipher(key=data)
        encrypted_data = encryptor.encrypt(password)
        con = sqlite3.connect("picus.db")
        con.row_factory = lambda cursor, row: row[0]
        cur = con.cursor()
        ids = cur.execute('SELECT id FROM users').fetchall()
        names = cur.execute('SELECT name FROM users').fetchall()

        if username in names or int(id) in ids:
            return "Username or ID is not unique"

        cur.execute("INSERT INTO users VALUES(?, ?, ?)",
                    (id, username, encrypted_data))
        cur.execute("Select * from users;")
        con.commit()
        con.close()
        return "Done!"
    return "Not done sorry :("


@app.route("/read_file")
def read_file():
    try:
        filename = request.args.get('filename')
        tempFileName = ""
        while True:
            tempFileName = filename.replace('.db', '').replace(
                '.py', '').replace('/', '').replace('..', '')
            if tempFileName != filename:
                filename = tempFileName
                continue
            break

        file = open(filename, "r")
        data = file.read()
        file.close()
        return data
    except Exception:
        return "wrong filename sorry :("


class AESCipher(object):

    def __init__(self, key):
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8081)
