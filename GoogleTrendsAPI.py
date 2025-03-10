from fastapi import FastAPI, Request

from fastapi.responses import JSONResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import time

from country_code import countries


def reloadWebDriver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--headless")
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument("--no-sandbox")  
    options.add_argument("--disable-dev-shm-usage")  
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


driver = reloadWebDriver()
app = FastAPI()


async def generate_link(request:Request) ->str:
    request = await request.json()
    use_country = "DE"
    use_time = 48
    use_category = "18"


    country = request.get("country")
    filter_time = request.get("time")
    category = request.get("category")
    active = request.get("active")

    if country:
        if countries.get(country):
            use_country = countries[country]
        
    baseLink = f"https://trends.google.com/trending?geo={use_country}&sort=search-volume"

    if filter_time:

        times = [7, 24, 48, 168]

        if filter_time in times:
            use_time = filter_time

    baseLink+= f"&hours={use_time}"

    if category:

        categories = {
            "technology": 18,
            "autos and vehicles": 1,
            "beauty and fashion ":2,
            "business and finance":3,
            "climate":20,
            "entertainment":4,
            "jobs and education":9,
            "games":6,
            "law and government":10,
            "science":15,
        }

        if categories[category]:

            use_category = categories[category]

    baseLink+= f"&category={use_category}"

    if active:

        if active == True:
            baseLink+= "&status=active"

    return baseLink



@app.post("/")
async def RequestTrends(request:Request):
    print(request.headers.get('Content-Type'))
    print(1)
    if (request.headers.get('Content-Type') != "application/json"):
        content = await getTrends()
        return content
    

    try:
        link = await generate_link(request)
    except:
        return JSONResponse(
        status_code=400,
        content={"message": "Request has to be Json formated"}
    )

    content = await getTrends(link)
    return content

async def getTrends(link:str = "https://trends.google.com/trending?geo=DE&sort=search-volume&category=18&hours=48&status=active"):

    info = {"generated_link": link}
    
    driver.get(link)

    time.sleep(2)
    topics = driver.find_elements(By.CLASS_NAME, "mZ3RIc")

    for i in topics:
        top_stories = []
        
        i.click()
        
        time.sleep(1)
        links = driver.find_elements(By.CLASS_NAME, "xZCHj")

        for j in links:
            link_info = j.text.split("\n")
            date = link_info[1].split("●")[0].strip()
            web = link_info[1].split("●")[1].strip()
            title = {
                "title": link_info[0],
                "time": date,
                "Publishing  website":web,
                "link": j.get_attribute('href')
            }
            top_stories.append(title)

        data = {"news": top_stories}
        info[i.text] = data
    return info

        



    