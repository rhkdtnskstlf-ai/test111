import streamlit as st
from datetime import date, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import re
import time

st.title("호텔 최저가 자동 수집")

selected_date = st.date_input("날짜 선택", value=date.today())

checkin = selected_date.strftime("%Y-%m-%d")
checkout = (selected_date + timedelta(days=1)).strftime("%Y-%m-%d")

hotel_ids = {
    "파라다이스": "11576700",
    "파크하얏트": "31696883",
    "롯데": "11577921",
    "웨스틴조선": "11565526",
    "아난티 앳 부산 코브": "650968109",
    "시그니엘 부산": "1857519376",
    "그랜드 조선": "1016404332",
    "아바니 센트럴": "1431665023",
    "신라스테이 해운대": "791821570",
    "신라스테이 서부산": "1568839412",
    "농심 디럭스": "11555977",
    "농심 하이디럭스": "11555977"
}

def make_url(hotel_id):

    return f"https://hotels.naver.com/accommodation/search/detail/domestic/{hotel_id}/rates?dAdultCnt=2&dCheckIn={checkin}&dCheckOut={checkout}"

if st.button("최저가 수집 시작"):

    chrome_options = Options()

    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    chrome_options.binary_location = "/usr/bin/chromium"

    driver = webdriver.Chrome(options=chrome_options)

    results = []

    progress = st.progress(0)
    status = st.empty()

    hotels = list(hotel_ids.keys())

    for idx, hotel in enumerate(hotels):

        status.text(f"{hotel} 수집중...")

        if "하이디럭스" in hotel:

            results.append({
                "호텔": hotel,
                "최저가": "직접입력"
            })

            continue

        url = make_url(hotel_ids[hotel])

        driver.get(url)

        try:

            price_elements = WebDriverWait(driver,10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR,"div.common_PriceInfo__vuU30 em.common_price__iYQ6j")
                )
            )

            prices = []

            for el in price_elements:

                try:

                    num = int(re.sub("[^0-9]","",el.text))
                    prices.append(num)

                except:
                    pass

            if prices:

                results.append({
                    "호텔": hotel,
                    "최저가": min(prices)
                })

            else:

                results.append({
                    "호텔": hotel,
                    "최저가": "마감"
                })

        except:

            results.append({
                "호텔": hotel,
                "최저가": "마감"
            })

        progress.progress((idx+1)/len(hotels))

        time.sleep(1)

    driver.quit()

    df = pd.DataFrame(results)

    st.subheader("수집 결과")

    st.dataframe(df)
