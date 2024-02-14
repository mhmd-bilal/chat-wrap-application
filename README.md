# ChatWrap - A web application

This project is a Flask web application designed to analyze WhatsApp chat history files and store the results in a database. It utilizes MongoDB for data storage and provides various analytics features such as sentiment analysis, word frequency analysis, and message count statistics.

## Features

- **User-friendly Interface**: The web app offers a user-friendly interface for uploading WhatsApp chat history files and selecting analysis options.
- **Sentiment Analysis**: Analyzes the sentiment of messages using the TextBlob library, providing insights into the overall sentiment of conversations.
- **Word Frequency Analysis**: Identifies the most common words used by each user in the chat, helping to understand key topics of discussion.
- **Message Count Statistics**: Calculates the total number of messages sent by each user and visualizes message distribution per day of the week.
- **Winner Determination**: Determines the winner of the chat based on the maximum number of messages sent by either participant.

## Setup

1. Clone the repository to your local machine.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Ensure MongoDB is installed and running on your system.
4. Modify the Flask app configuration in `app.py` to connect to your MongoDB instance.
5. Run the Flask application using `python app.py`.
6. Access the web app in your browser at `http://localhost:5000`.

## Usage

1. Upload your WhatsApp chat history file using the provided interface.
2. Select the appropriate options for theme and participant names.
3. Confirm the selections to initiate the analysis process.
4. View the analysis results on the generated page, including message statistics, sentiment analysis, and word frequency.


