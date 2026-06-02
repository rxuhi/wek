from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# ==================================================
# 공공데이터 약 API KEY
# ==================================================
DATA_API_KEY = "d370bbfce6e54215f07e80a02f4d9a71c5c825df92b6b86cdd5539574317b681"

# ==================================================
# NEWS API KEY
# ==================================================
NEWS_API_KEY = "39d7499fd9ef42f081c77dc3c098d5f3" 

# ==================================================
# 에어코리아 API KEY
# ==================================================
AIR_API_KEY = "d370bbfce6e54215f07e80a02f4d9a71c5c825df92b6b86cdd5539574317b681"

# ==================================================
# 메인 페이지
# ==================================================
@app.route("/")
def home():
    return render_template("index.html")


# ==================================================
# 약 검색
# ==================================================
@app.route("/medicine-search", methods=["POST"])
def medicine_search():

    try:

        data = request.get_json()

        medicine_name = data.get("medicine")

        url = (
            f"https://apis.data.go.kr/1471000/"
            f"DrbEasyDrugInfoService/getDrbEasyDrugList"
            f"?serviceKey={DATA_API_KEY}"
            f"&itemName={medicine_name}"
            f"&type=json"
        )

        response = requests.get(url)

        result = response.json()

        body = result.get("body")

        if not body:
            return jsonify({
                "success": False,
                "message": "약 정보를 찾을 수 없습니다."
            })

        items = body.get("items")

        if not items:
            return jsonify({
                "success": False,
                "message": "검색 결과 없음"
            })

        medicine = items[0]

        item_name = medicine.get("itemName", "정보 없음")

        effect = medicine.get(
            "efcyQesitm",
            "효능 정보 없음"
        )

        use_method = medicine.get(
            "useMethodQesitm",
            "복용법 정보 없음"
        )

        warning = medicine.get(
            "atpnWarnQesitm",
            "주의사항 정보 없음"
        )

        result_text = f"""
💊 약 이름:
{item_name}

✅ 효능:
{effect}

💡 복용 방법:
{use_method}

⚠️ 주의사항:
{warning}
"""

        return jsonify({
            "success": True,
            "result": result_text
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })


# ==================================================
# 약 추천
# ==================================================
@app.route("/medicine-recommend", methods=["POST"])
def medicine_recommend():
    try:
        data = request.get_json()
        symptom = data.get("symptom")  # ← 이게 있어야 함

        prompt = f"""
사용자 증상: '{symptom}'

오늘 날짜 기준으로 이 증상에 맞는 일반의약품을 추천해주세요.
매번 다른 관점으로 답변해주세요.

다음 형식으로 답해주세요:

1. 추천 약품 이름 (성분명 포함)
2. 이 약이 도움이 되는 이유
3. 복용 시 주의할 점
4. 이런 경우엔 병원 방문 필요

추천 약품은 매번 다양하게 제시해주세요. 전문적이지만 쉽게 설명해주세요.
"""
        ai_result = call_groq(prompt)
        final_result = ai_result + f"\n\n{DISCLAIMER}"

        return jsonify({"success": True, "result": final_result})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
# ==================================================
# 건강 뉴스
# ==================================================
@app.route("/health-news")
def health_news():

    try:

        url = (
            f"https://newsapi.org/v2/top-headlines?"
            f"category=health&"
            f"country=kr&"
            f"apiKey={NEWS_API_KEY}"
        )

        response = requests.get(url)

        data = response.json()

        articles = data.get("articles", [])

        news_list = []

        for article in articles[:5]:

            news_list.append({
                "title": article.get("title"),
                "description": article.get("description"),
                "url": article.get("url")
            })

        return jsonify({
            "success": True,
            "news": news_list
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })


# ==================================================
# 미세먼지 정보
# ==================================================
@app.route("/air")
def air():

    try:

        url = (
            "http://apis.data.go.kr/B552584/"
            "ArpltnInforInqireSvc/"
            "getCtprvnRltmMesureDnsty"
        )

        params = {
            "serviceKey": AIR_API_KEY,
            "returnType": "json",
            "numOfRows": "5",
            "pageNo": "1",
            "sidoName": "서울",
            "ver": "1.0"
        }

        response = requests.get(url, params=params)

        print(response.text)

        data = response.json()

        items = data["response"]["body"]["items"]

        air_list = []

        for item in items[:5]:

            air_list.append({
                "station": item.get("stationName"),
                "pm10": item.get("pm10Value"),
                "pm25": item.get("pm25Value")
            })

        return jsonify({
            "success": True,
            "air": air_list
        })

    except Exception as e:

        print(e)

        return jsonify({
            "success": False,
            "message": str(e)
        })

# ==================================================
# 서버 실행
# ==================================================
if __name__ == "__main__":
    app.run(debug=True)
