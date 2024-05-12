import json
import pickle
import random
import numpy
from pycorenlp import StanfordCoreNLP
from webscraping import scrape_data
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.models import model_from_yaml
from search_api import getSearchResults
from nltk import  LancasterStemmer
# Khởi tạo kết nối tới VnCoreNLP
nlp = StanfordCoreNLP('http://localhost:9000')

def main():
    print(getSearchResults("example query"))

stemmer = LancasterStemmer()
with open("DataJson/data.json", encoding='utf-8') as file:
    data = json.load(file)

try:
    with open("chatbot.pickle", "rb") as file:
        words, labels, training, output = pickle.load(file)

except:
    words = []
    labels = []
    docs_x = []
    docs_y = []

    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            # Sử dụng VnCoreNLP để tokenize
            output = nlp.annotate(pattern, properties={
                'annotators': 'tokenize',
                'outputFormat': 'json'
            })
            wrds = [token['word'] for sentence in output['sentences'] for token in sentence['tokens']]
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])

        if intent["tag"] not in labels:
            labels.append(intent["tag"])

    words = [stemmer.stem(w.lower()) for w in words if w != "?"]
    words = sorted(list(set(words)))

    labels = sorted(labels)

    training = []
    output = []

    output_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []

        wrds = [stemmer.stem(w.lower()) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = output_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)

    training = numpy.array(training)
    output = numpy.array(output)

    with open("chatbot.pickle", "wb") as file:
        pickle.dump((words, labels, training, output), file)

try:
    yaml_file = open('chatbotmodel.yaml', 'r')
    loaded_model_yaml = yaml_file.read()
    yaml_file.close()
    myChatModel = model_from_yaml(loaded_model_yaml)
    myChatModel.load_weights("chatbotmodel.h5")
    print("Loaded model from disk")

except:
    # Make our neural network
    myChatModel = Sequential()
    myChatModel.add(Dense(8, input_shape=[len(words)], activation='relu'))
    myChatModel.add(Dense(len(labels), activation='softmax'))

    # optimize the model
    myChatModel.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    # train the model
    myChatModel.fit(training, output, epochs=1000, batch_size=8)

    # serialize model to yaml and save it to disk
    model_json = myChatModel.to_json()

    with open("chatbotmodel.yaml", "w") as y_file:
        y_file.write(model_json)

    # serialize weights to HDF5
    myChatModel.save_weights("chatbotmodel.h5")
    print("Saved model from disk")

def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    # Sử dụng VnCoreNLP để tokenize
    output = nlp.annotate(s, properties={
        'annotators': 'tokenize',
        'outputFormat': 'json'
    })
    s_words = [token['word'] for sentence in output['sentences'] for token in sentence['tokens']]
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1

    return numpy.array(bag)

def chatWithBot(inputText):
    currentText = bag_of_words(inputText, words)
    currentTextArray = [currentText]
    numpyCurrentText = numpy.array(currentTextArray)

    if numpy.all((numpyCurrentText == 0)):
        return "I didn't get that, try again"

    result = myChatModel.predict(numpyCurrentText[0:1])
    result_index = numpy.argmax(result)
    tag = labels[result_index]

    if result[0][result_index] > 0.7:
        scrape_data(tag)
        with open("DataJson/data.json", encoding='utf-8') as file:
            new_data = json.load(file)
        for tg in new_data["intents"]:
            if tg['tag'] == tag:
                return random.sample(tg["responses"], 2)

        return "Try again"

    else:
        return "I didn't get that, try again"

def chat():
    print("Start talking with the chatbot (try quit to stop)")

    while True:
        inp = input("You: ")
        if inp.lower() == "quit":
            break

        print(chatWithBot(inp))

# chat()