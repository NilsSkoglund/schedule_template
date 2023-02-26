import streamlit as st
from datetime import datetime
from deta import Deta
from funcs import helper_funcs

############################### Session state #################################
if "deta" not in st.session_state:
    st.session_state["deta"] = Deta(st.secrets["deta_key"])

################################# Variables ###################################
table = "weekly_schedule"
db = st.session_state["deta"].Base(table)

current_week = str(datetime.now().date().isocalendar().week)

lista_veckodagar = [
    "måndag"
    , "tisdag"
    , "onsdag"
    , "torsdag"
    , "fredag"
    , "lördag"
    , "söndag"
]
db_workouts = st.session_state["deta"].Base("workouts_new")
workouts = [i["Namn"] for i in db_workouts.fetch().items]

################################# Functions ###################################

# choice == "show"
def select_weeks():
    weeks = [item["key"] for item in db.fetch().items]
    
    if current_week in weeks:
        options = st.multiselect("Välj vecka att visa"
                             , weeks
                             , default=[current_week])
    else:
        options = st.multiselect("Välj vecka att visa"
                             , weeks)
    return options

def exercise_widgets_update_db(widget_str, week, day, workout):
    db_item = db.get(week)
    db_item[day][workout][widget_str] =\
            st.session_state[f"{widget_str}{week}{day}{workout}"]

def display_exercises(item, day):
    for key in item[day].keys():                        
        st.markdown("---")
        st.subheader(key)

        current_item = item[day][key]

        genomfört = current_item["Genomfört"]
        genomfört_string = f"Genomfört{item['key']}{day}{key}"                    
        st.checkbox("Genomfört pass"
                , value = genomfört
                , key = genomfört_string
                , on_change = exercise_widgets_update_db
                , args=("Genomfört", item['key'], day, key))
        
        kommentar = current_item["Kommentar"]
        kommentar_string = f"Kommentar{item['key']}{day}{key}"
        st.text_area("Kommentar"
                    , value = kommentar
                    , key = kommentar_string
                    , on_change = exercise_widgets_update_db
                    , args = ("Kommentar", item['key'], day, key))

def display_week(db_items, weeks):
    for item in db_items:
        if item["key"] in weeks:
            st.header(f"Vecka {item['key']}")
            for day in lista_veckodagar:
                if len(item[day]) > 0:
                    with st.expander(day):
                        display_exercises(item, day)
    
# choice == "add/edit"

def choose_week():
    st.date_input(
    "Välj veckostart för den vecka du vill skapa/redigera träningsschema för"
    , datetime.date(datetime.now())
    , key = "first_day_of_week"
    )

    if "first_day_of_week" in st.session_state:
        week_from_input =\
            str(st.session_state["first_day_of_week"].isocalendar().week)
    
    return week_from_input

def insert_weekly_schedule_db(chosen_week):
    '''
        Create a new entry for chosen week in db
        Insert will throw an error if week already exists in db
    '''
    dct_temp = {"note":""}
    for day in lista_veckodagar:
        dct_temp[day] = {}
    try:
        db.insert(dct_temp, key = f"{chosen_week}")
    except:
        pass

def list_days():    
    col1, col2 = st.columns(2)

    stop_index = 4
    with col1:
        for day in lista_veckodagar[:stop_index]:
            st.checkbox(
                f"Lägg till pass {day}"
                , key=day
            )
    with col2:
        for day in lista_veckodagar[stop_index:]:
            st.checkbox(
                f"Lägg till pass {day}"
                , key=day
            )

def add_workout_to_weekly_schedule(day, week):
    if st.session_state[f"selectbox_{day}"] != "Välj pass":
        db_res = db.get(f"{week}")    
        pass_namn =  st.session_state[f"selectbox_{day}"]
        temp_dct = {"Genomfört": False
                , "Kommentar": ""}
        db_res[day].update({pass_namn: temp_dct})
        db.put(db_res)
    else:
        pass

def remove_workout_from_schedule(week, day, workout):
    item = db.get(week)
    del item[day][workout]
    db.put(item)

def loop_days(chosen_week):
    for day in lista_veckodagar:

        if st.session_state[day]:
            with st.expander(day):
                st.selectbox(""
                    , options = ["Välj pass"] + workouts
                    , key = f"selectbox_{day}"
                    , on_change = add_workout_to_weekly_schedule
                    , args = (day, chosen_week, )
                    , label_visibility = "collapsed"
                )

                week_dct = db.get(chosen_week)
                if len(week_dct[day].keys()) == 0:
                    st.markdown("- Inget pass inlagt")
                else:
                    st.markdown("**Nedan visas inlagda pass.\
                                 Klicka i boxen för att ta bort ett pass**")
                    for workout in week_dct[day].keys():
                        key = f"Remove {chosen_week} {day} {workout}"
                        st.checkbox(workout
                                    , key=key
                                    , on_change=remove_workout_from_schedule
                                    , args=(chosen_week, day, workout))


def add_weekly_schedule():
    chosen_week = choose_week()
    insert_weekly_schedule_db(chosen_week)
    st.subheader(f"Vecka {chosen_week}")
    list_days()
    loop_days(chosen_week)

# choice == "remove"

def remove_workout(key):
    db.delete(key)

def menu_remove_workout():
    items = db.fetch().items
    display = "Tryck i checkbox för att ta bort veckoschema"
    with st.expander(display, expanded = True):
        for item in items:                
            st.checkbox(f"Vecka: {item['key']}"
                        , key = item["key"]
                        , on_change = remove_workout
                        , args = (item["key"], ))

################################## Program ####################################

st.subheader(f"Dagens datum: {datetime.now().date()}")
st.write(f"Veckonummer: {current_week}")

page = "veckoschema"
choice = helper_funcs.options_menu_dev(page)

if choice == "show":
    weeks = select_weeks()
    
    display_week(db.fetch().items, weeks)

if choice == "add/edit":
    add_weekly_schedule()

if choice == "remove":
    menu_remove_workout()

