#IMPORTS
from selenium import webdriver
from time import sleep
import plotly.graph_objects as go
from flask import Flask, render_template
import threading
import datetime
import smtplib
from email.message import EmailMessage
#https://skyzoominteractive.herokuapp.com

#BASE VARS
app = Flask(__name__)
app.config["SECRET_KEY"] = "5791628bb0b13ce0c676dfde280ba245"
global total_uses
total_uses = 0
class Object:
        def __init__(self, name,code, make_my_trip, yatra, start_time, end_time):
            self.name = name
            self.code = code
            self.start_time = start_time
            self.end_time = end_time
            self.make_my_trip = make_my_trip
            self.yatra = yatra
        def __repr__(self):
            return f"Name: {self.name}  S_Time: {self.start_time}  T_Time: {self.end_time}  MMT: {self.make_my_trip}  YAT: {self.yatra}"

def plot(list, numberal, email, dcode, lcode):
    AIRLINE_NAMES= []
    MMT = []
    YAT = []
    STI = []
    ETI = []
    CODE = []
    FROM = []
    TO = []
    for i in list:
        AIRLINE_NAMES.append(i.name)
        MMT.append(i.make_my_trip)
        YAT.append(i.yatra)
        STI.append(i.start_time)
        ETI.append(i.end_time)
        CODE.append(i.code)
        FROM.append(dcode)
        TO.append(lcode)
    fig = go.Figure(data=[go.Table(header=dict(values=['From', 'To', 'Airline',  'Code', 'Departure','Arrival','Yatra' , 'MakeMyTrip']),
                 cells=dict(values=[FROM, TO, AIRLINE_NAMES, CODE, STI,ETI, YAT, MMT]))
                     ])
    fig.write_image(numberal+ ".png")
    EMAIL = "kahanvora@gmail.com"
    PASS = "w0nderkid!"

    SEND_TO = email

    msg = EmailMessage()
    msg['Subject'] = 'SKYZoom!'
    msg['From'] = EMAIL
    msg['To'] = SEND_TO
    time = datetime.datetime.now()
    mit = time.strftime("%M")
    hou = time.strftime("%H")
    day = time.strftime(r"%d")
    msg.set_content(f"""
                    Departure Location: {dcode},\n 
                    Landing Location  : {lcode},\n 
                    Time taken        : {mit}.{hou}.{day},\n
            """)
    with open(numberal+".png", 'rb') as f:
        file = f.read()
        print(file)

    msg.add_attachment(file, maintype='image', subtype='.png', filename=numberal+".png")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL, PASS)
        smtp.send_message(msg)

def main_programm(DCODE, LCODE, DAY, MONTH, YEAR, EMAIL, numeral):
    PATH = 'chromedriver'
    options = webdriver.ChromeOptions()
    DCODE = str(DCODE)
    LCODE = str(LCODE)
    DAYS = str(DAY)
    MONTHS = str(MONTH)
    YEARS = str(YEAR)

    DATE = DAYS + "/" + MONTHS +"/" + YEARS
    DATE2 = DAYS +r"%2F" + MONTHS + r"%2F" + YEARS
    YBASE = f'https://flight.yatra.com/air-search-ui/dom2/trigger?type=O&viewName=normal&flexi=0&noOfSegments=1&origin={DCODE}&originCountry=IN&destination={LCODE}&destinationCountry=IN&flight_depart_date={DATE2}&ADT=1&CHD=0&INF=0&class=Economy&source=fresco-home'
    TBASE = f'https://www.makemytrip.com/flight/search?itinerary={DCODE}-{LCODE}-{DATE}&tripType=O&paxType=A-1_C-0_I-0&intl=false&cabinClass=E&ccde=IN&lang=eng'
    DRIVER = webdriver.Chrome(PATH, chrome_options=options)
    D2 = webdriver.Chrome(PATH, chrome_options=options)
    ALL_FLIGHTS = []
    UNNESCESARY = None
    DICT = {}
    #END

    #MAIN PYTHON CODE
    

    DRIVER.get(TBASE)
    sleep(10)
    fll = DRIVER.find_elements_by_class_name("fli-filter-items")
    fll = fll[2]
    box = fll.find_element_by_class_name("box")
    box.click()
    sleep(7)
    flights =DRIVER.find_elements_by_class_name("dept-options")


    D2.get(YBASE)
    sleep(100)
    options = D2.find_element_by_class_name("filter-stops")
    box = options.find_element_by_class_name("cursor-pointer")
    print(box.text)
    box.click()
    sleep(5)
    flights2 = D2.find_elements_by_class_name("flight-det")
    for i in flights2:
        fl_code = i.find_element_by_class_name("fl-no")
        price = i.find_element_by_class_name("fare-group")
        print(f"{fl_code}, {price}")
        DICT[fl_code.text] = price.text
    print(DICT)
    print(flights2)
    for f in flights:
        name = f.find_element_by_class_name("airways-name")
        start_time = f.find_element_by_class_name("dept-time")
        end_time = f.find_element_by_class_name("reaching-time")
        price1 = f.find_element_by_class_name("actual-price")
        code1 = f.find_element_by_class_name("fli-code")
        price2 = "NA"
        try:
            price2 = DICT[code1.text]
        except:
            continue
        object = Object(name.text, code1.text, price1.text, price2, start_time.text, end_time.text)
        ALL_FLIGHTS.append(object)
    DRIVER.quit()
    D2.quit()
    plot(ALL_FLIGHTS, numeral, EMAIL, DCODE, LCODE)

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/search/<string:dcode>/<string:lcode>/<int:day>/<int:month>/<int:year>/<string:email>/<string:num>")
def search(dcode, lcode, day, month, year, email, num):
    new_thread = threading.Thread(target=main_programm, args=[dcode, lcode, day, month , year, email, num])
    try:
        new_thread.start()
    except:
        pass
    global total_uses
    total_uses += 1
    return '"status": "sent"'

@app.route("/check")
def check():
    global total_uses
    return {"uses": str(total_uses)}

@app.route("/download")
def download():
    return render_template("download.html")
if __name__ == "__main__":
    app.run(debug=True)