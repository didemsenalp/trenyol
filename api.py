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

def get_anka_result(message,success,data):
    return {"message":message,"success":success,"data":data}

def token_olustur():
   token = str(random.randint(1,100))
   return token

def get_musterid_with_by_token(token):
    query_token = "Select * From users where token = %s"
    token_query_result = g.cursor.execute(query_token,(token,))

    if token_query_result >0 :
        register_information = g.cursor.fetchone()
        musteri_id = register_information["musteri_id"]
        return get_anka_result('Kullanici musteri id alindi.',True,musteri_id)
    else:
        return get_anka_result('Boyle bir kullanici bulunamadi.',False,None)

@app.route("/UyeOlApi",methods = ["POST"])
def uye_ol_api():
    request_data = request.get_json()
    register_name = request_data["name"]
    register_email = request_data["email"]
    register_username = request_data["username"]
    register_password = request_data["password"]


    if validation_uye_ol(register_email)["data"] == None:

        token = token_olustur()

        if validation_token(token)["data"] == None:

            gu_id = uuid.uuid4()

            print(gu_id)

            uye_ol_query = "Insert into users(name,email,username,password,token,musteri_id) VALUES(%s,%s,%s,%s,%s,%s)"
            g.cursor.execute(uye_ol_query,(register_name,register_email,register_username,register_password,token,gu_id))
                
            mysql.connection.commit()

            return get_anka_result("Kullanici kaydedildi",True,token)
        else:
            return get_anka_result("token kayitli",False,token)
    else:
       return get_anka_result("eposta adresi sisteme kayitli.",True,register_email)

def validation_token(token):
    find_user_with_token_query = "Select * From users where token = %s"
    find_user_with_token_result = g.cursor.execute(find_user_with_token_query,(token,))
    if find_user_with_token_result == 0:
        return get_anka_result("token kayitli degil",True,None)
        
    else:
        return get_anka_result("token kayitli",False,token)
    
def validation_uye_ol(register_email):
    find_user_with_email_query = "Select * From users where email = %s"

    find_user_with_email_result = g.cursor.execute(find_user_with_email_query,(register_email,))

    if find_user_with_email_result == 0 :
        return get_anka_result("eposta adresi kayitli degil",True,None)
        
    else:
        return get_anka_result("eposta adresi sisteme kayitli.",True,register_email)

@app.route("/GirisYapApi",methods = ["POST"])
def giris_yap_api():
    request_data = request.get_json()
    entered_email = request_data["email"]
    entered_password = request_data["password"]

    if validation_email_and_password(entered_email,entered_password)["success"] == True:
        return get_anka_result('Basariyla giris yapildi.',True,None)
    else:
        return get_anka_result('Giris yapilamadi.',False,None)

def validation_email_and_password(email,password):
    validation_email_query = "Select * From users where email = %s"

    validation_email_result = g.cursor.execute(validation_email_query,(email,))

    if validation_email_result > 0 :
        register_data = g.cursor.fetchone()
        register_user_password = register_data["password"]
        if password == register_user_password:
            
            return get_anka_result('Basariyla giris yapildi.',True,None)

        else:
            return get_anka_result('Parola yanlis.',False,None)
    else:
         
        return get_anka_result('Eposta adresi kayitli degil',False,None)
    
@app.route("/KatalogUrunleriGoruntuleApi",methods = ["GET"])
def katalog_urunleri_goruntule():
    
    prdocuts_query = "Select * From products"

    prdocuts_query_result = g.cursor.execute(prdocuts_query)
    products = g.cursor.fetchall()

    if prdocuts_query_result > 0:
        
        return get_anka_result('Urunler goruntulendi',True,products)
    else:
        
        return get_anka_result('Urunler goruntulenemedi',False,None)
    
@app.route("/SepeteUrunEkleApi",methods = ["GET"])
def sepete_urun_ekle():
    token = request.headers.get('token')
    request_data = request.get_json()
    product_id = request_data["product_id"]
    if get_musterid_with_by_token(token)["success"] == True:
        musteri_id = get_musterid_with_by_token(token)["data"]
        if urun_varmi(product_id)["success"] == True:
            if musterinin_sepeti_var_mi(musteri_id)["success"] == True:
                musteri_sepet_id= musterinin_sepeti_var_mi(musteri_id)["data"]
                sepete_urun_ekle_query = "Insert into cart_item(musteri_id,product_id) VALUES(%s,%s)"
                sepete_urun_ekle_result = g.cursor.execute(sepete_urun_ekle_query,(musteri_id,product_id))
                if sepete_urun_ekle_result >0:
                    mysql.connection.commit()
                    return get_anka_result('Urun sepete eklendi',True,musteri_sepet_id)
                else:
                    return get_anka_result('Urun sepete eklenemedi',False,None)
            else:
                musteri_sepet_id = sepet_olustur(musteri_id)["data"]
                sepete_urun_ekle_query = "Insert into cart_item(musteri_id,product_id) VALUES(%s,%s)"
                sepete_urun_ekle_result = g.cursor.execute(sepete_urun_ekle_query,(musteri_id,product_id))
                if sepete_urun_ekle_result >0:
                    mysql.connection.commit()
                    return get_anka_result('Urun sepete eklendi',True,musteri_sepet_id)
                else:
                    return get_anka_result('Urun sepete eklenemedi',False,None)
        else:
            return get_anka_result('Urun yok',False,None)
    else:
            return get_anka_result('Kullanici yok',False,None)
            
        
def urun_varmi(product_id):

    urun_varmi_query = "Select * From products where product_id = %s"

    urun_varmi_result = g.cursor.execute(urun_varmi_query,(product_id,))
    if urun_varmi_result > 0 :
        
        return get_anka_result('Urun var.',True,None)
    else:
        
        return get_anka_result('Urun yok.',False,None)



def musterinin_sepeti_var_mi(musteri_id):
    query_musterinin_sepeti_varmi = "Select * From cart where musteri_id = %s "

    musterinin_sepeti_varmi_result = g.cursor.execute(query_musterinin_sepeti_varmi,(musteri_id,))

    if musterinin_sepeti_varmi_result > 0:

        musteri_sepet_info = g.cursor.fetchone()

        musteri_sepet_id = musteri_sepet_info["cart_id"]

        return get_anka_result('Musterinin sepeti var',True,musteri_sepet_id)
    else:
        return get_anka_result('Musterinin sepeti yok',False,None)
    
def sepet_olustur(musteri_id):
    
    query_sepet_olustur = "Insert into cart(musteri_id) VALUES(%s)"

    sepet_olustur_result = g.cursor.execute(query_sepet_olustur,(musteri_id,))

    if sepet_olustur_result >0:
        mysql.connection.commit()

        musteri_sepet_info = g.cursor.fetchone()

        musteri_sepet_id = musteri_sepet_info["cart_id"]
            
        return get_anka_result('Musteriye sepet olusturuldu',True,musteri_sepet_id)
    else: 
        return get_anka_result('Musteriye sepet olusturulamadi',False,None)
        
app.run(debug=True)