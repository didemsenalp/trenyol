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
    return {"message":message,
            "success":success,
            "data":data}

def token_olustur():
   token = str(random.randint(1,100))
   return token

def gu_id_olustur():
    gu_id = uuid.uuid4()
    return gu_id

def check_token(token):
    check_user_with_token_query = "Select * From users where token = %s"
    check_user_with_token_result = g.cursor.execute(check_user_with_token_query,(token,))
    if check_user_with_token_result == 0:
        return get_anka_result("token kayitli degil",True,None)
        
    else:
        return get_anka_result("token kayitli",False,token)
    
  

@app.route("/UyeOlApi",methods = ["POST"])
def uye_ol_api():
    request_data = request.get_json()
    register_name = request_data["name"]
    register_email = request_data["email"]
    register_username = request_data["username"]
    register_password = request_data["password"]

    validate_uye_ol_result = validate_uye_ol(register_name,register_email,register_username,register_password)
    check_email_result = check_email(register_email)
    check_token_result = check_token(token)
    uye_ol_result = uye_ol(register_name,register_email,register_username,register_password,token,gu_id)


    if validate_uye_ol_result["success"] == True:
        if check_email_result["success"] == True:

            token = token_olustur()

            if check_token_result["success"] == True:

                gu_id = gu_id_olustur()
                
                if uye_ol_result["success"] == True:

                    return uye_ol_result
                else:
                    return uye_ol_result
            else:
                return check_token_result
        else:
            return check_email_result
    else:
        return validate_uye_ol_result

def validate_uye_ol(name,email,username,password):
    request_data = request.get_json()
    name = request_data["name"]
    email = request_data["email"]
    username = request_data["username"]
    password = request_data["password"]

    if name == None or name == "" or type(name) == int:
        return get_anka_result("isim bos",False,None)
    if email == None or email == "" or type(email) == int:
        return get_anka_result("eposta adresi bos",False,None)
    if username == None or username == "" or type(username) == int:
        return get_anka_result("username bos",False,None)
    if password == None or password == "":
        return get_anka_result("parola bos",False,None)
    return get_anka_result("Tüm degerler dogru girildi",True,None)

def uye_ol(register_name,register_email,register_username,register_password,token,gu_id):
    uye_ol_query = "Insert into users(name,email,username,password,token,musteri_id) VALUES(%s,%s,%s,%s,%s,%s)"
    
    uye_ol_result = g.cursor.execute(uye_ol_query,(register_name,register_email,register_username,register_password,token,gu_id))

    if uye_ol_result > 0:

        mysql.connection.commit()

        return get_anka_result("Kullanici kaydedildi",True,token)
    else:
        return get_anka_result("Kullanici kaydedilemedi",False,None)
    
def check_email(register_email):
    check_user_with_email_query = "Select * From users where email = %s"

    check_user_with_email_result = g.cursor.execute(check_user_with_email_query,(register_email,))

    if check_user_with_email_result == 0 :
        return get_anka_result("eposta adresi kayitli degil",True,None)
        
    else:
        return get_anka_result("eposta adresi sisteme kayitli.",False,register_email)


@app.route("/GirisYapApi",methods = ["POST"])
def giris_yap_api():
    request_data = request.get_json()
    entered_email = request_data["email"]
    entered_password = request_data["password"]

    validate_giris_yap_inputları_result = validate_giris_yap_inputları(entered_email,entered_password)
    if validate_giris_yap_inputları_result["success"] == True:
        check_mail_password_result = check_email_and_password(entered_email,entered_password)
        if check_mail_password_result["success"] == True:
            return check_mail_password_result
        else:
            return check_mail_password_result
    else:
        return validate_giris_yap_inputları_result
    
def validate_giris_yap_inputları(email,password):
    if email == None or email == "":
        return get_anka_result("Eposta adresi bos",False,None)
    if password == None or password == "":
        return get_anka_result("Parola bos",False,None)
    return get_anka_result("Degerler dogru",True,None)
    
def get_musterid_with_by_token(token):
    query_token = "Select * From users where token = %s"
    token_query_result = g.cursor.execute(query_token,(token,))

    if token_query_result >0 :
        register_information = g.cursor.fetchone()
        musteri_id = register_information["musteri_id"]
        return get_anka_result('Kullanici musteri id alindi.',True,musteri_id)
    else:
        return get_anka_result('Boyle bir kullanici bulunamadi.',False,None)

def check_email_and_password(email,password):
    check_email_query = "Select * From users where email = %s"

    check_email_result = g.cursor.execute(check_email_query,(email,))

    if check_email_result > 0 :
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

    validate_token_result = validate_token(token)
    get_musterid_with_by_token_result = get_musterid_with_by_token(token)
    validate_product_id_result = validate_product_id(product_id)
    urun_varmi_result = urun_varmi(product_id)
    musterinin_sepeti_var_mi_result = musterinin_sepeti_var_mi(musteri_id)

    if validate_token_result["success"] == True:
        if get_musterid_with_by_token_result["success"] == True:
            musteri_id = get_musterid_with_by_token(token)["data"]
            if validate_product_id_result["success"] == True:
                if urun_varmi_result["success"] == True:
                    if musterinin_sepeti_var_mi_result["success"] == True:
                        musteri_sepet_id= musterinin_sepeti_var_mi_result["data"]
                        sepete_urun_ekle_query = "Insert into cart_item(musteri_id,product_id,cart_id) VALUES(%s,%s,%s)"
                        sepete_urun_ekle_result = g.cursor.execute(sepete_urun_ekle_query,(musteri_id,product_id,musteri_sepet_id))
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
                    return urun_varmi_result
            else:
                return validate_product_id_result
        else:
            return get_musterid_with_by_token_result
    else:
        return validate_token_result
    
def validate_token(token):
    if token == None or token == "":
        return get_anka_result("token degeri yanlis",False,None)
    return get_anka_result("token degeri dogru",True,None)   

def validate_product_id(product_id):
    if product_id == None or product_id == "" or type(product_id) == str:
        return get_anka_result('Urun id yanlis',False,None)
    return get_anka_result('Urun id dogru',True,product_id)

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

@app.route("/SepetiGoruntuleApi",methods = ["GET"])
def sepeti_goruntule():
    token = request.headers.get('token')

    validate_token_result = validate_token(token)
    get_musterid_with_by_token_result = get_musterid_with_by_token(token)
    musterinin_sepeti_var_mi_result = musterinin_sepeti_var_mi(musteri_id)
    musterinin_sepetteki_urunlerini_getir_result =musterinin_sepetteki_urunlerini_getir(musteri_sepet_id)

    
    if validate_token_result["success"] == True:
        if get_musterid_with_by_token_result["success"] == True:
            musteri_id = get_musterid_with_by_token_result["data"]
            if musterinin_sepeti_var_mi_result["success"] == True:
                musteri_sepet_id = musterinin_sepeti_var_mi_result["data"]
                if musterinin_sepetteki_urunlerini_getir_result["success"] == True:
                    return musterinin_sepetteki_urunlerini_getir_result
                else:
                    return musterinin_sepetteki_urunlerini_getir_result
            else:
                return musterinin_sepeti_var_mi_result
        else:
            return get_musterid_with_by_token_result
    else:
        return validate_token_result

def musterinin_sepetteki_urunlerini_getir(musteri_id,sepet_id):
    query_sepetteki_urunleri_getir = "Select * From cart_item where musteri_id = %s AND cart_id = %s"

    sepetteki_urunleri_getir_result = g.cursor.execute(query_sepetteki_urunleri_getir,(sepet_id,))

    cart_item = g.cursor.fetchall()

    if sepetteki_urunleri_getir_result > 0:

        sepet_tutari = musterinin_sepet_tutarini_getir(musteri_id)["data"]

        return get_anka_result('Sepetteki urunler goruntulendi',True,["urunler:",cart_item,["sepet_tutari:",sepet_tutari]])
        
    else:
        
        return get_anka_result('Sepette urun bulunamadi',False,None)
    
def musterinin_sepet_tutarini_getir(musteri_id):
    query_musteri_sepeti = "Select * From cart_item where musteri_id = %s"

    result_musteri_sepeti = g.cursor.execute(query_musteri_sepeti,(musteri_id,))

    if result_musteri_sepeti > 0 :

        products_id_list = [item['product_id'] for item in g.cursor.fetchall()]

        sepet_tutari = 0

        for product_id in products_id_list :

            get_product_price_metodu = get_product_price(product_id)

            product_price = get_product_price_metodu["data"]

            sepet_tutari += product_price
        

        return get_anka_result("Sepet tutari hesaplandi.",True,sepet_tutari)
    else:
        return get_anka_result("Sepet tutari hesaplanamadi.",False,None)

def get_product_price(product_id):
    query_get_product_price = "Select * From products where product_id = %s"

    result_get_product_price = g.cursor.execute(query_get_product_price,(product_id,))

    product_data = g.cursor.fetchone()

    product_price = product_data["product_price"]

    if result_get_product_price > 0 :
        return get_anka_result("Urun fiyati bulundu",True,product_price)
    
    return get_anka_result("Urun fiyati bulunamadi",False,None)

@app.route("/KartBilgisiGir",methods = ["GET"])
def kart_bilgisi_gir():
    
    token = request.headers.get('token')
    request_data = request.get_json()
    credi_card_number = request_data["card_number"]
    
    
    validate_token_result = validate_token(token)
    if validate_token_result["success"] == True:
        get_musterid_with_by_token_result = get_musterid_with_by_token(token)
        if get_musterid_with_by_token_result["success"] == True:
            musteri_id = get_musterid_with_by_token_result["data"]
            validate_card_number_and_balance_result = validate_card_number_and_balance(musteri_id,credi_card_number)
            if validate_card_number_and_balance_result["success"] == True:
                return validate_card_number_and_balance_result
            else:
                kredi_kart_bilgileri_kaydet_result = kredi_kart_bilgileri_kaydet(musteri_id,credi_card_number)
                return kredi_kart_bilgileri_kaydet_result
        else:
            return get_musterid_with_by_token_result
    else:
        return validate_token_result
 
def validate_card_number_and_balance(musteri_id,card_number):
    if card_number == None or card_number == "" or type(card_number) == str or "card_number" == None:
        return get_anka_result('Kart numarasini dogru giriniz.',False,None)
    else:
        musterinin_kredi_karti_bu_mu_result = musterinin_kredi_karti_bu_mu(musteri_id,card_number)
        if musterinin_kredi_karti_bu_mu_result["success"] == True:
            return musterinin_kredi_karti_bu_mu_result
        else:
            return musterinin_kredi_karti_bu_mu_result

def musterinin_kredi_karti_bu_mu(musteri_id,credi_card_number):
    musterinin_kayitli_karti_bu_mu_query = "Select * From card_information where musteri_id = %s AND card_number = %s"

    musterinin_kayitli_karti_bu_mu_result = g.cursor.execute(musterinin_kayitli_karti_bu_mu_query,(musteri_id,credi_card_number))
    if musterinin_kayitli_karti_bu_mu_result > 0 :
        
        return get_anka_result('Kullanicinin karti bu',True,credi_card_number)
    else:
        return get_anka_result('Kullanicinin kayitli karti bu degil',False,None)

def kredi_kart_bilgileri_kaydet(musteri_id,credi_card_number):
    
    credi_card_balance = random.randint(100,10000)


    kart_kaydet_query = "Insert into card_information(musteri_id,card_number,card_balance) VALUES(%s,%s,%s)"

    kart_kaydet_query_result = g.cursor.execute(kart_kaydet_query,(musteri_id,credi_card_number,credi_card_balance))
    mysql.connection.commit()

    if kart_kaydet_query_result > 0:
        return get_anka_result('Kart bilgileri kaydedildi',True,None)
    else:
        return get_anka_result('Kart bilgileri kaydedilemedi',False,None)

@app.route("/OdemeYap",methods = ["GET"])
def odeme_yap():
    token = request.headers.get('token')
    request_data = request.get_json()
    credi_card_number = request_data["card_number"]

    validate_token_result = validate_token(token)
    if validate_token_result["success"] == True:
        get_musterid_with_by_token_result = get_musterid_with_by_token(token)
        if get_musterid_with_by_token_result["success"] == True:
            musteri_id = get_musterid_with_by_token(token)["data"]
            validate_card_number_and_balance_result = validate_card_number_and_balance(musteri_id,credi_card_number)
            if validate_card_number_and_balance_result["success"] == True:
                credi_card_number = validate_card_number_and_balance_result["data"]
                musterinin_sepet_tutarini_getir_result = musterinin_sepet_tutarini_getir(musteri_id)
                musteri_sepet_tutari = musterinin_sepet_tutarini_getir_result["data"]
                odeme_kart_bakiye_guncellemesi_result = odeme_kart_bakiye_guncellemesi(musteri_id,credi_card_number,musteri_sepet_tutari)

                return odeme_kart_bakiye_guncellemesi_result
            else:
                return validate_card_number_and_balance_result
        else:
            return get_musterid_with_by_token_result
    else:
        return validate_token_result

    
    

def odeme_kart_bakiye_guncellemesi(musteri_id,credi_card_number,musteri_sepet_tutari):
        kredi_karti_bakiye_query = "Select * From card_information where musteri_id = %s AND card_number = %s"

        kredi_karti_bakiye_result = g.cursor.execute(kredi_karti_bakiye_query,(musteri_id,credi_card_number))


        credi_card_data = g.cursor.fetchone()
        card_balance = credi_card_data["card_balance"]

        if card_balance >= musteri_sepet_tutari:
            yeni_bakiye = card_balance - musteri_sepet_tutari

            #Burdaki sorguyu gözden geçirmeyi unutma...

            kredi_karti_bakiye_guncelle_query = "Update card_information set card_balance = ? where card_number = ?"

            kredi_karti_bakiye_guncelle_result = g.cursor.execute(kredi_karti_bakiye_guncelle_query,(yeni_bakiye,))

            mysql.connection.commit()

            return get_anka_result("Odeme yapildi",True,None)
        else:
            return get_anka_result("Odeme yapilamadi",False,None)




app.run(debug=True)