# Library Reservation Bot

This project automates the process of reserving seats in my university library.

## 🚀 Features

* Automatic reservation at a specific time
* Fills in user details (email, student ID, etc.)
* Checks if reservation was successful
* Sends Telegram notification with result

## 🛠 Tech Stack

* Python
* Playwright
* Telegram Bot API

## ⚙️ How it works

The bot runs automatically at a scheduled time, opens the reservation website, fills in the required information, submits the form, and verifies the result.

## ⚠️ Notes

* Make sure your system is running and connected to the internet
* Do not share your credentials publicly

## 📦 Setup

1. Clone the repository
2. Install dependencies:
   pip install -r requirements.txt
3. Add your credentials in `.env`
4. Run the bot:
   python main.py
