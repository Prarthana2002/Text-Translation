import streamlit as st
import google.generativeai as genai
import pyttsx3
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import os
import speech_recognition as sr
import requests
import warnings
warnings.filterwarnings("ignore")

# ✅ Set Streamlit page config at the very top
st.set_page_config(page_title="Multilingual NLP Tool", layout="wide")

# ✅ Set the background image (using a URL)
background_url = "https://github.com/Prarth2002/IMG/blob/main/pastel-blue.jpg?raw=true"
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url({background_url});
        background-size: cover;
        background-position: center center;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ✅ Sidebar content with logo image
with st.sidebar:
    st.markdown("**Multilingual Natural Language Tool**")
    st.markdown("Support literacy and learning in Indian education")
    st.image("https://github.com/Prarth2002/Images/blob/main/multilingual-removebg-preview.png?raw=true", use_column_width=True)
    about_option = st.radio("Navigation", ["Home", "About"])

# ✅ Configure Gemini API Key (Replace with your actual key)
genai.configure(api_key="AIzaSyAbLZEo6b3EB4pWANbxgJn4YhXQlo3tDWY")

# ✅ Supported languages (Removed "Auto Detect")
indian_languages = {
    "English": "en",
    "Hindi": "hi",
    "Bengali": "bn",
    "Telugu": "te",
    "Marathi": "mr",
    "Tamil": "ta",
    "Urdu": "ur",
    "Gujarati": "gu",
    "Malayalam": "ml",
    "Kannada": "kn",
    "Oriya": "or",
    "Punjabi": "pa",
    "Sindhi": "sd",
    "Nepali": "ne",
    "Arabic": "ar",
    "Portuguese": "pt"
}

# ✅ Function to translate using Gemini API
def translate_with_gemini(text, source_lang, target_lang):
    prompt = (
        f"Translate the following text from {source_lang} to {target_lang}: '{text}'.\n"
        f"Provide the output in two lines:\n"
        f"Translated text only\n"
        f"Romanized (phonetic) version prefixed with 'Romanized: '"
    )
    response = genai.GenerativeModel("gemini-pro").generate_content(prompt)
    
    if response.text:
        lines = response.text.split("\n")
        translated_text = lines[0].strip() if len(lines) > 0 else "Translation Error"
        romanized_text = lines[1].strip() if len(lines) > 1 else ""
        return translated_text, romanized_text
    return "Translation Error", ""

# ✅ Function to recognize speech
def recognize_speech():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        st.info("Listening for speech... Please speak clearly.")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
    try:
        text = recognizer.recognize_google(audio, language='en-US')
        st.session_state.input_text = text
        st.success(f"Recognized Text: {text}")
    except sr.UnknownValueError:
        st.error("Sorry, I could not understand the speech. Please try again.")
    except sr.RequestError as e:
        st.error(f"Could not request results from Speech Recognition service; {e}")

# ✅ Function to speak text
def speak_text(text, lang_code):
    try:
        tts = gTTS(text=text, lang=lang_code)
        tts.save("temp.mp3")
        audio = AudioSegment.from_file("temp.mp3", format="mp3")
        play(audio)
        os.remove("temp.mp3")
    except Exception as e:
        st.error(f"Error during speech synthesis: {e}")

# ✅ Initialize session state
if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""
if "romanized_text" not in st.session_state:
    st.session_state.romanized_text = ""

# ✅ About Page
if about_option == "About":
    st.title("About the Multilingual Natural Language Tool")
    text_file_url = "https://github.com/Prarth2002/IMG/blob/main/Text%201.txt?raw=true"
    response = requests.get(text_file_url)
    about_text = response.text
    st.subheader("Purpose and Vision")
    st.markdown(about_text)

# ✅ Home Page
if about_option == "Home":
    st.title("Multilingual Natural Language Tool")

    if st.button("🎙️ Listen to Speech and Convert to Text"):
        with st.spinner("Listening..."):
            recognize_speech()

    st.subheader("Input Text")
    st.session_state.input_text = st.text_area("Paste or type your text here:", value=st.session_state.input_text)

    st.subheader("Translation Options")
    source_language = st.selectbox("Select Source Language:", list(indian_languages.keys()))
    target_language = st.selectbox("Select Target Language:", list(indian_languages.keys()))

    if st.button("Translate"):
        if not st.session_state.input_text.strip():
            st.error("Please enter some text to translate.")
        else:
            translated_text, romanized_text = translate_with_gemini(st.session_state.input_text, source_language, target_language)
            st.session_state.translated_text = translated_text
            st.session_state.romanized_text = romanized_text

    if st.session_state.translated_text:
        st.subheader("Translated Text")
        st.write(st.session_state.translated_text)
        
        # ✅ Romanized text WITHOUT bold
        if st.session_state.romanized_text:
            st.write(f"{st.session_state.romanized_text}")

        col1, col2, col3 = st.columns(3)
        if col1.button("🔊 Speak"):
            with st.spinner("Speaking..."):
                speak_text(st.session_state.translated_text, indian_languages[target_language])
        if col3.button("🔁 Speak Again"):
            with st.spinner("Speaking again..."):
                speak_text(st.session_state.translated_text, indian_languages[target_language])

st.markdown("---")
st.markdown("Built for literacy and learning in Indian education.")
