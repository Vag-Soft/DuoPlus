import duolingo
import googletrans
import inspect
import json
from operator import attrgetter
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout  
from kivy.uix.gridlayout import GridLayout
from kivy.uix.carousel import Carousel
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.dropdown import DropDown


#Modifying the duolingo module to work with a JSON Web Token
source = inspect.getsource(duolingo)
new_source = source.replace('jwt=None', 'jwt')
new_source = source.replace('self.jwt = None', ' ')
exec(new_source, duolingo.__dict__)

 

def sortingKey(object):
    return object.known_langWord


class Word():
    def __init__(self, known_langWord, learning_langWord, learning_langPronunciation):
        self.known_langWord = known_langWord
        self.learning_langWord = learning_langWord
        self.learning_langPronunciation = learning_langPronunciation

    def __eq__(self, object):
        return self.known_langWord==object.known_langWord and self.learning_langWord==object.learning_langWord and self.learning_langPronunciation==object.learning_langPronunciation

    def printWord(self):
        print(self.known_langWord, self.learning_langWord, self.learning_langPronunciation)


class LoginScreen(Screen):
    def login(self, username, jwt):
        data = {"username": username, "jwt": jwt}

        with open("credentials.json", "w") as f:
            json.dump(data, f, indent=4)
        
        initial_code(username=username, jwt=jwt)
        
        self.parent.add_widget(MainScreen(name='Main'))
        self.parent.current = "Main"


class MainScreen(Screen):
    pass


class MainWidget(BoxLayout):   
    
    def slideCarousel(self, slide):
        self.children[1].load_slide(self.children[1].slides[slide])


class KnownWordsGrid(GridLayout):
    
    def fill_grid(self, wordList):
        known_lang = Label(text=settings["known_lang"], size_hint=(1, None), height="50dp", font_name="Fonts/unifont-15.0.01.ttf", font_size=0.04*self.width)  
        learning_lang = Label(text=settings["learning_lang"], size_hint=(1, None), height="50dp", font_name="Fonts/unifont-15.0.01.ttf", font_size=0.04*self.width) 
        pronunciation = Label(text="Pronunciation", size_hint=(1, None), height="50dp", font_name="Fonts/unifont-15.0.01.ttf", font_size=0.04*self.width)
        pronun_audio = Label(text="Audio", size_hint=(1, None), height="50dp", font_name="Fonts/unifont-15.0.01.ttf", font_size=0.04*self.width)
        self.add_widget(known_lang)
        self.add_widget(learning_lang)
        self.add_widget(pronunciation)
        self.add_widget(pronun_audio)

        for word in wordList:
            temp = Label(text = word.known_langWord, size_hint=(1, None), height="40dp", font_name="Fonts/unifont-15.0.01.ttf", font_size=0.03*self.width)
            self.add_widget(temp)

            temp = Label(text = word.learning_langWord, size_hint=(1, None), height="40dp", font_name="Fonts/unifont-15.0.01.ttf", font_size=0.03*self.width)
            self.add_widget(temp)

            temp = Label(text = word.learning_langPronunciation, size_hint=(1, None), height="40dp", font_name="Fonts/unifont-15.0.01.ttf", font_size=0.03*self.width)
            self.add_widget(temp)

            temp = Label(text = "COMING SOON", size_hint=(1, None), height="40dp", font_name="Fonts/unifont-15.0.01.ttf", font_size=0.03*self.width)
            self.add_widget(temp)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.fill_grid(wordList)

            

    def refresh(self, learning_lang_update, known_lang_update):
        
        global wordList
        if learning_lang_update:
            global duo

            learning_lang_abbr = duo.get_abbreviation_of(settings["learning_lang"])
            
            known_lang_abbr = googletrans.LANGCODES[settings["known_lang"].lower()]
            
            vocab = duo.get_vocabulary(learning_lang_abbr)       
            
            unsortedOriginalWords = []
            for word in vocab.get("vocab_overview"):
                unsortedOriginalWords.append(word.get("word_string"))
            
            unsortedTranslatedObjects = trans.translate(unsortedOriginalWords, dest=known_lang_abbr)               
            
            unsortedPronunciationObjects = trans.translate(unsortedOriginalWords, dest=learning_lang_abbr)               
            
            wordList = []
            for i in range(len(unsortedOriginalWords)):
                tempWord = Word(str(unsortedTranslatedObjects[i].text).lower(), unsortedOriginalWords[i], str(unsortedPronunciationObjects[i].pronunciation).lower())
                if(not(tempWord in wordList)):
                    wordList.append(tempWord)
            wordList.sort(key = sortingKey)     

            
            self.clear_widgets()
            
            self.fill_grid(wordList)
        
        elif known_lang_update:
            known_lang_abbr = googletrans.LANGCODES[settings["known_lang"].lower()]

            sortedOriginalWords = list(map(attrgetter('learning_langWord'), wordList))

            sortedTranslatedObjects = trans.translate(sortedOriginalWords, dest=known_lang_abbr)

            for i in range(len(wordList)):
                wordList[i].known_langWord = str(sortedTranslatedObjects[i].text).lower()
            wordList.sort(key = sortingKey)  

                
            self.clear_widgets()
            
            self.fill_grid(wordList)    
            


class SettingsTab(BoxLayout):



    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        
        learning_langs_label = Label(text="Learning language", size_hint=(1, 0.05), pos_hint={'center_x': 0.5}, font_name="Fonts/unifont-15.0.01.ttf", font_size=0.2*self.width)
        learning_langs_button = Button(text=settings["learning_lang"], size_hint=(0.5, 0.1), pos_hint={'center_x': 0.5}, font_name="Fonts/unifont-15.0.01.ttf", font_size=0.2*self.width)

        self.learning_langs_dropdown = DropDown()
        for i in settings["learning_langs"]:
            temp = Button(text=i, size_hint_y=None, height=50, font_name="Fonts/unifont-15.0.01.ttf", font_size=0.2*self.width)

            temp.bind(on_release=lambda temp: self.learning_langs_dropdown.select(temp.text))

            self.learning_langs_dropdown.add_widget(temp)

        learning_langs_button.bind(on_release=self.learning_langs_dropdown.open)
        self.learning_langs_dropdown.bind(on_select=lambda instance, x: setattr(learning_langs_button, 'text', x))
        
        
        known_lang_label = Label(text="Known language", size_hint=(1, 0.05), pos_hint={'center_x': 0.5}, font_name="Fonts/unifont-15.0.01.ttf", font_size=0.2*self.width)
        known_lang_button = Button(text=settings["known_lang"], size_hint=(0.5, 0.1), pos_hint={'center_x': 0.5}, font_name="Fonts/unifont-15.0.01.ttf", font_size=0.2*self.width)
        
        self.known_lang_dropdown = DropDown()
        for i in googletrans.LANGUAGES.values():
            btn = Button(text=i.capitalize(), size_hint_y=None, height=50, font_name="Fonts/unifont-15.0.01.ttf", font_size=0.2*self.width)

            btn.bind(on_release=lambda btn: self.known_lang_dropdown.select(btn.text))

            self.known_lang_dropdown.add_widget(btn)

        known_lang_button.bind(on_release=self.known_lang_dropdown.open)
        self.known_lang_dropdown.bind(on_select=lambda instance, x: setattr(known_lang_button, 'text', x))


        
        
        def save_settings(self):
            learning_lang_update = False
            known_lang_update = False
            if settings["learning_lang"] != learning_langs_button.text:
                learning_lang_update = True
                settings["learning_lang"] = learning_langs_button.text
            if settings["known_lang"] != known_lang_button.text:
                known_lang_update = True
                settings["known_lang"] = known_lang_button.text

            with open("settings.json", "w") as f:
                json.dump(settings, f, indent=4)

            
            self.parent.parent.parent.ids.scroll.ids.grid.refresh(learning_lang_update, known_lang_update);


        save_button = Button(text="Save", size_hint=(0.2, 0.1), pos_hint={'center_x': 0.9}, font_name="Fonts/unifont-15.0.01.ttf", font_size=0.25*self.width)
        save_button.bind(on_release=save_settings)

        
        
        filler1 = Label(size_hint=(1, 0.03))
        filler2 = Label(size_hint=(1, 0.75))

        self.add_widget(learning_langs_label)
        self.add_widget(learning_langs_button)
        self.add_widget(filler1)
        self.add_widget(known_lang_label)
        self.add_widget(known_lang_button)
        self.add_widget(filler2)
        self.add_widget(save_button)


class DuoPlus(App):
    
    def build(self):
        screen_manager = ScreenManager()
        
        
        with open("credentials.json", "r") as f:
            data = json.load(f)

        jwt = data["jwt"]
        username = data["username"]

        if jwt == "" or username =="":
            screen_manager.add_widget(LoginScreen(name='Login'))
        else:
            initial_code(username=username, jwt=jwt)
            screen_manager.add_widget(MainScreen(name='Main'))
        
        return screen_manager
   

duo = None
trans = googletrans.Translator()


unsortedOriginalWords = []
wordList = []
with open("settings.json", "r") as f:
    settings = json.load(f)
def initial_code(username, jwt):
    global duo
    duo  = duolingo.Duolingo(username=username, jwt = jwt)
    
    settings["learning_langs"] = duo.get_languages()

    
    known_lang_abbr = googletrans.LANGCODES[settings["known_lang"].lower()]
    if settings["learning_lang"] == "":
        settings["learning_lang"] = settings["learning_langs"][len(settings["learning_langs"]) - 1]
    
    learning_lang_abbr = duo.get_abbreviation_of(settings["learning_lang"])
    vocab = duo.get_vocabulary(learning_lang_abbr)

    
    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=4)


    for word in vocab.get("vocab_overview"):
        unsortedOriginalWords.append(word.get("word_string"))
    unsortedTranslatedObjects = trans.translate(unsortedOriginalWords, dest=known_lang_abbr)
    unsortedPronunciationObjects = trans.translate(unsortedOriginalWords, dest=learning_lang_abbr)
    
    global wordList
    for i in range(len(unsortedOriginalWords)):
        tempWord = Word(str(unsortedTranslatedObjects[i].text).lower(), unsortedOriginalWords[i], str(unsortedPronunciationObjects[i].pronunciation).lower())
        if(not(tempWord in wordList)):
            wordList.append(tempWord)
    wordList.sort(key = sortingKey) 
    
    

DuoPlus().run()
