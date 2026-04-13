# Library Reservation Bot

A Python-based automation bot that reserves library seats automatically at a specific time, eliminating the need for manual booking.
This project automates the process of reserving seats in my university library.

## 🚀 Features

* Automatic reservation at a specific time
* Fills in user details (email, student ID, etc.)
* Checks if reservation was successful
* Sends Telegram notification with result
* Supports multiple users and parallel reservations

## 🛠 Tech Stack

* Python
* Playwright
* Telegram Bot API

## ⚙️ How it works

The bot runs automatically at a scheduled time, opens the reservation website, fills in the required information, submits the form, and verifies the result.

## ⚠️ Notes

* Make sure your system is running and connected to the internet
* Do not share your credentials publicly

# Demo
![photo_2_2026-04-13_23-22-48](https://github.com/user-attachments/assets/10cdf93a-1941-4e0e-a5c7-458e6716fd80)
![photo_1_2026-04-13_23-22-48](https://github.com/user-attachments/assets/17258e37-3b95-4da4-a37f-32376cce25ad)

## 🧠 Problem

Reserving a seat in my university library required waking up early and booking exactly at a specific time, usually a few days in advance.

Since I usually wake up later, this became a daily frustration. Missing the reservation window meant no available seats for the day.

Instead of changing my routine, I decided to automate the process.

## ▶️ How to run

1. Clone the repository:
   git clone https://github.com/shayansan/library-reservation-bot.git

2. Go to the project folder:
   cd library-reservation-bot

3. Install dependencies:
   pip install -r requirements.txt

4. Create a `.env` file based on `.env.example`

5. Run the bot:
   python main.py
