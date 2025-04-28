# ADHD-Friendly Pomodoro Timer

A desktop Pomodoro timer application specifically designed to be ADHD-friendly, with customizable intervals, visual cues, and non-intrusive notifications.

## Features

- **High-contrast interface** for better focus and reduced visual strain
- **Flexible timer durations** with default and shorter interval options (15, 20, 25, 30 minutes)
- **Visual progress indicator** showing how much time remains in the current interval
- **Large, clear countdown timer** that's easy to read at a glance
- **Gentle transition warnings** before time is up (configurable)
- **Session tracking** to celebrate your accomplishments
- **Non-intrusive notifications** that don't break your focus
- **Toggleable sound alerts** for additional time awareness
- **Background operation** capability while you work

## ADHD-Friendly Design Elements

This timer was created with ADHD needs in mind:

- **Shorter work sessions** available (15-20 minutes) for when focus is difficult
- **Visual feedback** through color-coded modes (work/break) and progress bar
- **Forgiving controls** allowing easy pause, reset, and skip options
- **Warning notifications** to help with time blindness
- **Celebratory tracking** of completed sessions for motivation
- **Minimal distractions** in the interface design
- **High contrast** visual elements to maintain attention

## Installation

1. Ensure you have Python 3.8+ installed on your Windows system
2. Clone or download this repository
3. Navigate to the application directory
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python app.py
   ```

2. The timer starts in "Work Time" mode with the default duration (25 minutes)
3. Use the quick interval buttons to easily change work duration
4. Click "Start" to begin the timer
5. When a work session completes, the timer automatically switches to a break
6. After completing the configured number of work sessions, you'll get a longer break

### Timer Controls

- **Start/Resume**: Begins the timer or resumes from pause
- **Pause**: Temporarily stops the timer
- **Reset**: Resets the current interval to its beginning
- **Skip**: Moves to the next interval (e.g., from work to break)

### Customization Options

Click the Settings (⚙️) button to customize:

- Work session duration (1-60 minutes)
- Short break duration (1-30 minutes)
- Long break duration (5-60 minutes)
- Number of work cycles before a long break (1-10)
- Warning time before interval end (0-5 minutes)
- Enable/disable sound alerts
- Enable/disable desktop notifications

## Tips for ADHD Users

- Start with shorter work intervals (15-20 minutes) and gradually increase as comfort improves
- Take all scheduled breaks - they're essential for maintaining focus in subsequent sessions
- Use the completed sessions counter to celebrate your progress and build motivation
- Keep the timer visible on your screen to help with time awareness
- Consider pairing with other ADHD-friendly strategies like body doubling or the "body scan" technique

## License

This project is open source and available for personal and educational use.
