from flask import Flask, request, jsonify, render_template, redirect, url_for
from modules.qna import QnAModule
from modules.music import MusicModule
from modules.weather import WeatherModule
from modules.reminder import ReminderModule
from modules.speech import SpeechModule
from logger import CustomLogger
from prompts.main_prompt import main_prompt, main_bot_examples
from langchain.schema import SystemMessage, HumanMessage
import os

# Initialize Flask app
app = Flask(__name__)
logger = CustomLogger().get_logger()

# Global states
current_functionality = None
conversation_context = {}

# ✅ Load Groq API key automatically from Render env if available
groq_api_key = os.environ.get("GROQ_API_KEY")

# Modules
qna_module = None
music_module = None
weather_module = None
reminder_module = ReminderModule()
speech_module = SpeechModule()


@app.route("/", methods=["GET", "POST"])
def api_key_page():
    """
    Collects Groq API key from user if not provided via environment.
    """
    global groq_api_key, qna_module, music_module, weather_module

    # ✅ If API key exists in Render env → initialize modules instantly
    if groq_api_key:
        if not (qna_module and music_module and weather_module):
            qna_module = QnAModule(groq_api_key)
            music_module = MusicModule(groq_api_key)
            weather_module = WeatherModule(groq_api_key)
            logger.info("Groq API key loaded from Render environment.")
        return redirect(url_for("assistant_page"))

    # ✅ If no key in environment → fallback to manual entry page
    if request.method == "POST":
        groq_api_key = request.form.get("api_key")
        if groq_api_key:
            qna_module = QnAModule(groq_api_key)
            music_module = MusicModule(groq_api_key)
            weather_module = WeatherModule(groq_api_key)
            logger.info("Groq API key entered manually.")
            return redirect(url_for("assistant_page"))
        else:
            return render_template("api_key.html", error="Please provide a valid API key.")

    return render_template("api_key.html")


@app.route("/assistant", methods=["GET"])
def assistant_page():
    """
    Main voice assistant page. Redirects to API Key page if key not set.
    """
    if not groq_api_key:
        return redirect(url_for("api_key_page"))
    return render_template("assistant.html")


@app.route("/process_input", methods=["POST"])
def process_input():
    """
    Handles user input and routes to the appropriate module.
    """
    global current_functionality, conversation_context

    user_input = request.json.get("user_input", "").strip()
    if not user_input:
        return jsonify({"response": "Sorry, I didn't catch that. Please try again."})

    try:
        # If in a functionality, bypass intent detection
        if current_functionality:
            if user_input.lower() == "exit":
                current_functionality = None
                conversation_context.clear()
                return jsonify({"response": "Exited the current functionality. How can I assist you next?"})

            if current_functionality == "qna":
                response = qna_module.handle_qna(user_input)
            elif current_functionality == "music":
                response = music_module.handle_play_music(user_input)
            elif current_functionality == "weather":
                response = weather_module.handle_weather(user_input)
            elif current_functionality == "reminder":
                response = reminder_module.handle_reminder(user_input)
            else:
                response = "You're currently in a functionality. Please say 'exit' to leave it."
            return jsonify({"response": response})

        # Detect intent for the first input
        intent = detect_intent(user_input)
        if intent in ["qna", "music", "weather", "reminder"]:
            current_functionality = intent
            return process_input()

        return jsonify({"response": "I'm sorry, I couldn't understand that. Could you try rephrasing?"})

    except Exception as e:
        logger.error(f"Error processing input: {e}")
        return jsonify({"response": f"An error occurred: {e}"})


@app.route("/interrupt", methods=["POST"])
def interrupt_response():
    try:
        if music_module:
            message = music_module.handle_play_music("interrupt")
            return jsonify({"response": message})

        speech_module.stop_tts()
        return jsonify({"response": "Assistant response interrupted. How can I assist you next?"})
    except Exception as e:
        logger.error(f"Error during interrupt: {e}")
        return jsonify({"response": f"An error occurred while interrupting: {e}"})


@app.route("/exit", methods=["POST"])
def exit_functionality():
    global current_functionality, conversation_context
    current_functionality = None
    conversation_context.clear()
    if music_module:
        music_module.stop_music()
    return jsonify({"response": "Exited the current functionality. How can I assist you next?"})


@app.route("/stop", methods=["POST"])
def stop_assistant():
    global current_functionality, conversation_context, groq_api_key
    current_functionality = None
    conversation_context.clear()
    groq_api_key = None
    speech_module.stop_tts()
    if music_module:
        music_module.stop_music()
    return jsonify({"response": "Assistant stopped. Thank you! Have a Great Day!..", "redirect": "/"})


@app.route("/start", methods=["POST"])
def start_assistant():
    return jsonify({
        "response": (
            "Welcome to your Voice Assistant by Ayush. You can ask me to set reminders, "
            "fetch weather, play music, or answer general questions. Say 'exit' to leave any functionality."
        )
    })


def detect_intent(user_input):
    try:
        logger.info(f"Detecting intent for input: {user_input}")
        few_shot_examples = main_bot_examples
        few_shot_text = "\n".join([f"Input: {ex['input']} Intent: {ex['intent']}" for ex in few_shot_examples])
        prompt = main_prompt(user_input, few_shot_text)

        messages = [
            SystemMessage(content="You are an intent detection assistant."),
            HumanMessage(content=prompt)
        ]
        response = qna_module.llm.invoke(messages)
        intent_detected = response.content.strip().lower()
        print(f"[DEBUG] Detected Intent: {intent_detected}")
        return intent_detected

    except Exception as e:
        logger.error(f"Error detecting intent: {e}")
