from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivy.lang.builder import Builder
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDIconButton, MDRectangleFlatButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import IRightBody, ThreeLineAvatarIconListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar
import pyrebase

firebaseConfig={
    "apiKey": "AIzaSyD6jsgVsHiD2vaGvDPR_4iCdTkXpbFQafo",
    "authDomain": "logistic-72ed4.firebaseapp.com",
    "databaseURL": "https://logistic-72ed4-default-rtdb.europe-west1.firebasedatabase.app",
    "projectId": "logistic-72ed4",
    "storageBucket": "logistic-72ed4.appspot.com",
    "messagingSenderId": "185587951953",
    "appId": "1:185587951953:web:d08e84237e77ce2b5b4b70",
    "measurementId": "G-RMEB749QCT"
}

firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()

def produs_saver(name, barcode, departament):
    data = {
        "name" : name,
        "departament" : departament,
        "barcode" : barcode
    }
    db.push(data)
    return True

def all():
    resp = db.get()
    return resp

def delete_by_id(id):
    db.child(id).remove()

def get_one_row(id):
    resp = db.child(id).get()
    return resp

def update_row(name, departament, barcode, id):
    db.child(id).update({
        "name": name,
        "departament": departament,
        "barcode": barcode
        })

kv_string = Builder.load_string(""" 
<MainWindow>:
    orientation: "vertical"

    MDToolbar: 
        title: "Depozit"
        MDIconButton:
            icon: "expand-all"
            on_release: app.get_all()

    MDBottomNavigation:
        id: bottom_navigation
        padding: 5
        MDBottomNavigationItem:
            name: "screen search"
            text: "căutare"
            icon: "database-search"

            MDBoxLayout:
                orientation: 'vertical'
                MDBoxLayout:
                    MDTextField:
                        id: search_name
                        hint_text: "Introduceți denumirea sau codul mărfii"
                        on_text:
                            app.name_search_and_fill(root.ids.search_name.text)
                    MDRectangleFlatButton:
                        text: "Caută"
                        on_release:
                            app.name_search_and_fill(root.ids.search_name.text)
                ScrollView:
                    size_hint: 1, 7
                    MDList:
                        id: search_results
                Widget:

        MDBottomNavigationItem:
            name: "screen add"
            text: "adauga"
            icon: "database-plus"

            MDBoxLayout:
                orientation: "vertical"
                MDTextField:
                    hint_text: "Introduceti numele produsului"
                    id: add_name
                    multiline: True
                MDTextField:
                    hint_text: "Introduceti departamentului"
                    id: add_departament
                MDTextField:
                    hint_text: "Introduceti barcodul produsului"
                    id: add_barcode
                Widget:
                MDFloatingActionButton:
                    icon: "plus"
                    md_bg_color: app.theme_cls.primary_color
                    pos_hint: {"center_x": .92, "center_y": .10}
                    on_release:
                        app.save_product(
                        root.ids.add_name.text, 
                        root.ids.add_departament.text, 
                        root.ids.add_barcode.text)

<SearchResulItem>:
    IconLeftWidget:
        icon: "pencil"
        on_release:
            root.get_one()
            root.show_udate_diaalog()
    RightButton:
        icon: "delete-alert"
        on_release: 
            root.show_confirm_dialog()
""")

class MainWindow(MDBoxLayout):
    pass

class RightButton(IRightBody, MDIconButton):
    pass  

class SearchResulItem(ThreeLineAvatarIconListItem):

    last_name = ''
    last_barcode = ''
    last_departament = ''

    def __init__(self, produs_id,**kwargs):
        super( SearchResulItem, self).__init__(**kwargs)
        self.produs_id = produs_id

    def delete_product(self, obj):
        delete_by_id(self.produs_id)
        self.close_dialog(obj)
        self.parent.remove_widget(self)

    def get_one(self):
        elm = get_one_row(self.produs_id)
        elm = elm.val()
        self.last_name = elm["name"]
        self.last_barcode = elm["barcode"]
        self.last_departament = elm["departament"]


    def show_confirm_dialog(self):
        self.dialog = MDDialog(title='Ștergeți înregistrarea?',
                                text = "Informația ștearsă nu poate fi restabilită",
                               size_hint=(0.6, 1),
                               buttons=[MDFlatButton(text='Închide', on_release=self.close_dialog),
                                        MDFlatButton(text='Șterge', on_release=self.delete_product,)]
                               )
        self.dialog.open()
    
    def show_udate_diaalog(self):
        content_layout = MDBoxLayout(
            orientation = "vertical",
            height = "130dp"
        )
        lsn = MDTextField(
            hint_text = "Denumirea produsului",
        )
        lsb = MDTextField(
            hint_text = "Barcodul produsului",
        )
        lsd = MDTextField(
            hint_text = "Departamentul produsului",
        )
        lsn.text = str(self.last_name)
        lsb.text = str(self.last_barcode)
        lsd.text = str(self.last_departament)
        def exchange(obj):
            self.last_name = lsn.text
            self.last_departament = lsd.text
            self.last_barcode = lsb.text
            self.update(obj)
        content_layout.add_widget(lsn)
        content_layout.add_widget(lsb)
        content_layout.add_widget(lsd)
        self.update_dialog = MDDialog(title='Editarea înregistrării:',
                                type = "custom",
                               size_hint=(.7, 8),
                               content_cls = content_layout,
                               buttons=[MDFlatButton(text='Închide',on_release=self.close_update_dialog),
                                        MDFlatButton(text='Reînoiește', on_release = exchange)]
                               )
        self.update_dialog.open()

    def update(self, obj):
        update_row(self.last_name, self.last_departament, self.last_barcode, self.produs_id)
        self.close_update_dialog(obj)
        LogisticApp.get_all(self)

    def close_dialog(self, obj):
        self.dialog.dismiss()

    def close_update_dialog(self, obj):
        self.update_dialog.dismiss()

class LogisticApp(MDApp):

    def clearWidgets(self):
        app = MDApp.get_running_app()
        result_list_widget = app.root.ids.search_results
        result_list_widget.clear_widgets()
        return result_list_widget

    def get_all(self):
        app = MDApp.get_running_app()
        result_list_widget = app.root.ids.search_results
        result_list_widget.clear_widgets()
        reponse = all()
        for product in reponse.each():
            value = product.val()
            value["key"] = product.key()
            result_list_widget.add_widget(
                SearchResulItem(text = value["name"], secondary_text=value["departament"], tertiary_text=value["barcode"], produs_id=value["key"])
            )

    def name_search_and_fill(self, query):
        result_list_widget = self.clearWidgets()
        response = all()
        for product in response.each():
            value = product.val()
            value["key"] = product.key()
            if query.lower() in value["name"].lower() or query.lower() in value["departament"].lower() or query in value["barcode"]:
                result_list_widget.add_widget(
                    SearchResulItem(text = value["name"], secondary_text=value["departament"], tertiary_text=value["barcode"], produs_id=value["key"])
                )

    def build(self):
        return MainWindow()

    def save_product(self, name, departament, barcode):
        if produs_saver(name, departament, barcode):
            app = MDApp.get_running_app()
            screen_manager = app.root.ids.bottom_navigation
            screen_manager.switch_tab("screen search")
            self.get_all()
            app.root.ids.add_name.text = ""
            app.root.ids.add_departament.text = ""
            app.root.ids.add_barcode.text = ""
    
    def on_start(self, **kwargs):
        self.get_all()

if __name__ == "__main__":
    LogisticApp().run()