# Exercise Tracker

A beautiful, modern web application to track your daily exercises with SQLite database storage.

## Features

- 🏃‍♂️ **Track Multiple Exercise Types**: Running, cycling, swimming, weight training, yoga, and more
- 📊 **Statistics Dashboard**: View weekly and monthly workout summaries
- 💾 **Persistent Storage**: SQLite database stores all your exercise data
- 📱 **Responsive Design**: Works perfectly on desktop and mobile devices
- 🎨 **Modern UI**: Beautiful gradient design with smooth animations
- ⚡ **Real-time Updates**: Instant feedback and data updates

## Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and go to: `http://localhost:5000`

## Usage

### Adding Exercises
1. Select the date (defaults to today)
2. Choose your exercise type from the dropdown
3. Enter duration in minutes
4. Optionally add calories burned and notes
5. Click "Add Exercise"

### Viewing Statistics
The dashboard automatically shows:
- Number of workouts this week/month
- Total minutes exercised
- Total calories burned

### Exercise History
All your recent exercises are displayed in the right panel, showing:
- Exercise type and date
- Duration and calories
- Personal notes

## Database

The application uses SQLite database (`exercise_tracker.db`) which is automatically created when you first run the app. The database includes:

- **exercises** table with fields:
  - `id`: Unique identifier
  - `date`: Exercise date
  - `exercise_type`: Type of exercise
  - `duration`: Duration in minutes
  - `calories`: Calories burned (optional)
  - `notes`: Personal notes (optional)
  - `created_at`: Timestamp when record was created

## API Endpoints

- `GET /`: Main application page
- `POST /add_exercise`: Add a new exercise record
- `GET /get_exercises`: Retrieve all exercises
- `GET /get_stats`: Get weekly and monthly statistics

## Customization

You can easily customize the application by:

1. **Adding new exercise types**: Edit the `<select>` options in `templates/index.html`
2. **Modifying the color scheme**: Update the CSS gradient colors
3. **Adding new statistics**: Extend the `/get_stats` endpoint in `app.py`
4. **Database fields**: Modify the database schema in the `init_db()` function

## File Structure

```
exercise-tracker/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Main HTML template
└── exercise_tracker.db   # SQLite database (created automatically)
```

## Troubleshooting

**Port already in use**: If port 5000 is busy, modify the last line in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change port number
```

**Database issues**: Delete `exercise_tracker.db` to reset the database (you'll lose all data).

## Contributing

Feel free to fork this project and add new features like:
- Exercise categories and goals
- Data export functionality
- Charts and graphs
- User authentication
- Exercise reminders

Enjoy tracking your fitness journey! 💪
