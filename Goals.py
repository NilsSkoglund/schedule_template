import streamlit as st
from datetime import datetime, time
from deta import Deta
from funcs import helper_funcs
############################## Sessuin State ###################################
if "current_date" not in st.session_state:
    st.session_state["current_date"] = datetime.now().date()
    st.session_state["current_year"] = datetime.now().date().year
    st.session_state["current_month"] = datetime.now().date().month

    st.session_state["current_quarter"] =\
         (st.session_state["current_month"]-1)//3

# Connect to Deta Base
if "deta" not in st.session_state:
    st.session_state["deta"] = Deta(st.secrets["deta_key"])
table = "Quarterly_goals"
db = st.session_state["deta"].Base(table)
def fetch_from_db():
    return db.fetch().items

################################ functions ####################################
def add_goal_to_db(dct):
    # Connect to Deta Base
    db = Deta(st.secrets["deta_key"]).Base("Quarterly_goals")
    namn = dct["namn"]
    kvartal = dct["kvartal"]
    key = kvartal+namn
    
    try:
        db.insert(dct, key)
    except:
        st.error(f"Mål med namn {namn} finns redan för {kvartal}")

def get_goal_end_date(kvartal, år):
    if kvartal == "Q1":
        return år, 3, 31
    elif kvartal == "Q2":
        return år, 6, 30
    elif kvartal == "Q3":
        return år, 9, 30
    elif kvartal == "Q4":
        return år, 12, 31


def skapa_mål_func(kvartal, år):

    with st.form("my_form", clear_on_submit=True):
        st.subheader("Skapa mål")
        namn = st.text_input("Namn på målet")
        beskrivning = st.text_input("Beskriv ditt mål")
        year, month, day = get_goal_end_date(kvartal, år)
        datum = st.date_input(
            "När ska målet vara uppnåt?",
            datetime(year, month, day))
        noteringar = st.text_area("Övriga anteckningar")

        submitted = st.form_submit_button("Skapa mål")

        if submitted:
            temp_dct = {"år": år
                        , "kvartal":kvartal
                        , "namn":namn
                        , "beskrivning":beskrivning
                        , "datum": {"år": datum.year
                            , "månad":datum.month
                            , "dag":datum.day}
                        , "noteringar":noteringar
                        , "uppnått": False}
            add_goal_to_db(temp_dct)            

def goal_reached_update_db(item, key):
    item["uppnått"] = st.session_state[key]
    db = Deta(st.secrets["deta_key"]).Base("Quarterly_goals")
    db.put(item)

def display_goal(item):

    with st.expander(item["namn"]):
        st.markdown("---")
        st.markdown("**Beskrivning av mål:**")
        st.write(item["beskrivning"])
        st.markdown("**Datum för mål:**")
        datum = item['datum']
        datum_string = f"{datum['år']}-{datum['månad']}-{datum['dag']}"
        st.write(datum_string)
        if item["noteringar"] != "":
            st.markdown("**Övriga noteringar:**")
            st.write(item["noteringar"])
        key = item["key"] + "uppnått"
        st.checkbox("Uppnåt"
                    , value = item["uppnått"]
                    , key = key
                    , on_change=goal_reached_update_db
                    , args = (item, key))

def display_goals(kvartal, år):
    db = Deta(st.secrets["deta_key"]).Base("Quarterly_goals")
    items = db.fetch({"år": år, "kvartal": kvartal}).items

    if len(items) == 0:
        st.info(f"Finns inga mål för {kvartal} - {år}")    

    for item in items:
        display_goal(item)

def ta_bort_mål(key):
    db = Deta(st.secrets["deta_key"]).Base("Quarterly_goals")
    db.delete(key)

def meny_ta_bort_mål(kvartal, år):
    db = Deta(st.secrets["deta_key"]).Base("Quarterly_goals")
    items = db.fetch({"år": år, "kvartal":kvartal}).items

    display = "Tryck i checkbox för att ta bort målet"
    with st.expander(display, expanded = True):

        for item in items:                
            st.checkbox(item['namn']
                        , key = item["key"]
                        , on_change = ta_bort_mål
                        , args = (item["key"], ))

def modify_item(key, col):
    if col == "datum":
        col == st.session_state[key+col]
        dct = {"datum": {"år": col.year
                            , "månad":col.month
                            , "dag":col.day}}
        db.update(dct, key)
    else:
        dct = {col:st.session_state[key+col]}
        db.update(dct, key)

def edit_goals(kvartal, år):
    items = db.fetch({"år": år}).items

    items = list(filter(lambda item: item['kvartal'] == kvartal, items))

    for item in items:
        with st.expander(item["namn"]):
            col = "år"
            key = item["key"] + col
            st.number_input(col
                        , value=item[col]
                        , key=key
                        , on_change=modify_item
                        , args=(item["key"], col,)
                        , label_visibility="visible")
            col = "kvartal"
            key = item["key"] + col
            st.radio(col
                    , options=("Q1", "Q2", "Q3", "Q4")
                    , key=key
                    , on_change=modify_item
                    , args=(item["key"], col,)
                    , horizontal=True
                    , label_visibility="visible")
            col = "datum"
            key = item["key"] + col
            year, month, day = get_goal_end_date(kvartal, år)
            st.date_input(col
                        , value=datetime(year, month, day)
                        , key=key
                        , on_change=modify_item
                        , args=(item["key"], col,)
                        , label_visibility="visible")

            text_input_cols = ["namn", "beskrivning"]
            for col in text_input_cols:
                key = item["key"] + col
                st.text_input(col
                            , value=item[col]
                            , key=key
                            , on_change=modify_item
                            , args=(item["key"], col,)
                            , label_visibility="visible")

            col = "noteringar"
            key = item["key"] + col
            st.text_area(col
                        , value=item[col]
                        , key=key
                        , on_change=modify_item
                        , args=(item["key"], col,)
                        , label_visibility="visible")

################################# Program #####################################

with st.expander("Ändra år och kvartal"):
    current_year = st.session_state["current_year"]
    lista_år = list(range(current_year, current_year+5))
    välj_år = st.radio("Vilket år vill du se?"
                            , lista_år
                            , horizontal=True)
    välj_år = int(välj_år)

    välj_kvartal = st.radio("Vilket kvartal vill du se?"
                            , ('Q1', 'Q2', 'Q3', 'Q4')
                            , index=st.session_state["current_quarter"]
                            , horizontal=True)
                            
st.header(f"{välj_kvartal} - {välj_år}")
page = "_mål"

choice = helper_funcs.options_menu_dev(page)

st.markdown("---")

if choice == "show":
    display_goals(välj_kvartal, välj_år)

if choice == "add":
    st.write("---")
    skapa_mål_func(välj_kvartal, välj_år)

if choice == "edit":
    st.write("---")
    edit_goals(välj_kvartal, välj_år)

if choice == "remove":
    st.write("---")
    meny_ta_bort_mål(välj_kvartal, välj_år)

# st.radio("Välj vy"
#         , ("Visningsvy", "Redigeringsvy")
#         , horizontal=True
#         , label_visibility="collapsed"
#         , key = "vy_mål")
            
# st.markdown("---")


# if st.session_state["vy_mål"] == "Visningsvy":
#     display_goals(välj_kvartal, välj_år)

# if st.session_state["vy_mål"] == "Redigeringsvy":

#     st.radio("Välj ..."
#             , ("Lägg till", "Redigera", "Ta bort")
#             , horizontal=True
#             , label_visibility="collapsed"
#             , key = "val_redigering_mål")

#     if st.session_state["val_redigering_mål"] == "Lägg till":
#         st.write("---")
#         skapa_mål_func(välj_kvartal, välj_år)
#     elif st.session_state["val_redigering_mål"] == "Redigera":
#         st.write("---")
#         edit_goals(välj_kvartal, välj_år)
#     elif st.session_state["val_redigering_mål"] == "Ta bort":
#         st.write("---")
#         meny_ta_bort_mål(välj_kvartal, välj_år)    




