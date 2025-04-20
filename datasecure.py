#develop a streamlit-based secure data storage and retrieval system by Hira Hanif


import streamlit as st
import hashlib
import json
import os
import time
from cryptography.fernet import fernet
from base64 import urlsafe_b64encode
from hashlib import pbkdf2_hmac

# === data information of user ===
DATA_FILE = "secure_data.json"
SALT = b"secure_salt_value"
LOCKOUT_DURATION = 60


# === SECTION LOGIN DEATAILS ===
if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = None

if "failed_attempts" not in st.session_state:
    st.session_state.failed_attempts = 0

if "lockout_time" not in st.session_state:
    st.session_state.lockout_time = 0

# === if data is load ===
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def generate_key(passkey):
    key = pbkdf2_hmac('sha256' , passkey.encode(), SALT, 100000)
    return urlsafe_b64encode(key)

def hash_password(password):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), SALT, 100000).hex()


# === cryptography.fernet used ===
def encrypt_text(text, key):
    cipher = fernet(generate_key(key))
    return cipher.encrypt(text.encode()).decode()

def decrypt_text(encrypt_text, key):
    try:
        cipher = fernet(generate_key(key))
        return cipher.decrypt(encrypt_text.encode()).decode()
    except:
        return None
    
stored_data = load_data()

# === navigation bar ===
st.title("secure data encryption system")
menu = ["home", "register", "login", "store data", "retrieve data"]
choice = st.sidebar.selectbox("navigation", menu)

if choice == "home":
    st.subheader("welcome to my data encryption system using streamlit")
    st.markdown("develop a streamlit-based secure data storage and retrieval system where: users store data with a unique passkey. users decrypt data by providing the correct passkey. multiple failed attempts result in a forced reauthorization (login page). the system operates entirely in memory without external databases.")

# === user registration ===
elif choice == "register":
    st.subheader("register new user")
    username = st.text_input("choose username")
    password = st.text_input("choose password", type="password")

    if st.button("register"):
        if username and password:
            if username in stored_data:
                st.warning("user already exists.")
            else:
                stored_data[username] = {
                    "password": hash_password(password),
                    "data": []
                }
                save_data(stored_data)
                st.success("user register successfully!")
        else:
            st.error("both fiels are required.")
            
    elif choice == "login":
        st.subheader("user login")

        if time.time() < st.session_state.lockout_time:
            remaining = int(st.session_state.lockout_time - time.time())
            st.error(f" too many failed attempts. please wait {remaining} seconds.")
            st.stop()
        
        usename = st.text_input("username")
        password = st.text_input("password", type="password")

        if st.button("login"):
            if username in stored_data and stored_data[username]["password"] == hash_passwor(password):
                st.session_state.authenticated_user = username
                st.session_state.failed_attempts = 0
                st.success(f" welcome {username}!")
            else:
                st.session_state.failed_attempts += 1
                remaining = 3 - st.session_state.failed_attempts
                st.error(f" individual credentials! attempts left: {remaining}")

                if st.session_state.failed_attempts >= 3:
                    st.session_state.lockout_time = time.time() + LOCKOUT_DURATION
                    st.error("to many failed attempts. locked for 60 seconds")
                    st.stop()

# === data score section ===
elif choice == "store data":
    if not st.session_state.authenticated_user:
        st.warning("please login first.")
    else:
        st.subheader("store encrypted data")
        data = st.text_area("enter data to encrypty")
        passkey = st.text_input("encryption key (passphrase)", type="password")

        if st.button("encrypt and save"):
            if data and passkey:
                encrypted = encrypt_text(data, passkey)
                stored_data[st.session_state.authenticated_user]["data"].append(encrypted)
                save_data(stored_data)
                st.success("data encrypted and save successfully!")

            else:
                st.error("all fields are required to fill.")

# === data retrieve data section ===
elif choice == "retrieve data":
    if not st.session_state.authenticated_user:
        st.warning("please login first")
    else:
        st.subheader("retrieve data")
        user_data = stored_data.get(st.session_state.authenticated_user, {}).get("data", [])

        if not user_data:
            st.info("no data found!")
        else:st.write("encrypted data enteries:")
        for i, item in enumerate(user_data):
            st.code(item,language="text")

        encrypted_input = st.text_area("enter encrypted text")
        passkey = st.text_input("enter passkey T decrypt", type="password")

        if st.button("drcrypt"):
            result = decrypt_text(encrypted_input, passkey)
            if result:
                st.success(f"decrypted : {result}")
            else:
                st.error("incorrect passkey or corrupted data.")