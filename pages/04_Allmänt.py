import streamlit as st
from datetime import datetime, time
from deta import Deta
import string
import random
import time
from funcs import helper_funcs

# Connect to Deta Base
if "deta" not in st.session_state:
    st.session_state["deta"] = Deta(st.secrets["deta_key"])
table = "general"
db = st.session_state["deta"].Base(table)
def fetch_from_db():
    return db.fetch().items

# functions

def add_comment_to_db(key, rubrik, text):
    db.put({"Rubrik":rubrik, "Comment":text}, key)
def add_recommendation():

    ascii = string.ascii_uppercase
    key = "".join([random.choice(ascii) for i in range(16)])
    items = fetch_from_db()
    keys = [i["key"] for i in items]
    while key in keys:
        key = "".join([random.choice(ascii) for i in range(16)])

    with st.form("My form", clear_on_submit=True):

        rubrik = st.text_input("Rubrik")
        text = st.text_area("Kommentar:")
        # Every form must have a submit button.
        submitted = st.form_submit_button("Lägg till rekommendation")
        if submitted:
            rubrik = rubrik.strip().title()
            add_comment_to_db(key, rubrik, text)
            st.info("Rekommendation tillagd")

def modify_item(key, col):
    db.update({col:st.session_state[key+col]}, key)

def display_recommendations():

    items = fetch_from_db()
    rubriker = [item["Rubrik"] for item in items]
    unika_rubriker = set(rubriker)

    for rubrik in unika_rubriker:
        st.subheader(rubrik)
        filtered_items =\
             list(filter(lambda item: item['Rubrik'] == rubrik, items))
        for item in filtered_items:
            st.write(item["Comment"])

def edit_recommendations():
    items = fetch_from_db()
    # rubriker = [item["Rubrik"] for item in items]
    # unika_rubriker = set(rubriker)

    # for rubrik in unika_rubriker:
    #     st.subheader(rubrik)
    #     filtered_items = list(filter(lambda person: person['Rubrik'] == rubrik, items))
    for item in items:
        col = "Rubrik"
        key = item["key"] + col
        st.text_input("Rubrik"
                    , value=item["Rubrik"]
                    , key=key
                    , on_change=modify_item
                    , args=(item["key"], col,)
                    , label_visibility="visible")
        col = "Comment"
        key = item["key"] + col
        st.text_area("Rekommendation"
                    , value=item["Comment"]
                    , key=key
                    , on_change=modify_item
                    , args=(item["key"], col,)
                    , label_visibility="visible")
        st.markdown("---")

def remove_recommendations():
    def remove_single_recommendation(key):
        db.delete(key)

    items = fetch_from_db()
    rubriker = [item["Rubrik"] for item in items]
    unika_rubriker = set(rubriker)

    for rubrik in unika_rubriker:
        st.subheader(rubrik)
        filtered_items =\
             list(filter(lambda item: item['Rubrik'] == rubrik, items))
        for item in filtered_items:
            st.write(item["Comment"])
            st.checkbox("Ta bort"
                    , key=item["key"]
                    , on_change=remove_single_recommendation
                    , args=(item["key"], )
                    , label_visibility="visible")
        st.markdown("---")

################################# Program #####################################
page = "allmänt"
choice = helper_funcs.options_menu_dev(page)

st.markdown("---")

if choice == "show":
    display_recommendations()

if choice == "add":
    st.write("---")
    add_recommendation()

if choice == "edit":
    st.write("---")
    edit_recommendations()

if choice == "remove":
    st.write("---")
    remove_recommendations()
# vy = st.radio("Välj vy"
#             , ("Visningsvy", "Redigeringsvy")
#             , horizontal=True
#             , label_visibility="collapsed")
            
# st.markdown("---")

# if vy == "Redigeringsvy":

#     val_redigering = st.radio("Välj ..."
#                             , ("Lägg till", "Redigera", "Ta bort")
#                             , horizontal=True
#                             , label_visibility="collapsed")
#     if val_redigering == "Lägg till":
#         st.write("---")
#         add_recommendation()
#     elif val_redigering == "Redigera":
#         st.write("---")
#         edit_recommendations()
#     elif val_redigering == "Ta bort":
#         st.write("---")
#         remove_recommendations()

# elif vy == "Visningsvy":
#     display_recommendations()
