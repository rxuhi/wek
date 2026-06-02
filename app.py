from flask import Flask, render_template, request, jsonify
import requests
import random
import os

app = Flask(__name__)

# ==================================================
# API Keys
# ==================================================
DATA_API_KEY = os.environ.get("DATA_API_KEY", "d370bbfce6e54215f07e80a02f4d9a71c5c825df92b6b86cdd5539574317b681")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "39d7499fd9ef42f081c77dc3c098d5f3")
AIR_API_KEY  = os.environ.get("DATA_API_KEY", "d370bbfce6e54215f07e80a02f4d9a71c5c825df92b6b86cdd5539574317b681")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")


# ==================================================
# 면책 문구
# ==================================================
DISCLAIMER = "※ 본 정보는 참고용입니다. 의약품 복용 전 반드시 전문가(의사·약사)와 상담하세요."


# ==================================================
# 미세먼지 농도별 랜덤 코멘트
# ==================================================
AIR_COMMENTS = {
    "좋음": [
        "오늘은 공기가 맑습니다. 외출 후 손 씻기를 잊지 마세요.",
        "야외 활동하기 좋은 날입니다. 돌아와서 물 한 잔으로 몸을 챙겨보세요.",
        "맑은 공기 덕분에 기분이 한결 가볍습니다. 산책 후 가벼운 스트레칭을 해보세요.",
    ],
    "보통": [
        "큰 문제는 없지만 민감한 분들은 마스크를 챙기는 것이 좋습니다.",
        "공기가 무난한 편입니다. 환기는 짧게 하고 외출 후 세수를 해주세요.",
        "보통 수준이지만 호흡기 약한 분들은 주의가 필요합니다. 손 씻기는 기본입니다.",
    ],
    "나쁨": [
        "외출 시 KF80 이상 마스크를 착용하는 것이 좋습니다. 귀가 후 코와 입을 헹꿔주세요.",
        "오늘은 창문을 닫고 실내 공기를 지키는 것이 필요합니다. 물을 자주 마시면 도움이 됩니다.",
        "호흡기 질환이 있는 분들은 외출을 줄이고 실내에서 가벼운 운동을 해보세요.",
    ],
    "매우나쁨": [
        "실내 생활을 권장합니다. 어린이와 노인은 특히 주의가 필요합니다.",
        "공기가 많이 탁합니다. 외출은 피하고 창문을 닫아두는 것이 좋습니다.",
        "기관지나 심혈관 질환 환자는 오늘 각별히 조심하세요. 따뜻한 차로 목을 보호해보세요.",
    ],
}


# ==================================================
# 오늘의 건강정보 (30개 중 3개 랜덤)
# ==================================================
HEALTH_TIPS = [
    {"title": "수면 관리",     "tip": "오늘은 일찍 자고 푹 쉬어보세요. 면역력이 쑥쑥 올라갑니다!"},
    {"title": "수분 섭취",     "tip": "물 한 잔으로 시작하는 하루, 몸이 훨씬 가벼워져요."},
    {"title": "균형 잡힌 식사","tip": "채소·단백질·곡물, 골고루 먹는 게 최고의 보약!"},
    {"title": "운동 습관",     "tip": "30분만 걸어도 기분이 달라집니다."},
    {"title": "스트레스 관리", "tip": "깊게 숨 쉬고, 마음을 가볍게 해보세요."},
    {"title": "손 씻기",       "tip": "작은 습관이 큰 예방! 손 씻기는 최고의 백신입니다."},
    {"title": "비타민 섭취",   "tip": "비타민 C 하나로 피로가 훨씬 덜해져요."},
    {"title": "자세 교정",     "tip": "허리를 쭉 펴고 앉아보세요. 몸이 훨씬 편안해집니다."},
    {"title": "정기 검진",     "tip": "조기 발견이 최고의 치료! 검진은 꼭 챙기세요."},
    {"title": "금연",          "tip": "오늘 한 개비 덜 피우는 게 내일의 건강을 지킵니다."},
    {"title": "절주",          "tip": "술잔을 조금 줄이면 간이 웃습니다."},
    {"title": "아침 식사",     "tip": "아침식사는 하루 에너지의 시작!"},
    {"title": "단백질 섭취",   "tip": "근육은 단백질을 좋아합니다. 오늘은 계란 하나 추가!"},
    {"title": "칼슘 섭취",     "tip": "우유 한 잔으로 뼈 건강 챙겨요."},
    {"title": "철분 섭취",     "tip": "시금치 같은 철분 음식은 빈혈 예방에 도움이 됩니다!"},
    {"title": "과일 섭취",     "tip": "오늘은 달콤한 과일로 비타민 충전!"},
    {"title": "채소 섭취",     "tip": "채소는 자연이 준 최고의 항산화제예요."},
    {"title": "소금 줄이기",   "tip": "오늘은 간을 조금 싱겁게! 혈압이 좋아집니다."},
    {"title": "당 줄이기",     "tip": "오늘은 평소보다 당을 좀 줄여봐요~!"},
    {"title": "스트레칭",      "tip": "목과 어깨를 쭉 늘려주면 피로가 풀려요."},
    {"title": "눈 건강",       "tip": "20분마다 창밖을 바라보세요. 눈이 훨씬 편안해집니다."},
    {"title": "구강 건강",     "tip": "양치질은 하루 두 번 이상! 치아가 오래 갑니다."},
    {"title": "피부 관리",     "tip": "자외선 차단제는 피부의 방패예요."},
    {"title": "체중 관리",     "tip": "적정 체중은 만성질환 예방의 첫걸음."},
    {"title": "심호흡",        "tip": "깊게 들이마시고 천천히 내쉬면 마음이 차분해져요."},
    {"title": "명상",          "tip": "5분 명상으로 하루가 훨씬 가벼워집니다."},
    {"title": "사회적 교류",   "tip": "사람과의 대화가 최고의 정신 건강 비타민!"},
    {"title": "취미 활동",     "tip": "좋아하는 일을 하면 스트레스가 사라져요."},
    {"title": "햇빛 쬐기",    "tip": "햇살은 비타민 D와 기분을 동시에 선물합니다."},
    {"title": "규칙적 생활",   "tip": "규칙적인 생활이 몸과 마음을 안정시켜요."},
]


# ==================================================
# Groq AI 호출
# ==================================================
def call_groq(prompt: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": (
                    "당신은 친절한 한국인 약사 AI입니다. "
                    "반드시 한국어로만 답변하세요. "
                    "다른 언어는 절대 사용하지 마세요. "
                    "꼭 한국어로만 작성해주세요. "
                    "한국어로만 표기해주세요 "
                    "한국어만 사용가능합니다. "
                    "모든 단어를 한글로 표기하세요. "
                    "모든 답변을 한글로만 표기하세요. "
                    "복용, 상담, 주의 등 모든 단어를 한글로만 표기하세요. "
                    "의약품 추천 시 반드시 '심한 경우 병원 방문 권장' 문구를 포함하세요."
                )
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 1.0,
        "max_tokens": 1024
    }
    response = requests.post(url, headers=headers, json=body)
    result = response.json()
    return result["choices"][0]["message"]["content"]


# ==================================================
# 미세먼지 등급 판별
# ==================================================
def get_air_grade(pm10_value):
    try:
        pm10 = int(pm10_value)
        if pm10 <= 30:
            return "좋음"
        elif pm10 <= 80:
            return "보통"
        elif pm10 <= 150:
            return "나쁨"
        else:
            return "매우나쁨"
    except:
        return "보통"


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
            return jsonify({"success": False, "message": "약 정보를 찾을 수 없습니다."})

        items = body.get("items")
        if not items:
            return jsonify({"success": False, "message": "검색 결과 없음"})

        medicine   = items[0]
        item_name  = medicine.get("itemName", "정보 없음")
        effect     = medicine.get("efcyQesitm", "효능 정보 없음")
        use_method = medicine.get("useMethodQesitm", "복용법 정보 없음")
        warning    = medicine.get("atpnWarnQesitm", "주의사항 정보 없음")

        prompt = f"""
다음은 '{item_name}' 약에 대한 공식 데이터입니다.
이 내용을 환자가 이해하기 쉽게 정리해 주세요.

[효능]
{effect}

[복용 방법]
{use_method}

[주의사항]
{warning}

이모지를 활용해서 보기 좋게, 핵심만 간결하게 요약해 주세요.
"""
        ai_summary = call_groq(prompt)
        final_result = ai_summary + f"\n\n{DISCLAIMER}"

        return jsonify({"success": True, "result": final_result})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# ==================================================
# 약 추천
# ==================================================
@app.route("/medicine-recommend", methods=["POST"])
def medicine_recommend():
    try:
        data = request.get_json()
        symptom = data.get("symptom")

        prompt = f"""
사용자 증상: '{symptom}'

이 증상에 맞는 일반의약품을 추천해주세요.
매번 다양한 관점과 다른 약품 위주로 답변해주세요.

다음 형식으로 답해주세요:

1. 추천 약품 이름
   - 실제 약국에서 살 수 있는 제품명 (예: 타이레놀, 이부프로펜정, 판콜에이 등) 2~3개 구체적으로 알려주세요
   - 성분명도 함께 표기해주세요

2. 이 약이 도움이 되는 이유

3. 복용 시 주의할 점

4. 이런 경우엔 병원 방문 필요

실제 약국에서 처방전 없이 구매 가능한 약 위주로 추천해주세요.
전문적이지만 쉽게 설명해주세요.
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
            f"category=health&country=kr&apiKey={NEWS_API_KEY}"
        )
        response = requests.get(url)
        data = response.json()
        articles = data.get("articles", [])

        news_list = []
        for article in articles[:5]:
            news_list.append({
                "title":       article.get("title"),
                "description": article.get("description"),
                "url":         article.get("url")
            })

        return jsonify({"success": True, "news": news_list})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# ==================================================
# 미세먼지
# ==================================================
@app.route("/air")
def air():
    try:
        url = (
            "http://apis.data.go.kr/B552584/"
            "ArpltnInforInqireSvc/getCtprvnRltmMesureDnsty"
        )
        params = {
            "serviceKey": AIR_API_KEY,
            "returnType": "json",
            "numOfRows":  "5",
            "pageNo":     "1",
            "sidoName":   "서울",
            "ver":        "1.0"
        }
        response = requests.get(url, params=params)
        data = response.json()
        items = data["response"]["body"]["items"]

        air_list = []
        for item in items[:5]:
            pm10_value = item.get("pm10Value", "0")
            grade      = get_air_grade(pm10_value)
            comment    = random.choice(AIR_COMMENTS[grade])

            air_list.append({
                "station": item.get("stationName"),
                "pm10":    pm10_value,
                "pm25":    item.get("pm25Value"),
                "grade":   grade,
                "comment": comment,
            })

        return jsonify({"success": True, "air": air_list})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# ==================================================
# 오늘의 건강정보 (3개 랜덤)
# ==================================================
@app.route("/health-tips")
def health_tips():
    tips = random.sample(HEALTH_TIPS, 3)
    return jsonify({"success": True, "tips": tips})


# ==================================================
# 감염병 현황
# ==================================================
@app.route("/infectious-disease")
def infectious_disease():
    try:
        url = "http://apis.data.go.kr/1790387/infectiousDisease/getInfectious"
        params = {
            "serviceKey": DATA_API_KEY,
            "pageNo":     "1",
            "numOfRows":  "10",
            "returnType": "json",
        }
        response = requests.get(url, params=params)
        data = response.json()
        items = data.get("response", {}).get("body", {}).get("items", [])

        if not items:
            return jsonify({"success": False, "message": "감염병 데이터를 불러올 수 없습니다."})

        disease_list = []
        for item in items:
            disease_list.append({
                "name":     item.get("diseaseName", "정보 없음"),
                "count":    item.get("patientCnt", "0"),
                "date":     item.get("reportDate", ""),
                "category": item.get("diseaseCategory", ""),
                "trend":    "same",
            })

        return jsonify({"success": True, "diseases": disease_list})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# ==================================================
# 서버 실행
# ==================================================
if __name__ == "__main__":
    app.run(debug=True)
