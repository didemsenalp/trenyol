from flask import Flask,request,jsonify,json
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
import random
from flask import g
import uuid
import re

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
    print(gu_id)
    return f"{gu_id}"

def check_musteri_id(musteri_id):
    check_user_with_musteri_id_query = "Select * From users where token = %s"
    check_user_with_musteri_id_result = g.cursor.execute(check_user_with_musteri_id_query,(musteri_id,))
    if check_user_with_musteri_id_result == 0:
        return get_anka_result("musteri id kayitli degil",True,None)
        
    else:
        return get_anka_result("musteri id kayitli",False,musteri_id)

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
    
    validate_uye_ol_result = validate_uye_ol(request_data)
    if validate_uye_ol_result["success"] == True:
        register_name = request_data["name"]
        register_email = request_data["email"]
        register_username = request_data["username"]
        register_password = request_data["password"]
        check_email_result = check_email(register_email)
        if check_email_result["success"] == True:

            token = token_olustur()
            check_token_result = check_token(token)

            if check_token_result["success"] == True:

                gu_id = gu_id_olustur()
                check_musteri_id_result = check_musteri_id(gu_id)
                if check_musteri_id_result["success"] == True:
                    uye_ol_result = uye_ol(register_name,register_email,register_username,register_password,token,gu_id)
                    if uye_ol_result["success"] == True:

                        return uye_ol_result
                    else:
                        return uye_ol_result
                else:
                    return check_musteri_id_result
            else:
                return check_token_result
        else:
            return check_email_result
    else:
        return validate_uye_ol_result

def validate_uye_ol(request_data):

    if "name" not in request_data or request_data["name"] == None or request_data["name"] == "" or type(request_data["name"]) == int:
        return get_anka_result("isim degeri yanlis girildi",False,None)
    isValid_result = isValid(request_data["email"])
    if "email" not in request_data or request_data["email"] == None or request_data["email"] == "" or type(request_data["email"]) == int or isValid_result["success"] == False:
        return get_anka_result("eposta adresi degeri yanlis girildi",False,None)
    if "username" not in request_data or request_data["username"] == None or request_data["username"] == "" or type(request_data["username"]) == int:
        return get_anka_result("username degeri yanlis girildi",False,None)
    if "password" not in request_data or request_data["password"] == None or request_data["password"] == "":
        return get_anka_result("parola degeri yanlis girildi",False,None)
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
    
    validate_giris_yap_result = validate_giris_yap(request_data)
    if validate_giris_yap_result["success"] == True:
        entered_email = request_data["email"]
        entered_password = request_data["password"]
        check_mail_password_result = check_email_and_password(entered_email,entered_password)
        if check_mail_password_result["success"] == True:
            return check_mail_password_result
        else:
            return check_mail_password_result
    else:
        return validate_giris_yap_result

regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

def isValid(email):
    if re.fullmatch(regex, email):
      return get_anka_result('Eposta adresi dogru girildi',True,None)
    else:
      return get_anka_result('Gecerli bir eposta adresi giriniz.',False,None)

def validate_giris_yap(request_data):
    if "email" not in request_data or "password" not in request_data or request_data["email"] == "" or request_data["password"] == "" :
        return get_anka_result('Degerler yanlis girildi.',False,None)
    isValid_result = isValid(request_data["email"])
    if isValid_result["success"] == False:
        return get_anka_result('Gecerli bir eposta adresi giriniz.',False,None)
    return get_anka_result('Degerler dogru girildi.',True,None)

    
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

    validate_token_result = validate_token(token)
    if validate_token_result["success"] == True:

        get_musterid_with_by_token_result = get_musterid_with_by_token(token)
        if get_musterid_with_by_token_result["success"] == True:

            musteri_id = get_musterid_with_by_token_result["data"]
            validate_product_id_result = validate_product_id(request_data)

            if validate_product_id_result["success"] == True:
                product_id = request_data["product_id"]

                urun_varmi_result = urun_varmi(product_id)
                if urun_varmi_result["success"] == True:

                    musterinin_sepeti_var_mi_result = musterinin_sepeti_var_mi(musteri_id)
                    if musterinin_sepeti_var_mi_result["success"] == True:

                        musteri_sepet_id= musterinin_sepeti_var_mi_result["data"]
                        
                        sepete_urun_ekle_result = sepete_urun_ekle(musteri_id,product_id,musteri_sepet_id)

                        return sepete_urun_ekle_result
                            
                    else:
                        sepet_olustur_result = sepet_olustur(musteri_id)
                        if sepet_olustur_result["success"] == True:

                            musteri_sepet_id = sepet_id_getir(musteri_id)["data"]

                            sepete_urun_ekle_result = sepete_urun_ekle(musteri_id,product_id,musteri_sepet_id)

                            return sepete_urun_ekle_result
                        else:
                            return sepet_olustur_result
                else:
                    return urun_varmi_result
            else:
                return validate_product_id_result
        else:
            return get_musterid_with_by_token_result
    else:
        return validate_token_result

#Token client ın girdiği bir data değil ama int kontrolü yapmak için yazdım.

def validate_token(token):
    if type(token) == int:
        return get_anka_result("token degeri yanlis",False,None)
    return get_anka_result("token degeri dogru",True,None)   

def validate_product_id(request_data):
    if "product_id" not in request_data or request_data["product_id"] == "" or type(request_data["product_id"]) == str:
        return get_anka_result('Urun id degeri yanlis girildi',False,None)
    return get_anka_result('Urun id degeri dogru girildi',True,None)

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
    
def sepet_id_getir(musteri_id):
    query_get_sepet_id = "Select * From cart where musteri_id = %s "

    result_get_sepet_id = g.cursor.execute(query_get_sepet_id,(musteri_id,))

    if result_get_sepet_id >0:

        musteri_sepet_info = g.cursor.fetchone()

        musteri_sepet_id = musteri_sepet_info["cart_id"]

        return get_anka_result('Musteriye sepet_id getirildi.',True,musteri_sepet_id)
    else:
        return get_anka_result('Musteriye sepet_id getirme basarisiz.',False,None)
    
def sepet_olustur(musteri_id):
    
    query_sepet_olustur = "Insert into cart(musteri_id) VALUES(%s)"

    sepet_olustur_result = g.cursor.execute(query_sepet_olustur,(musteri_id,))

    if sepet_olustur_result >0:
        mysql.connection.commit()
                
        return get_anka_result('Musteriye sepet olusturuldu',True,None)
    else: 
        return get_anka_result('Musteriye sepet olusturulamadi',False,None)

def sepete_urun_ekle(musteri_id,product_id,musteri_sepet_id):
    sepete_urun_ekle_query = "Insert into cart_item(musteri_id,product_id,cart_id) VALUES(%s,%s,%s)"
    sepete_urun_ekle_result = g.cursor.execute(sepete_urun_ekle_query,(musteri_id,product_id,musteri_sepet_id))
    if sepete_urun_ekle_result >0:
        mysql.connection.commit()

        return get_anka_result('Urun sepete eklendi',True,None)
    else:
        return get_anka_result('Urun sepete eklenemedi',False,None)
    
@app.route("/SepetiGoruntuleApi",methods = ["GET"])
def sepeti_goruntule():
    token = request.headers.get('token')

    validate_token_result = validate_token(token)
    if validate_token_result["success"] == True:
        get_musterid_with_by_token_result = get_musterid_with_by_token(token)
        if get_musterid_with_by_token_result["success"] == True:
            musteri_id = get_musterid_with_by_token_result["data"]
            musterinin_sepeti_var_mi_result = musterinin_sepeti_var_mi(musteri_id)
            if musterinin_sepeti_var_mi_result["success"] == True:
                musteri_sepet_id = musterinin_sepeti_var_mi_result["data"]
                musterinin_sepetteki_urunlerini_getir_result = musterinin_sepetteki_urunlerini_getir(musteri_id,musteri_sepet_id)
                if musterinin_sepetteki_urunlerini_getir_result["success"] == True:
                    musterinin_sepetteki_urunleri = musterinin_sepetteki_urunlerini_getir_result["data"]
                    musterinin_sepet_tutari = musterinin_sepet_tutarini_getir(musteri_id)["data"]
                    sepetteki_urunler_ve_sepet_tutari = {"urunler":musterinin_sepetteki_urunleri,"sepet_tutari":musterinin_sepet_tutari}
                    return sepetteki_urunler_ve_sepet_tutari
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

    sepetteki_urunleri_getir_result = g.cursor.execute(query_sepetteki_urunleri_getir,(musteri_id,sepet_id,))

    products_id_list = [item['product_id'] for item in g.cursor.fetchall()]


    if sepetteki_urunleri_getir_result > 0:


        return get_anka_result('Sepetteki urunler goruntulendi',True, products_id_list)
        
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

@app.route("/KartBilgisiGirApi",methods = ["GET"])
def kart_bilgisi_gir():
    
    token = request.headers.get('token')
    request_data = request.get_json()
    
    
    
    validate_token_result = validate_token(token)
    if validate_token_result["success"] == True:
        get_musterid_with_by_token_result = get_musterid_with_by_token(token)
        if get_musterid_with_by_token_result["success"] == True:
            musteri_id = get_musterid_with_by_token_result["data"]
            validate_card_number_result = validate_card_number(request_data)
            if validate_card_number_result["success"] == True:
                credi_card_number = request_data["card_number"]
                musterinin_kredi_karti_bu_mu_result = musterinin_kredi_karti_bu_mu(musteri_id,credi_card_number)
                if musterinin_kredi_karti_bu_mu_result["success"] == True:
                    return musterinin_kredi_karti_bu_mu_result
                else:
                    kredi_kart_bilgileri_kaydet_result = kredi_kart_bilgileri_kaydet(musteri_id,credi_card_number)
                    return kredi_kart_bilgileri_kaydet_result
            else:
                return validate_card_number_result        
        else:
            return get_musterid_with_by_token_result
    else:
        return validate_token_result
 
def validate_card_number(request_data):
    if "card_number" not in request_data or request_data["card_number"] == "" or type(request_data["card_number"]) == str :
        return get_anka_result('Kart numarasini dogru giriniz.',False,None)
    if len(str(request_data["card_number"])) != 16:
        return get_anka_result('16 haneli kart numarasini dogru giriniz.',False,None)
    return get_anka_result('Kart numarasini dogru girildi',True,request_data["card_number"])

def musterinin_kredi_karti_bu_mu(musteri_id,credi_card_number):
    musterinin_kayitli_karti_bu_mu_query = "Select * From card_information where musteri_id = %s AND card_number = %s"

    musterinin_kayitli_karti_bu_mu_result = g.cursor.execute(musterinin_kayitli_karti_bu_mu_query,(musteri_id,credi_card_number))
    if musterinin_kayitli_karti_bu_mu_result > 0 :
        
        return get_anka_result('Kullanicinin karti bu',True,None)
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


@app.route("/OdemeYapApi",methods = ["GET"])
def odeme_yap():
    token = request.headers.get('token')
    request_data = request.get_json()
    

    validate_token_result = validate_token(token)
    if validate_token_result["success"] == True:
        get_musterid_with_by_token_result = get_musterid_with_by_token(token)
        if get_musterid_with_by_token_result["success"] == True:
            musteri_id = get_musterid_with_by_token(token)["data"]
            validate_card_number_result = validate_card_number(request_data)
            if validate_card_number_result["success"] == True:
                credi_card_number = request_data["card_number"]
                musterinin_kredi_karti_bu_mu_result = musterinin_kredi_karti_bu_mu(musteri_id,credi_card_number)
                if musterinin_kredi_karti_bu_mu_result["success"] == True:
                    musterinin_sepet_tutarini_getir_result = musterinin_sepet_tutarini_getir(musteri_id)
                    if musterinin_sepet_tutarini_getir_result["success"] == True:
                        musteri_sepet_tutari = musterinin_sepet_tutarini_getir_result["data"]
                        
                        odeme_yap_result = odeme_yap(musteri_id,credi_card_number,musteri_sepet_tutari)
                        if odeme_yap_result["success"] == True:
                            musterinin_siparisini_siparis_tablosuna_ekle_result = musterinin_siparisini_siparis_tablosuna_ekle(musteri_id,musteri_sepet_tutari)
                            if musterinin_siparisini_siparis_tablosuna_ekle_result["success"] == True:

                                order_id = musteri_siparisinin_order_idsini_getir(musteri_id)["data"][0]

                                sepet_id = sepet_id_getir(musteri_id)["data"]
                                product_id_list = musterinin_sepetteki_urunlerini_getir(musteri_id,sepet_id)["data"]
                                for product_id in product_id_list:
                                    product_name = get_product_name_by_product_id(product_id)["data"]
                                    product_price = get_product_price(product_id)["data"]
                                
                                    musterinin_siparis_detayini_siparis_detay_tablosuna_ekle_result = musterinin_siparis_detayini_siparis_detay_tablosuna_ekle(order_id,product_name,product_price)
                                if musterinin_siparis_detayini_siparis_detay_tablosuna_ekle_result["success"] == True:
                                    sepetteki_urunleri_sil_result = sepetteki_urunleri_sil(musteri_id)
                                    return sepetteki_urunleri_sil_result
                                else:
                                    return musterinin_siparis_detayini_siparis_detay_tablosuna_ekle_result
                            else:
                                return musterinin_siparisini_siparis_tablosuna_ekle_result
                        else:
                            return odeme_yap_result
                    else:
                        return musterinin_sepet_tutarini_getir_result
                else:
                    return musterinin_kredi_karti_bu_mu_result
            else:
                return validate_card_number_result
        else:
            return get_musterid_with_by_token_result
    else:
        return validate_token_result
  
def odeme_yap(musteri_id,credi_card_number,musteri_sepet_tutari):
        kredi_karti_bakiye_query = "Select * From card_information where musteri_id = %s AND card_number = %s"

        kredi_karti_bakiye_result = g.cursor.execute(kredi_karti_bakiye_query,(musteri_id,credi_card_number))


        credi_card_data = g.cursor.fetchone()
        card_balance = credi_card_data["card_balance"]

        if card_balance >= musteri_sepet_tutari:
            yeni_bakiye = card_balance - musteri_sepet_tutari

            kredi_karti_bakiye_guncelle_query = "UPDATE card_information SET card_balance = %s WHERE musteri_id = %s AND card_number = %s"

            kredi_karti_bakiye_guncelle_result = g.cursor.execute(kredi_karti_bakiye_guncelle_query,(yeni_bakiye,musteri_id,credi_card_number))

            if kredi_karti_bakiye_guncelle_result > 0 :

                mysql.connection.commit()

                return get_anka_result("Odeme yapildi",True,None)
        else:
            return get_anka_result(f"Odeme yapilamadi. Bakiye: {card_balance}",False,None)
        
def musterinin_siparisini_siparis_tablosuna_ekle(musteri_id,order_price):
    musterinin_siparisini_siparis_tablosuna_ekle_query = "Insert into customer_orders(musteri_id,order_price) VALUES(%s,%s)"

    musterinin_siparisini_siparis_tablosuna_ekle_result = g.cursor.execute(musterinin_siparisini_siparis_tablosuna_ekle_query,(musteri_id,order_price))

    if musterinin_siparisini_siparis_tablosuna_ekle_result > 0:
        mysql.connection.commit()

        return get_anka_result('Siparis tablosuna siparisler eklendi',True,None)
    else:
        return get_anka_result('Siparis tablosuna siparisler ekleme basarisiz',False,None)

def musterinin_siparis_detayini_siparis_detay_tablosuna_ekle(order_id,product_name,product_price):
    musterinin_siparis_detayini_siparis_detay_tablosuna_ekle_query = "Insert into customer_orders_item(order_id,product_name,product_price) VALUES(%s,%s,%s)"

    musterinin_siparis_detayini_siparis_detay_tablosuna_ekle_result = g.cursor.execute(musterinin_siparis_detayini_siparis_detay_tablosuna_ekle_query,(order_id,product_name,product_price))

    if musterinin_siparis_detayini_siparis_detay_tablosuna_ekle_result > 0:
        mysql.connection.commit()

        return get_anka_result('Siparis detayı tabloya eklendi',True,None)
    else:
        return get_anka_result('Siparis detayını tabloya ekleme başarısız.',False,None)
    
    


def get_product_name_by_product_id(product_id):
    query_get_product_name_and_by_product_id = "Select * From products where product_id = %s"

    result_get_product_name_and_by_product_id = g.cursor.execute(query_get_product_name_and_by_product_id,(product_id,))

    product_data = g.cursor.fetchone()

    product_name = product_data["product_name"]

    if result_get_product_name_and_by_product_id > 0 :
        return get_anka_result("Urun ismi bulundu",True,product_name)
    else:
        return get_anka_result("Urun ismi bulunamadi",False,None)


def sepetteki_urunleri_sil(musteri_id):
    query_sepetteki_urunleri_sil = "Delete from cart_item where musteri_id = %s"

    result_sepetteki_urunleri_sil = g.cursor.execute(query_sepetteki_urunleri_sil,(musteri_id,))

    if result_sepetteki_urunleri_sil > 0:
        mysql.connection.commit()

        return get_anka_result('Sepet temizlendi',True,None)
    else:
        return get_anka_result('Sepet temizlenemedi',False,None)

def musteri_siparisinin_order_idsini_getir(musteri_id):
    query_get_order_id = "Select * From customer_orders where musteri_id = %s ORDER BY order_id DESC"

    result_get_order_id = g.cursor.execute(query_get_order_id,(musteri_id,))

    if result_get_order_id > 0:

        order_id_list = [item['order_id'] for item in g.cursor.fetchall()]

        return get_anka_result('Order id getirildi',True,order_id_list)
    else:
        return get_anka_result('Order id getirilemedi.',False,None)

@app.route("/SiparisiGoruntuleApi",methods = ["GET"])
def siparisi_goruntule():
    token = request.headers.get('token')


    validate_token_result = validate_token(token)
    if validate_token_result["success"] == True:
        get_musterid_with_by_token_result = get_musterid_with_by_token(token)
        if get_musterid_with_by_token_result["success"] == True:
            musteri_id = get_musterid_with_by_token_result["data"]
            musterinin_sepeti_var_mi_result = musterinin_sepeti_var_mi(musteri_id)
            if musterinin_sepeti_var_mi_result["success"] == True:
                
                order_id_list = musteri_siparisinin_order_idsini_getir(musteri_id)["data"]
                siparis = []
                siparis_listele_result = siparis_listele(siparis,order_id_list)
                return siparis_listele_result
            else:
                return musterinin_sepeti_var_mi_result
        else:
            return get_musterid_with_by_token_result
    else:
        return validate_token_result
    
def siparis_listele(siparis,order_id_list):
    for order_id in order_id_list:
        siparisi_goruntule_result = siparisi_goruntule(order_id)["data"]
        siparis.append(siparisi_goruntule_result)
    return get_anka_result("Siparisleriniz goruntulendi",True,siparis)

def siparisi_goruntule(order_id):
    siparis_detay_tablosunu_goruntule_query = "Select * From customer_orders_item where order_id = %s"

    siparis_detay_tablosunu_goruntule_result = g.cursor.execute(siparis_detay_tablosunu_goruntule_query,(order_id,))


    if siparis_detay_tablosunu_goruntule_result > 0:

        siparis_data = g.cursor.fetchall()

        return get_anka_result("Siparis detayları goruntulendi",True,siparis_data)
    else:
        return get_anka_result("Siparis detayları goruntulenemedi",False,None)
    

app.run(host="0.0.0.0")