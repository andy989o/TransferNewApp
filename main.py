from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import ButtonBehavior, Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, ListProperty
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
import mysql.connector

db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "Q2s5!tmn6L7",
    database = "TransferNew"
)

cursor = db.cursor(buffered = True)

# Creating database if it doesn't exist
cursor.execute("CREATE DATABASE IF NOT EXISTS TransferNew")
# Creating table if it doesn't exist
cursor.execute("CREATE TABLE IF NOT EXISTS registeredusers(Username VARCHAR(255), Email VARCHAR(255), Password VARCHAR(255), Urges INT(255), Money INT(255), Calories INT(255))")

class LabelButton(ButtonBehavior, Label):
    pass

class ImageButton(ButtonBehavior, Image):
    pass


class SettingsScreen(Screen):
    def on_enter(self):
        self.ids.settings_button.source = "icons/settings_icon_pressed.png"
    def on_leave(self):
        self.ids.settings_button.source = "icons/settings_icon.png"

class SupportScreen(Screen):
    zipcodeInput = ObjectProperty(None)
    def checkZipcode(self):
        zipcode = self.zipcodeInput.text
        query = "SELECT * FROM " + "`" + zipcode + "`" + ";"
        cursor.execute(query)
        fetchInfo = cursor.fetchall()
        pop = Popup(title='Nearby Clinics',
                        content=Label(text=(('\n'.join(map(lambda x: str(x[0]) + '\n' + str(x[1]), fetchInfo))))),
                        size_hint=(None, None), size=(600, 600))
        pop.open()
    def healthTips(self):
        pop = Popup(title='Health Tips',
                        content=Label(text="1. Highdryating Foods\n- Alcohol dehydates your body so it is essential to \nkeep hydrated during detox and recovery\n\n2. High Quality Protein\n- Protein is used to help the body repair \nitself after chronic alcohol use\n\n3. Bright Fruits and Veggies\n- Chronic alcohol use can cause nutrient deficiences, \nand fruits and vegetables are one of the best \nways to restore these imbalances\n\n4. Healthy Carbohydrates\n- Healthy carbohydrates help provide your \nbody energy to repair itself after alcohol addiction\n\n5. Nuts, Seeds, and Other Sources of Healthy Fats\n- Alcohol consumption can damage your brain \nand healthy fatty acids help the brain function optimally"),
                        size_hint=(None, None), size=(600,600))
        pop.open()
    def on_enter(self):
        self.ids.support_button.source = "icons/support_icon_pressed.png"
    def on_leave(self):
        self.ids.support_button.source = "icons/support_icon.png"


def invalidLogin():
    pop = Popup(title='Invalid Login',
                  content=Label(text='Invalid username or password'),
                  size_hint=(None, None), size=(400, 400))
    pop.open()

def invalidEntry():
    pop = Popup(title='Invalid Entry',
                  content=Label(text='Please a number for each'),
                  size_hint=(None, None), size=(400, 400))
    pop.open()
    
class RegisterScreen(Screen):
    usernameInput = ObjectProperty(None)
    emailInput = ObjectProperty(None)
    passwordInput = ObjectProperty(None)

    def addInfoToDB(self):
        query = "INSERT INTO registeredusers (Username, Email, Password, Urges, Money, Calories) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (self.usernameInput.text, self.emailInput.text, self.passwordInput.text, 0, 0, 0)
        cursor.execute(query, values)
        db.commit()
        self.parent.current = 'login_screen'

class LoginScreen(Screen):
    user = 3
    usernameInputLogin = StringProperty
    passwordInputLogin = StringProperty
    def checkIfDetailsExist(self):
        cursor.execute("SELECT Username, Password FROM registeredusers")
        fetchInfo = cursor.fetchall()
        global username, password
        username = self.usernameInputLogin.text
        password = self.passwordInputLogin.text
        if tuple((username, password)) in fetchInfo:
            self.parent.current = 'tracking_screen'
        else:
            invalidLogin()

class TrackingScreen(Screen):
    global urgesInput, moneyInput, caloriesInput
    urgesInput = NumericProperty
    moneyInput = NumericProperty
    caloriesInput = NumericProperty

    def addDataToDB(self):
        urgesInput = self.urgesInput.text
        moneyInput = self.moneyInput.text
        caloriesInput = self.caloriesInput.text
        if urgesInput.isnumeric() and moneyInput.isnumeric() and caloriesInput.isnumeric():
            query = "UPDATE transfernew.registeredusers set Urges = Urges + " + urgesInput + ", Money = Money + " + moneyInput + ", Calories = Calories + " + caloriesInput + " where Username = " + "'" + username + "'" + ";"
            cursor.execute(query)
            db.commit()
            self.parent.current = 'progress_screen'
        else:
            invalidEntry()

class ProgressScreen(Screen):
    username = StringProperty
    password = StringProperty
    def on_enter(self):
        self.ids.progress_button.source = "icons/progress_icon_pressed.png"
        global username, password
        loginscreen = self.manager.get_screen('login_screen')
        self.username = loginscreen.usernameInputLogin.text
        self.password = loginscreen.passwordInputLogin.text
        cursor.execute("SELECT Urges, Money, Calories FROM registeredusers WHERE Username = " + "'" + username + "'" + " and Password = " + "'" + password + "'" + ";" ";")
        fetchInfo = cursor.fetchall()
        global urges
        urges = fetchInfo[0][0]
        money = fetchInfo[0][1]
        calories = fetchInfo[0][2]
        self.ids.urges_label.text = f'  {urges}'
        self.ids.money_label.text = f'${money}'
        self.ids.calories_label.text = f'  {calories}'
    def on_leave(self):
        self.ids.progress_button.source = "icons/progress_icon.png"
    def pledge(self):
        current = int(self.ids.progress_bar.value)
        if current == 30:
            current = 0
        else:
            current += 1

        self.ids.progress_bar.value = current
        self.ids.streak.text = f'{current}'

GUI = Builder.load_file("main.kv")

class MainApp(App):
    def build(self):
        return GUI
    
    def change_screen(self, screen_name):
        # Get screen manager from kv file
        screen_manager = self.root.ids['screen_manager']
        screen_manager.current = screen_name
        #screen_manager = self.root.ids



if __name__ == "__main__":
    MainApp().run()