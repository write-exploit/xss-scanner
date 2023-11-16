from bs4 import BeautifulSoup
import re
import urllib.parse
import asyncio
import httpx
from termcolor import colored
import argparse

mesaj = '''
[+]---TURK-----HACK-----TEAM----[+]
[+]-----------yuathay-----------[+]
[+]-----------------------------[+]
'''
#==============================
parser = argparse.ArgumentParser(description='xss scanner',usage="tool kullanım rehberi")
parser.add_argument("-s", "--site", metavar="", type=str, help="hedef url",required=True)
parser.add_argument("-d", "--data",metavar="" ,nargs="+", help='(login olmadan alt sayfalarda gezinemediğiniz siteler için) form verilerini boşluklu bir şekilde girin örneğin : login=ahmet password=sifre123')
parser.add_argument("-l","--login",metavar="", type=str, help="login olunacak site")
args = parser.parse_args()
#==============================
print(mesaj)
print("sitede input alanı varmı e/h")
cevap = input()
#======================
#verilen payloadları düzenleme
def load_payloads(file_path): #burayı girmek zorundasın gibi bişey yaz
    with open(file_path, 'r') as file:
        global javascript_codes # değişkene kodun her tarafından ulaşabilmek için global adında bir değer kullanıyoruz
        javascript_codes =  [line.strip() for line in file]
load_payloads(r"C:\Users\ogulc\OneDrive\Masaüstü\visual\byfelez\payloads.txt") #payloads.txt
#=======================
if args.data:
    değişken = args.data
    global data
    data = {}
    for i in range(len(değişken)):
        key,value = str(değişken[i]).split("=") # ad=mustafa değerini {ad:mustafa} değerine dönüştürüyoruz siteye data değeri gönderirken bu şekilde parametre vermemiz lazım
        data[key] = value
#=======================
async def scan_url_for_xss(url):
    async with httpx.AsyncClient() as client:
        if args.data:        
            login = args.login
            await client.post(login,data=data) 
        for i in javascript_codes: 
            payload = url+i #url'ye javascript kodu ekliyoruz
        
            response = await client.get(payload)
            if response.status_code < 404: 
                
                içerik = response.text
                
                if i in içerik: 
                    print(colored(f"zafiyet mevcut kullanılan script : \n{payload}\n","red"))
                    
                else: #eğer yukarıdaki if blogundan herhangi bir sonuc alamadıysak payload'i encode edip site içinde encode edilmiş halini arıyoruz
                    metin = i
                    encode = urllib.parse.quote(metin) # payload encode işlemi
                    
                    if encode in içerik:
                        print(colored(f"zafiyet mevcut kullanılan script : \n{payload}\n","red"))
                        
                    else:
                        payload = url+i.upper() # eğer yukardaki if else bloklarından bir sonuç alamadıysak bu seferde payload'ı büyüterek gönderiyoruz
                        response = await client.get(payload)
                        if response.status_code < 404:
                            
                            içerik = response.text
                            
                            if i in içerik: #yeniden sayfada payload'ı araıyoruz
                                print(colored(f"zafiyet mevcut kullanılan script : \n{payload}\n","red"))
                                
                            else: #sayfada payload yoksa encode edip encode edilmiş halini arıyoruz
                                metin = i
                                encode = urllib.parse.quote(metin)
                                if encode in içerik:
                                    print(colored(f"zafiyet mevcut kullanılan script : \n{payload}\n","red"))
                        else:
                            continue

asyncio.run(scan_url_for_xss(args.site))
    
    
#sitede herhangi bir input alanı varmı varsa tarayalımmı ? diye bir soru sor yoksa bura çalışmaz
#buradaki değerleri büyük küçük şeklindede gönder


async def main(site):

    async with httpx.AsyncClient() as session:
        if args.data:
            login = args.login
            await session.post(login,data=data)     
        else:
            pass   
        #==============================

        response = await session.get(site)
        
        soup = BeautifulSoup(response.text,'html.parser')
        forms = soup.find_all("form")
        inputs = soup.find_all("input")
        
        global sözlük
        sözlük = {}
        for i in inputs:    
            try:
                re.search("id=",str(i)).group()
                if i['type'] != 'submit':
                    deger = "id"
            except:
                if i['type'] != 'submit':
                    deger = "name"
            try:           
                sözlük[i[deger]] = "" # başka bir döngüde buraya javascript payloadları yerleştirecez
            except:
                pass
            
        form = str(forms).split("</form>")
        global methodumuz
        methodumuz = ""
        for i in form:
            for keyler in sözlük.keys():
                key = keyler
                
                if key in i:
                    i = str(i).split()
                    for q in i:
                        if q.startswith("method"):
                            
                            if 'GET' in q:
                                methodumuz = "get"
                            else:
                                methodumuz = "post"
    
        #print(methodumuz) #yapılan isteğin method'u ---get--- veya ---post--- işleminden biri
        #print(sözlük) #burada data yada params ile göndereceğimiz değerlerin key'leri var, value olarakda javascript kodlarını vericez
        if methodumuz == "get":
            
            for o in javascript_codes:
                for anahtar in sözlük.keys():
                    sözlük[anahtar] = o # sözlük içinde ne gibi değerler var ?: {deger1: <script>alert('xss')</script>, deger2: <script>alert('xss')</script>} 
                                
                #PARAMS olarak gönderim yapıyoruz
                params_gönder = await session.get(site,params=sözlük)
                if params_gönder.status_code < 404:  #eğer 400'den aşağıda bir status code değeri varsa
                    if o in params_gönder.text: #eğer javascript kodları sayfanın içeriğindeyse
                        print(colored(f"[+] input alanında açık olma ihtimali var kullanılan script :\n{o}\n","green"))

        if methodumuz == "post":
            
            for o in javascript_codes:
                for anahtar in sözlük.keys():
                    sözlük[anahtar] = o # sözlük içinde ne gibi değerler var ?: {deger1: <script>alert('xss')</script>, deger2: <script>alert('xss')</script>} 

                for _ in range(1): 
                    
                    #????????????????????????????
                    #bu döngü neden var ?:
                    #eğer aşağıdaki iki koşuldan biri input alanında açık var çıktısını bize verirse break diyerek kodu durdurup ve gereksiz çalışmasını engelliycez 
                    #eğer bunu bu döngü içinde yapmasaydık sadece 1 kodumuz sadece 1 kere çalışır ve break ifadesini görünce sonlanırdı bu yüzden break ifadesini kullandık
                    #ardından diğer script'ler ile denemelerimize devam ediyoruz 
                    #????????????????????????????
                    
                    #===========================                    
                    #DATA olarak gönderim yapıyoruz
                    data_gönder = await session.post(site,data=sözlük)
                    if data_gönder.status_code < 404:
                        if o in data_gönder.text:
                            print(colored(f"[+] input alanında açık olma ihtimali var kullanılan script :\n{o}\n","green"))
                            break
                    #============================
                    #PARAMS olarak gönderim yapıyoruz
                    params_gönder = await session.post(site,params=sözlük)
                    if params_gönder.status_code < 404:
                        if o in params_gönder.text:
                            print(colored(f"[+] input alanında açık olma ihtimali var kullanılan script :\n{o}\n","green"))                    
                            break
cevap = cevap.lower()
if cevap == 'e':
    site = args.site
    asyncio.run(main(site))

