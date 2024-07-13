from wonderwords import RandomWord
import requests
import random
def generate_name():
    r = RandomWord()
    name = ""
    while len(name) < 14:
        word = r.word()
        name += word
    return name[:14]  # Ensure it's not longer than 14 characters

def generate_title():
    r = RandomWord()
    title = ""
    while len(title) < 60:
        if len(title) > 11:
            break
        word = r.word()
        title += word
    return title  # Ensure it's not longer than 60 characters

def generate_thread_text():
    r = RandomWord()
    thread_text = ""
    while len(thread_text) < 600:
        word = r.word()
        thread_text += word + " "
    return thread_text.strip()

def generate_category():
    categories = ["jobb", "lön", "arbetsmiljö", "arbetsgivare", "kultur","VD","arbetstider","ledighet"]
    return random.choice(categories)





