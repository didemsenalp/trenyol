from flask import Flask,request,jsonify,json
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
import random
from flask import request,g
import uuid

app = Flask(__name__)

app.secret_key="trenyol123"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "trenyol"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

@app.before_request
def before_request():
    g.conn = mysql.connection
    g.cursor = g.conn.cursor()

def token_olustur():
   token = str(random.randint(1,100))
   return token

def get_anka_result(message,success,data):
    return {"message":message,"success":success,"data":{data}}

def validation_uye_ol(register_email):
    find_user_with_email_query = "Select * From users where email = %s"

    find_user_with_email_result = g.cursor.execute(find_user_with_email_query,(register_email,))

    if find_user_with_email_result == 0 :
        return get_anka_result("eposta adresi kayitli degil",True,None)
        
    else:
        return get_anka_result("eposta adresi sisteme kayitli.",True,register_email)
    
@app.route("/UyeOlApi",methods = ["POST"])

def uye_ol_api():
    request_data = request.get_json()
    register_name = request_data["name"]
    register_email = request_data["email"]
    register_username = request_data["username"]
    register_password = request_data["password"]


    if validation_uye_ol(register_email)["data"] == {None}:

        token = token_olustur()

        if validation_token(token)["data"] == {None}:

            gu_id = uuid.uuid4()

            print(gu_id)

            uye_ol_query = "Insert into users(name,email,username,password,token,musteri_id) VALUES(%s,%s,%s,%s,%s,%s)"
            g.cursor.execute(uye_ol_query,(register_name,register_email,register_username,register_password,token,gu_id))
                
            mysql.connection.commit()
        else:
            return validation_token(token) 
    else:
        return get_anka_result()["message"]

def validation_token(token):
    find_user_with_token_query = "Select * From users where token = %s"
    find_user_with_token_result = g.cursor.execute(find_user_with_token_query,(token,))
    if find_user_with_token_result == 0:
        return get_anka_result("token kayitli degil",True,None)
        
    else:
        return get_anka_result("token kayitli",False,token)

app.run(debug=True)