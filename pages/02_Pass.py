import streamlit as st
from datetime import datetime
from deta import Deta
from funcs import helper_funcs


############################### Session state #################################
if "deta" not in st.session_state:
    st.session_state["deta"] = Deta(st.secrets["deta_key"])

################################# Variables ###################################
table = "workouts_new"
db = st.session_state["deta"].Base(table)

################################# Functions ###################################

def add_workout_db(key, name, exercises, time, notes):
    dct = {"Namn":name
           , "Övningar": exercises
           , "Tidsåtgång (minuter)": time
           , "Anteckningar": notes
           }
    db.put(dct, key)

def add_workout():
    with st.form("my form", clear_on_submit=True):
        st.subheader("Skapa pass")
        key = helper_funcs.generate_key(db)
        name = st.text_input("Ange namn på pass")
        exercises = st.text_area("Lägg in övningar")
        time = st.number_input("Uppskattad tidsåtgång (minuter)", value=30)
        notes = st.text_area("Allmänna anteckningar")
        submitted = st.form_submit_button("Skapa pass")
        if submitted:
            add_workout_db(key
                      , name
                      , exercises
                      , time
                      , notes
                      )


def select_exercises():
    exercise_names = [item["Namn"] for item in db.fetch().items]
    options = st.multiselect("Välj pass att visa"
                             , exercise_names)
    return options

def display_workouts(options):
    workouts = db.fetch().items
    filtered_w = list(filter(lambda x: x['Namn'] in options, workouts))
    for w in filtered_w:
        with st.expander(w["Namn"], expanded=True):
            st.write("**Övningar**")
            st.markdown(w["Övningar"])
            st.write("")

            st.markdown(f"**Uppskattad tidsåtgång**")
            st.markdown(f"{w['Tidsåtgång (minuter)']} min")

            st.write("**Anteckningar**")
            st.markdown(w["Anteckningar"])

def edit_workout_db(key, col):
    new_val = st.session_state[key+col]
    dct = {col: new_val}
    db.update(dct, key)




def edit_workout(options):
    workouts = db.fetch().items
    filtered_w = list(filter(lambda x: x['Namn'] in options, workouts))
    for w in filtered_w:
        key = w["key"]
        with st.expander(w["Namn"], expanded=True):
            col = "Namn"
            st.text_input(col
                          , value=w[col]
                          , key = key+col
                          , help = "Om du byter namn behöver du välja\
                            det nya namnet från dropdown-menyn"
                          , on_change=edit_workout_db
                          , args=(key, col, )
            )

            col = "Övningar"
            st.text_area(col
                          , value=w[col]
                          , key = key+col
                          , on_change=edit_workout_db
                          , args=(key, col, )
            )

            col = "Tidsåtgång (minuter)"
            st.number_input(col
                          , value=w[col]
                          , key = key+col
                          , on_change=edit_workout_db
                          , args=(key, col, )
            )

            col = "Anteckningar"
            st.text_area(col
                          , value=w[col]
                          , key = key+col
                          , on_change=edit_workout_db
                          , args=(key, col, )
            )

def remove_workout(key):
    db.delete(key)

def menu_remove_workout():
    items = db.fetch().items
    display = "Tryck i checkbox för att ta bort målet"
    with st.expander(display, expanded = True):
        for item in items:                
            st.checkbox(item['Namn']
                        , key = item["key"]
                        , on_change = remove_workout
                        , args = (item["key"], ))

################################## Program ####################################
page = "pass"
choice = helper_funcs.options_menu_dev(page)

if choice == "show":
    options = select_exercises()
    st.write("---")
    display_workouts(options)

if choice == "add":
    add_workout()

if choice == "edit":
    options = select_exercises()
    st.write("---")
    edit_workout(options)

if choice == "remove":
    menu_remove_workout()
