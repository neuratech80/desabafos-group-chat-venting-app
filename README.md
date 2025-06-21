
Built by https://www.blackbox.ai

---

# Desabafos: A Group Chat and Venting Application

Desabafos is a web application built using Flask, providing users with a platform to vent their thoughts and feelings in a supportive environment through posts and group chat functionalities. The application allows users to create groups, send messages, like posts/messages, and add comments seamlessly.

## Project Overview

Desabafos combines elements of social networking with the ability for users to express themselves anonymously. Users can create groups for chatting, send messages, like posts, and react to each other's contributions, all in real time thanks to the integration of Socket.IO.

## Installation

To install and run Desabafos, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/desabafos.git
   cd desabafos
   ```

2. **Set up a Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   Make sure you have the required packages by installing them via pip.
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database**:
   You can set up the database using the provided script.
   ```bash
   python init_db.py
   ```

5. **Run the Application**:
   Start the Flask application.
   ```bash
   python app.py
   ```

## Usage

- Navigate to `http://localhost:8000` in your web browser to access the application.
- You can create posts, which can include text and images.
- Join or create groups to chat with other users in real time.
- Like posts and messages to express your appreciation and support.

## Features

- **Real-time chat:** Users can join specific groups and exchange messages instantly.
- **Posts and Comments:** Users can create posts and comment on them, facilitating discussions.
- **Likes:** Users can like posts and messages, with real-time updates reflecting the current count.
- **Image Uploads:** Users can also upload images with their posts and messages.
- **Anonymous User Registration:** Users can interact without registering, using a generated username.

## Dependencies

This application requires the following Python packages:

- Flask
- Flask-SQLAlchemy
- Flask-SocketIO
- Werkzeug

Ensure you have these in your `requirements.txt` to install all dependencies upfront.

## Project Structure

The project is organized into the following structure:

```
desabafos/
│
├── app.py              # Main application file
├── models.py           # Database models and relationships
├── extensions.py       # Extensions for Flask
├── init_db.py          # Database initialization script
└── requirements.txt     # Python package dependencies
```

### Database Models

The application defines several models that correspond to the database tables:

- `Group`: Represents a chat group where messages can be sent.
- `GroupMessage`: Represents messages sent in a chat group.
- `GroupMessageLike`: Records likes for messages in groups.
- `Post`: Represents user posts on the main feed.
- `Comment`: Represents comments made on posts.
- `UserLike`: Records likes for user posts.

For more details about models and their relationships, refer to `models.py`.

---

Feel free to contribute by submitting issues or pull requests. Happy venting!