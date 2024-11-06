from flask import Flask, request, jsonify, render_template
from googletrans import Translator
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import nltk
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
import random

app = Flask(__name__)

translator = Translator()

# Ensure necessary NLTK resources are downloaded
nltk.download('punkt')
nltk.download('wordnet')

# Simple synonym substitution function (filter for common, basic words)
def simple_synonym_substitution(sentence):
    words = word_tokenize(sentence)
    new_sentence = []
    
    for word in words:
        synonyms = wordnet.synsets(word)
        if synonyms and word.isalpha():  
            
            simple_synonyms = [syn.lemmas()[0].name() for syn in synonyms if len(syn.lemmas()[0].name()) <= 6]
            if simple_synonyms:
                simple_word = random.choice(simple_synonyms) 
                if simple_word != word:  
                    new_sentence.append(simple_word)
                else:
                    new_sentence.append(word)
            else:
                new_sentence.append(word)
        else:
            new_sentence.append(word)
    
    return ' '.join(new_sentence)

# Function to summarize using LexRank algorithm and substitute synonyms
def summarize_text(text, sentence_count=2):  # Keep summary shorter
    try:
        # Parse and summarize the text using LexRank
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LexRankSummarizer()
        summary = summarizer(parser.document, sentence_count)
        
        # Convert summary sentences to text and apply synonym substitution
        summarized_text = []
        for sentence in summary:
            simplified_sentence = simple_synonym_substitution(str(sentence))  # Simple synonym substitution
            summarized_text.append(simplified_sentence)
        
        return ' '.join(summarized_text)
    except Exception as e:
        return f"Error in summarization: {str(e)}"

@app.route("/")
def index():
    return render_template('base.html')  # Serve your HTML file here

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    option = request.json.get("option")

    # Handling the 'stop' command
    if user_input.lower() == "stop":
        return jsonify({"response": "Thank you for using the chatbot. Have a great day!"})

    # Handling the 'start' command
    if user_input.lower() == "start":
        return jsonify({
            "response": "Welcome! Please select one of the following options:",
            "options": [
                {"label": "Translate from English to Marathi", "value": "Translating English to Marathi"},
                {"label": "Translate from Marathi to English", "value": "Translating Marathi to English"},
                {"label": "Summarize English text", "value": "Summarize English"},
                {"label": "Summarize Marathi text", "value": "Summarize Marathi"}
            ]
        })

    # Display options when the user types 'options'
    if user_input.lower() == "options":
        return jsonify({
            "response": "Please select one of the following options:",
            "options": [
                {"label": "Translate from English to Marathi", "value": "Translating English to Marathi"},
                {"label": "Translate from Marathi to English", "value": "Translating Marathi to English"},
                {"label": "Summarize English text", "value": "Summarize English"},
                {"label": "Summarize Marathi text", "value": "Summarize Marathi"}
            ]
        })

    # Handling translation options
    if option == "Translating English to Marathi":
        if not user_input.strip():
            return jsonify({"response": "Please provide the English text that you would like to translate into Marathi."})
        translated_text = translator.translate(user_input, src='en', dest='mr').text
        return jsonify({"response": translated_text})

    elif option == "Translating Marathi to English":
        if not user_input.strip():
            return jsonify({"response": "Please provide the Marathi text that you would like to translate into English."})
        translated_text = translator.translate(user_input, src='mr', dest='en').text
        return jsonify({"response": translated_text})

    # Handling summarization options
    elif option == "Summarize English":
        if not user_input.strip():
            return jsonify({"response": "Please provide the English text that you would like to summarize."})
        summary = summarize_text(user_input)
        return jsonify({"response": summary})

    elif option == "Summarize Marathi":
        if not user_input.strip():
            return jsonify({"response": "Please provide the Marathi text that you would like to summarize."})
        summary = summarize_text(user_input)  # You may want to implement a different logic for Marathi
        return jsonify({"response": summary})

    return jsonify({"response": "I did not understand your request. Please type 'options' to see available functionalities."})

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)



# from flask import Flask, request, jsonify, render_template
# from googletrans import Translator
# from sumy.parsers.plaintext import PlaintextParser
# from sumy.nlp.tokenizers import Tokenizer
# from sumy.summarizers.lex_rank import LexRankSummarizer
# import nltk
# from nltk.corpus import wordnet
# from nltk.tokenize import word_tokenize
# import random

# app = Flask(__name__)

# translator = Translator()

# # Ensure necessary NLTK resources are downloaded
# nltk.download('punkt')
# nltk.download('wordnet')

# # Function to replace complex words with simpler synonyms
# def simple_synonym_substitution(sentence):
#     words = word_tokenize(sentence)
#     new_sentence = []
    
#     for word in words:
#         synonyms = wordnet.synsets(word)
#         simple_word = word
#         if synonyms and word.isalpha():  # Only consider alphabetic words
#             # Filter synonyms that are commonly used (lower complexity)
#             simple_synonyms = [syn.lemmas()[0].name() for syn in synonyms if len(syn.lemmas()[0].name()) <= 6]  # Restrict length
#             if simple_synonyms:
#                 simple_word = random.choice(simple_synonyms)  # Choose a simpler synonym if available
        
#         new_sentence.append(simple_word)
    
#     return ' '.join(new_sentence)

# # Function to summarize and simplify the text
# def summarize_text(text, sentence_count=2):  # Reduced sentence count
#     try:
#         # Parse and summarize the text using LexRank
#         parser = PlaintextParser.from_string(text, Tokenizer("english"))
#         summarizer = LexRankSummarizer()
#         summary = summarizer(parser.document, sentence_count)
        
#         # Convert summary sentences to text and apply synonym substitution
#         summarized_text = []
#         for sentence in summary:
#             simplified_sentence = simple_synonym_substitution(str(sentence))  # Simple synonym substitution
#             summarized_text.append(simplified_sentence)
        
#         return ' '.join(summarized_text)
#     except Exception as e:
#         return f"Error in summarization: {str(e)}"

# @app.route("/")
# def index():
#     return render_template('base.html')  # Serve your HTML file here

# @app.route("/chat", methods=["POST"])
# def chat():
#     user_input = request.json.get("message")
#     option = request.json.get("option")

#     # Handling the 'stop' command
#     if user_input.lower() == "stop":
#         return jsonify({"response": "Thank you for using the chatbot. Have a great day!"})

#     # Handling the 'start' command
#     if user_input.lower() == "start":
#         return jsonify({
#             "response": "Welcome! Please select one of the following options:",
#             "options": [
#                 {"label": "Translate from English to Marathi", "value": "Translating English to Marathi"},
#                 {"label": "Translate from Marathi to English", "value": "Translating Marathi to English"},
#                 {"label": "Summarize English text", "value": "Summarize English"},
#                 {"label": "Summarize Marathi text", "value": "Summarize Marathi"}
#             ]
#         })

#     # Display options when the user types 'options'
#     if user_input.lower() == "options":
#         return jsonify({
#             "response": "Please select one of the following options:",
#             "options": [
#                 {"label": "Translate from English to Marathi", "value": "Translating English to Marathi"},
#                 {"label": "Translate from Marathi to English", "value": "Translating Marathi to English"},
#                 {"label": "Summarize English text", "value": "Summarize English"},
#                 {"label": "Summarize Marathi text", "value": "Summarize Marathi"}
#             ]
#         })

#     # Handling translation options
#     if option == "Translating English to Marathi":
#         if not user_input.strip():
#             return jsonify({"response": "Please provide the English text that you would like to translate into Marathi."})
#         translated_text = translator.translate(user_input, src='en', dest='mr').text
#         return jsonify({"response": translated_text})

#     elif option == "Translating Marathi to English":
#         if not user_input.strip():
#             return jsonify({"response": "Please provide the Marathi text that you would like to translate into English."})
#         translated_text = translator.translate(user_input, src='mr', dest='en').text
#         return jsonify({"response": translated_text})

#     # Handling summarization options
#     elif option == "Summarize English":
#         if not user_input.strip():
#             return jsonify({"response": "Please provide the English text that you would like to summarize."})
#         summary = summarize_text(user_input)
#         return jsonify({"response": summary})

#     elif option == "Summarize Marathi":
#         if not user_input.strip():
#             return jsonify({"response": "Please provide the Marathi text that you would like to summarize."})
#         summary = summarize_text(user_input)  # You may want to implement a different logic for Marathi
#         return jsonify({"response": summary})

#     return jsonify({"response": "I did not understand your request. Please type 'options' to see available functionalities."})

# if __name__ == "__main__":
#     app.run(debug=True, host="127.0.0.1", port=5000)
