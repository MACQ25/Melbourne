import math
from random import randint
import spacy
from spacy.matcher import Matcher
import regex as re
import json

""" 
Script made to be used in an FAQ bot, made using the FAQ_Bot_Skeleton and File_Input scripts
by Sam Scott (Mohawk College, May 2023), made to be both usable as part of the shell of an IDE
through inputs in the console or to be integrated into the code of a discord bot.

Mauricio Canul, January 2024
"""


def loadJson(fileName: str):
    """
    Function used by this program to load all the contents
    of a JSON file to their respective lists within our program,
    could be further modularized to serve as a general single-point
    access function to our JSON data file
    :param fileName: Name of the JSON file to access (within the data folder)
    :return: Questions(Dict), Answers(List), Speech(Dict), and Entities(Dict)
    """
    f = open(f'data/{fileName}', 'r')
    myDict = json.load(f)
    f.close()
    Questions = dict(myDict["Questions"])
    Answers = list(dict(myDict["Answers"]).values())
    Speech = dict(myDict["SpaCy"])
    Entities = dict(myDict["GeneralTopics"])
    return Questions, Answers, Speech, Entities


def makePatterns(SP: dict):
    """
    Function used to load the values from a dictionary and
    enter them into a Match object (from the SpaCy library)
    as a pattern.
    :param SP: A dictionary with entries, each of which should have "name" (string) and a "pattern" (list of dictionaries) keys
    """
    global match
    for entry in SP.values():
        match.add(entry.get("name"), [entry.get("pattern")])


def smallLoadData(fileName):
    """
    function which gets a randomized entry of data from the given filepath,
    it has been coded with reuse in mind as we are accessing a lot of files
    to get a value a random from, it takes in a filepath from the data folder
    as argument and returns a single string
    :param fileName: filepath, expected to be from the data/ folder
    :return: A string which is a line at random from the given file
    """
    try:
        f = open(f'data/{fileName}', 'r')
        lines = f.readlines()
        length = len(lines) - 1
        randomN = randint(0, length)
        val = lines.pop(randomN)
        f.close()
        return val.strip()
    except FileNotFoundError:
        return "Data for generation could not be found"


def createCharacter():
    """
    Function used to generate a string derived at random from a defined set of data, it is called by especialProtocols()

    This function creates a D&D character at random, with the base values of name, last name, race and class.

    :return: A formatted string to which random data from the desired pools is inserted
    """
    return f'{smallLoadData("firstNames.txt")} {smallLoadData("lastNames.txt")}, a {smallLoadData("races.txt")} {smallLoadData("classes.txt")}'


def createQuest():
    """
    Function used to generate a string derived at random from a defined set of data, it is called by especialProtocols()

    This function gives a prompt that could be used as the starting point of a D&D campaign.

    :return: A string containing a random quest idea
    """
    return f'{smallLoadData("prompts.txt")}'


def createEncounter():
    """
    Function used to generate a string derived at random from a defined set of data, it is called by especialProtocols()

    This function creates a string that is meant to serve as the introduction to a combat in D&D.

    :return: A formatted string to which random data from the desired pools is inserted
    """
    return f'you find yourself facing a {smallLoadData("monsters.txt")} {smallLoadData("places.txt")}'


def rollDice():
    """
    Function meant to create a response to the bot being asked to roll a die, it is called by especialProtocols().
    it is based on the idea that the die in question is a D20
    :return: A string giving the results of the "die roll"
    """
    return f"I shall roll a D2O... *Rolls* I got a {randint(1, 20)}!"


def especialProtocols(protocol: str):
    """
    Function called when the keyword "protocol" is found at the start of an answer, this happens
    when a "specialized" answer has been requested, meaning that the data cannot be gotten by
    simply extracting it from the answers array, this uses helper functions in order to
    correctly generate the desired output
    :param protocol: A string that says protocol at the start and has an identifying number
    :except: A string that was confused as a "Protocol" has entered the function, in such case, said string is returned
    :return: A formatted string representing the result of executing the needed function
    """
    try:
        var = int(protocol.lower().strip("protocol"))
        if var == 1:
            return createCharacter()
        elif var == 2:
            return createQuest()
        elif var == 3:
            return createEncounter()
        elif var == 4:
            return rollDice()
        else:
            return "I could not generate the requested response (how???)"
    except TypeError:
        return protocol


def greetMel(utterance: str):
    """
    This function is called every time a message is sent through discord, it compares
    the utterance from said message with a regular expression used to detect whenever
    someone greets Melbourne or not, and returns an equivalent boolean value
    :param utterance: String to run against the regex string
    :return: True if greeting Melbourne, False if not
    """
    global botName
    pattern = re.compile(r'(^(hello|greetings|hi|hey|what\'s up)[\b\s]*' + botName + r'([!?]|(\w:[3dp]))*$){e<=3}',
                         re.IGNORECASE)
    if pattern.match(utterance) is not None:
        return True
    return False


def dismissMel(utterance: str):
    """
    This function is called every time a message is sent through discord, while Melbourne
    is active, it compares the utterance from said message with a regular expression used
    to detect whenever said message is a dismissal, it returns the corresponding boolean value
    :param utterance: String to run against the regex string
    :return:True if dismissing Melbourne, False if not
    """
    global botName
    pattern = re.compile(r'(^(((good)?bye)|farewell|stop)[\b\s]*' + botName + r'([!]|(\w:[3dp]))*$){e<=3}',
                         re.IGNORECASE)
    if pattern.match(utterance) is not None:
        return True
    return False


def understand(utterance: str):
    """
    The function used to compare the text sent by the user to all the possible questions and their respective RegEx
    strings, it first tries to compare the utterance to the questions directly, if no direct match is found, it runs
    through every RegEx available and adds them to an array, containing both a match object and the index of its
    corresponding answer
    :param utterance: A string that is the user's input
    :return: An array containing all possible match objects after
    comparing the utterance to all available RegEx, will return an array containing -1 if nothing was found
    """
    returnValue = [-1]
    utterance = utterance.lower()
    global questions, count
    for i in questions.values():
        if i["Question"] == utterance:
            returnValue[0] = i["Answer"]
    if returnValue[0] < 0:
        returnValue = []
        for i in questions.values():
            for r in i["Regex"]:
                sens = f'{{e<={math.ceil(len(i["Question"]) / 10)}}}'
                regx = re.compile(r'(' + r + ')' + sens, flags=re.BESTMATCH | re.IGNORECASE)
                match = regx.match(utterance)
                if match is not None:
                    returnValue.append({match: i["Answer"]})
                    print(type(match.fuzzy_counts))
                    print(type(match.fuzzy_counts[0]))
    if len(returnValue) < 1:
        returnValue = [-1]
    return returnValue


def bestOnErrors(intents):
    """
    Function ran in the case that the array returned from understand contains more than 1 possible match,
    in which case this function will run through the matches and compare them to one another, ultimately
    returning the one it finds to have the lowest fuzzy_count (utterance most similar to pattern with least
    mistakes in comparison) returning it and the 2nd most similar if both share a fuzzy count.
    :param intents: All possible match objects and their corresponding answer index in a list of dictionaries
    :return: A list with the match with the lowest fuzzy count among the previous collection, returns two matches
    if both are tied
    """
    bestMatch = []
    otherMatches = []
    indexOfBest = 0
    bestMatchCount = 100
    for x in range(0, len(intents)):
        if type(intents[x]) is dict:
            for obj in intents[x].keys():
                tple = obj.fuzzy_changes
                total = 0
                for n in tple:
                    total += n[0] if len(n) > 0 else 0
                if total < bestMatchCount:
                    bestMatchCount = total
                    indexOfBest = x
                elif total == bestMatchCount:
                    otherMatches.append({total: intents[x]})
    bestMatch.append(intents[indexOfBest])
    if len(otherMatches) > 0 and list(otherMatches[-1])[0] == bestMatchCount:
        bestMatch.append(list(otherMatches[-1])[1])
    return bestMatch


def bestOnLenght(intents):
    """
    Our "last resort" function in the case that multiple matches have been made and of said matches multiple
    are matched to the RegEx to perfection, this will check the number of part groups and put as the first element
    of the array the one with the longest set of group matches that aren't "None", in effect favouring the longest
    match among with the least errors

    Note:
    May be broken, further testing is needed, works as of now with the set of questions and answers we are using where
    two RegEx matches have a fuzzy_count of 0 while being from different patterns

    :param intents: All current candidate matches and their respective answer index
    :return: An array containing the longest and most correct match to be used to generate an answer
    """
    bestMatch = []
    otherMatches = []
    bestMatchCount = 0
    indexOfBest = 0
    for x in range(0, len(intents)):
        if type(intents[x]) is dict:
            for obj in intents[x].keys():
                partGroups = obj.groups()
                curCount = (len(partGroups) - partGroups.count(None))
                if curCount > bestMatchCount:
                    indexOfBest = x
                elif curCount == bestMatchCount:
                    otherMatches.append({curCount: intents[x]})
    bestMatch.append(intents[indexOfBest])
    if len(otherMatches) > 0 and list(otherMatches[-1])[0] == bestMatchCount:
        bestMatch.append(list(otherMatches[-1])[1])
    return bestMatch


def extract(indt):
    """
    Function used to extract an integer value from some specific
    data structures within our program, it returns an int if the
    argument already was one
    :param indt: A dictionary number
    :return: The int value of the argument
    """
    if type(indt) == int:
        return indt
    else:
        return list(indt.values())[0]


def generate(intent: int):
    """
    This function takes in a single number, which is the user's
    "Intent", this Intent should have been discerned from the understand()
    function, with said number it tries to retrieve a response from the
    corresponding index in the array of answers, if the intent is ever an
    invalid number it will return an appropriate answer
    :param intent: A number corresponding to an index in the answers array
    :return: String answer
    """
    global answers
    if intent < 0 or intent >= len(answers):
        return "Sorry, I don't know the answer to that!"
    answer = answers[intent]
    if answer.startswith("protocol"):
        answer = especialProtocols(answer)
    return answer


def process(input: str):
    """
    Function repeated by the bot every time there is an input, it processes input in the following order:
    - Runs it through understand()
    - Understand() looks for a perfect match
        - IF understand() finds it, returns the index directly
        - ELSE understand compares it with all available RegEx and returns ALL possible matches
            - IF only one match was found, generates the corresponding answer
                - IF more than one match, tries to find the one with the least mistakes
                - ELSEIF multiple tied for the one with the least mistakes, tries to find the longest match
            - ELSE run it through SpaCy
                - IF pattern matches generate corresponding pattern answer (favours the longest match)
                - ELSEIF entity is found on utterance, generate based on entity
    - ELSE generate a response explaining that Mel does not know that
    :param input: Question or request the user is making
    :return: String corresponding to an answer
    """

    global nlp, match, entities, speech
    response = None

    intent = understand(input.lower())

    if len(intent) > 1:
        matches = bestOnErrors(intent)
        if len(matches) > 1:
            matches = bestOnLenght(matches)
            n = extract(matches[0])
            response = generate(n)
        else:
            n = extract(matches[0])
            response = generate(n)
    else:
        if len(intent) == 0 or intent[0] == -1:
            # SpaCy goes here
            values = nlp(input)

            matches = match(values)
            if len(matches) > 0:
                lowestMatch = 0
                currentMatch = ""
                for res in matches:
                    matchLen = list(res)[2] - list(res)[1]
                    if matchLen > lowestMatch:
                        lowestMatch = matchLen
                        currentMatch = nlp.vocab.strings[list(res)[0]]
                for entry in speech.values():
                    conv = dict(entry)
                    if conv.__contains__("name") and conv.get("name") == currentMatch:
                        response = conv.get("resp") if conv.__contains__("name") else None
                        break

            elif len(values.ents) > 0:
                response = ""
                for entity in values.ents:
                    if entities.__contains__(entity.label_):
                        response += entities.get(entity.label_).format(entity=entity.text)
        else:
            response = generate(extract(intent[0]))
    return response if response is not None and response != "" else generate(-1)


def main():
    """Implements a chat session in the shell.
    :rtype: None
    """
    print("Hello! I know stuff about chat bots. When you're done talking, just say 'goodbye'.")
    print()
    response = ""
    while True:
        statement = input("-->").lower()
        if dismissMel(statement):
            print("Bye bye!")
            break
        response = process(statement)
        print(response)
        print()
    print("Nice talking with you!")


questions, answers, speech, entities = loadJson('regStr.json')
nlp = spacy.load('en_core_web_md')
match = Matcher(nlp.vocab)
makePatterns(speech)
botName = r'(mel)((born)|bourne|[lbourney])*'
count = 0
