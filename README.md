# TG-bot-schedule

TG-bot-schedule is an open-source Telegram bot designed to provide accurate, simple, and reliable schedule management for educational institutions or organizations. The bot delivers up-to-date schedules, notifications, and interactive features to users directly in Telegram.

## Why This Project Exists

This project was created to offer a truly open-source solution for schedule management that is:
- Precise: The schedule does not change unexpectedly.
- Simple: Easy to use and configure.
- Reliable: Always delivers the correct information.

Many existing solutions are either closed, complex, and have a lot of unnecessary functionality, or often encounter errors with schedules (for example, due to parsing the schedule website). This bot aims to solve these problems.

## Configuration Options

- **Chat IDs:** You can specify which Telegram chat IDs receive notifications or interact with the bot (for using the bot in group chats).
- **Assets:** Customize images and other assets for your organization.

## Features & Highlights

- **Schedule:** Sends daily or weekly schedules to users.
- **Notifications:** Reminds users of upcoming events or changes.
- **Interactive Commands:** `/start`, `/help`, `/today`, and more.
- **Callback Handlers:** Interactive buttons for quick actions.
- **Custom Keyboards:** User-friendly navigation in chat.
- **Building Images:** Visual assets for locations.
- **Polls:** conducting polls within the specified group.

## Quick Start & Running the Application

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/dvrkns/TG-bot-schedule.git
   cd TG-bot-schedule
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure the Bot:**
   - Add the bot token and chat IDs to `src/utils/secrets.py`.
   - Configure images and other resources for your organization in assets/
   - Add your schedule using the template in src/data/schedule
   - Optionally, change the author name for the `/dev` command in the configuration.
4. **Run the Bot:**
   ```bash
   python bot.py
   ```

## Technology Stack

- **Python 3.11+**
- **python-telegram-bot** (Telegram Bot API framework)
- **apscheduler** (task scheduling)
- **JSON** for notifications and schedule data

## License

This project is licensed under the Apache License 2.0.

### What Does the License Mean?

- **Freedom to Use:** You can use, modify, and distribute the code for any purpose.
- **Attribution:** You must give appropriate credit to the original authors.
- **No Warranty:** The software is provided "as is" without warranty of any kind.
- **Contribution:** Contributions are welcome and will be licensed under Apache 2.0.

For more details, see the [LICENSE](https://www.apache.org/licenses/LICENSE-2.0) file.

---

Feel free to contribute, suggest features, or report issues!
