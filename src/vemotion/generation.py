
from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from vemotion import settings
import ipinfo
import weatherapi

# https://aistudio.google.com/
GOOGLE_API_KEY = settings.google_api_key
# https://ipinfo.io
IPINFO_API_KEY = settings.ipinfo_api_key
# https://www.weatherapi.com/
WEATHER_API_KEY = settings.weather_api_key

ipinfo_handler = ipinfo.getHandler(IPINFO_API_KEY)
configuration = weatherapi.Configuration()
configuration.api_key['key'] = WEATHER_API_KEY

api_instance = weatherapi.APIsApi(weatherapi.ApiClient(configuration))

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    api_key=GOOGLE_API_KEY,
    max_tokens=1000,
    temperature=0.5,
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    },
)

def get_response_for_emotion(emotion: str) -> str:
    weather = get_weather()
    req_string: str = f"Generate a single sassy and maybe very slightly insulting slack status for the emotion {emotion}. Also take into account the current weather and time: {weather}. You don't have to mention everything in every response. Do not mention the prompt in the response."
    response = llm.invoke(req_string).content
    return response

def get_weather() -> str:
    response = api_instance.realtime_weather(get_postal())
    return response

def get_postal() -> str:
    details = ipinfo_handler.getDetails()
    return str(details.postal)

if __name__ == "__main__":
    print(get_response_for_emotion("mad", get_weather()))