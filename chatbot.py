import os
import re
import subprocess
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import speech_recognition as sr
import pyttsx3

# Download NLTK resources
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

class CustomChatAssistant:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Configure voice
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)
        self.engine.setProperty('rate', 150)

        # Define intent patterns
        self.intent_patterns = {
    'greeting': r'hello|hi|hey|greetings|good morning|good afternoon|good evening|howdy|sup|yo|what\'s up|hey there|hi there|hey you',
    'open_app': r'open|start|launch|run|begin|activate|load|open the app|start the program|launch the application|open the software|initiate',
    'close_app': r'close|exit|quit|terminate|shut down|end|stop|close the app|quit the program|terminate the application|exit the software|shut it down|log out',
    'coding_help': r'code|coding|program|algorithm|solve|problem|debug|help with code|assist with programming|write a function|fix bug|implement algorithm|write code for|coding help|how to program|how do I write|can you help with coding|how do I debug',
    'system_info': r'info|information|describe|explain|what is|tell me about|what\'s the info|give me details|what\'s this|how does it work|how do I use|what\'s going on|can you explain|can you describe|give me the system info|can you explain this',
    'goodbye': r'bye|goodbye|see you|exit|take care|bye bye|see ya|farewell|later|have a good one|peace out|catch you later|good night|bye for now',
    'thank_you': r'thank you|thanks|thanks a lot|thank you so much|many thanks|I appreciate it|thank you very much|thanks a ton|thanks a bunch|I\'m grateful|appreciate it',
    'apology': r'sorry|apologize|I\'m sorry|my apologies|I didn\'t mean to|excuse me|I\'m sorry for that|please forgive me|pardon me|sorry about that|I apologize|sorry for the inconvenience',
    'help': r'help|assist|can you help|need assistance|can you assist|I need help|help me|please help|can you guide me|assist me|give me a hand|I need assistance|help with this|can you help me',
    'thanks_for_help': r'thank you for your help|thanks for helping|thanks for the assistance|I appreciate the help|thank you for assisting|thanks for your support|appreciate your help|thank you for your time|I\'m grateful for your help|thanks for your guidance',
    'weather': r'weather|forecast|what\'s the weather|how\'s the weather|weather today|forecast today|what\'s the temperature|is it sunny|is it raining|weather report|current weather|what\'s the temperature like|how hot is it',
    'time': r'time|what\'s the time|current time|tell me the time|what time is it|what\'s the time now|how late is it|give me the time|what time do you have|what is the current time|how many hours',
    'joke': r'joke|tell me a joke|make me laugh|tell a joke|can you tell a joke|funny|say something funny|humor|crack a joke|tell me something funny|got a joke for me|can you tell a funny story',
    'motivation': r'motivate me|give me motivation|inspire me|encourage me|I need motivation|I need encouragement|tell me something inspiring|give me some inspiration|can you motivate me|say something inspiring|lift my spirits|I feel down|cheer me up',
    'compliment': r'you are great|you\'re awesome|you are amazing|good job|well done|that\'s impressive|you rock|you\'re fantastic|you\'re brilliant|you\'re excellent|I\'m impressed|you\'re a genius|keep it up|you\'re doing well|that\'s awesome',
    'movie_recommendation': r'movie|film|recommend a movie|suggest a movie|what movie should I watch|give me movie recommendations|I\'m looking for a movie|suggest a film|any good movies|movie ideas|what movie do you recommend|what should I watch next',
    'music_recommendation': r'music|song|recommend a song|suggest a song|what should I listen to|give me music recommendations|I need some music|suggest a playlist|what\'s a good song|can you suggest a song|any good music recommendations|what are you listening to|can you recommend a song',
    'quote': r'quote|inspiration|tell me a quote|give me a quote|motivation quote|quote of the day|inspirational quote|share a quote|I need a quote|give me a motivational quote|tell me something wise|quote me|any good quotes',
    'news': r'news|what\'s the news|current events|latest news|what\'s happening|what\'s going on|any news today|what\'s new|give me the news|tell me what\'s going on|what\'s the latest news|any updates|what\'s the current news',
    'sports': r'sports|what\'s the score|any sports updates|sports news|tell me about the game|score update|sports news|any games today|how\'s the match|who won the game|sports scores|game update|what\'s happening in sports|who won the match',
    'food': r'food|what\'s for lunch|recommend a dish|what should I eat|suggest a food|what\'s for dinner|any food suggestions|what\'s a good meal|what should I have|any food ideas|what should I cook|give me food ideas|what\'s tasty',
    'technology': r'tech|technology|what\'s new in tech|tell me about tech|give me tech news|what\'s happening in tech|new tech updates|technology news|latest in tech|what\'s new in gadgets|tech trends|give me tech updates|what are the latest gadgets',
    'health': r'health|wellness|how do I stay healthy|tips for good health|tell me about health|how to stay fit|any health advice|what\'s good for health|fitness tips|well-being|stay healthy|how to get fit|health tips',
    'finance': r'finance|money|how do I save money|what\'s a good investment|financial tips|tell me about finance|what should I invest in|how do I manage my finances|can you give me financial advice|budgeting tips|investing advice|finance tips|how to manage money',
    'shopping': r'shopping|buy something|where can I buy|what to buy|best products to buy|shopping tips|give me shopping ideas|what should I buy|what\'s trending in shopping|where to shop|best places to shop|where can I find',
    'travel': r'travel|where to go|travel tips|give me travel advice|best travel destinations|recommend a place to visit|where should I travel|tell me about travel|what\'s a good place to travel|where should I go next|give me travel ideas|I want to travel to',
    'study_help': r'study help|study tips|how to study|study advice|tips for studying|can you help me study|study guide|how do I study better|study tips for exams|study resources|study with me|how to prepare for exams|how to improve study skills'
}


        # App mapping dictionary
        self.app_mapping = {
            'calculator': 'calc.exe',
            'notepad': 'notepad.exe',
            'browser': 'start chrome',
            'file explorer': 'explorer.exe'
        }

    def preprocess_text(self, text):
        tokens = nltk.word_tokenize(text.lower())
        filtered = [self.lemmatizer.lemmatize(w) for w in tokens if w not in self.stop_words]
        return filtered

    def detect_intent(self, text):
        for intent, pattern in self.intent_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return intent
        return 'unknown'

    def handle_coding_problem(self, question):
        # Simple coding problem solver (can be expanded)
        coding_knowledge = {
            'reverse string': 'In Python: "".join(reversed(string))',
            'fibonacci': 'def fib(n):\n    a, b = 0, 1\n    for _ in range(n):\n        yield a\n        a, b = b, a+b',
            'sort list': 'Use list.sort() or sorted(list) in Python',
            'binary search': '''def binary_search(arr, target):
    left, right = 0, len(arr)-1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1'''
        }
        for key in coding_knowledge:
            if key in question.lower():
                return coding_knowledge[key]
        return "I can help with: reverse string, fibonacci, sort list, binary search. Ask about one!"

    def execute_command(self, intent, text):
                try:
                    if intent == 'greeting':
                        return "Hello! How can I assist you today?"
                    elif intent == 'goodbye':
                        return "Goodbye! Have a great day!"
                    elif intent == 'open_app':
                        return "Opening the application now."
                    elif intent == 'close_app':
                        return "Closing the application now."
                    elif intent == 'coding_help':
                        return "I can help with coding problems. What are you working on?"
                    elif intent == 'system_info':
                        return "Let me know what system info you'd like. For example, CPU, RAM, or storage."
                    elif intent == 'thank_you':
                        return "You're welcome! I'm glad I could help."
                    elif intent == 'apology':
                            return "No worries! How can I assist you further?"
                    elif intent == 'weather':
                        return "Let me check the weather for you."
                    elif intent == 'time':
                        return "Let me get the current time for you."
                    elif intent == 'joke':
                        return "Here's a joke: Why don't skeletons fight each other? They don't have the guts!"
                    elif intent == 'motivation':
                        return "Keep going, you're doing great! Success is just around the corner."
                    elif intent == 'compliment':
                        return "Thank you! You're doing an amazing job yourself!"
                    elif intent == 'movie_recommendation':
                        return "How about watching 'Inception'? It's a mind-bending thriller!"
                    elif intent == 'music_recommendation':
                        return "I recommend listening to 'Blinding Lights' by The Weeknd. It's a great hit!"
                    elif intent == 'quote':
                        return "Here's an inspiring quote: 'The only way to do great work is to love what you do.' - Steve Jobs"
                    elif intent == 'news':
                        return "Let me fetch the latest news for you."
                    elif intent == 'sports':
                        return "I can help with sports updates. Which sport are you interested in?"
                    elif intent == 'food':
                        return "How about trying something new? Maybe some sushi or a pizza?"
                    elif intent == 'technology':
                        return "Tech is evolving fast! What would you like to know about the latest trends?"
                    elif intent == 'health':
                        return "Staying healthy is important. How can I assist with your health goals?"
                    elif intent == 'finance':
                        return "For financial advice, start by tracking your expenses and saving for the future."
                    elif intent == 'shopping':
                        return "You can find great deals on Amazon or eBay. What are you looking to buy?"
                    elif intent == 'travel':
                        return "Traveling can be so exciting! Do you have a destination in mind?"
                    elif intent == 'study_help':
                        return "I can assist with study tips! Are you preparing for an exam or need help with a topic?"
                    return "I'm not sure how to help with that. Could you rephrase?"
                except Exception as e:
                    return f"Error executing command: {str(e)}"


    def process_query(self, text):
        intent = self.detect_intent(text)
        return self.execute_command(intent, text)

    def text_to_speech(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def speech_to_text(self):
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source)
            try:
                return self.recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                return "Could not understand audio"
            except sr.RequestError:
                return "Speech service unavailable"

# Main interaction loop
if __name__ == "__main__":
    assistant = CustomChatAssistant()
    
    while True:
        user_input = assistant.speech_to_text()
        print("User:", user_input)
        
        if user_input.lower() in ['exit', 'quit', 'goodbye']:
            response = "Goodbye! Have a great day!"
            print("Assistant:", response)
            assistant.text_to_speech(response)
            break
            
        response = assistant.process_query(user_input)
        print("Assistant:", response)