## GoalMasterApp v0.8.6

GoalMasterApp is an interactive application built with [Textual](https://textual.textualize.io/), designed to provide statistics, events, rankings, and predictions for major football (soccer) leagues. It uses the [api_football](https://rapidapi.com/api-sports/api/api-football) API to retrieve up-to-date match data and [gemini_ai](https://gemini.ai) to generate advanced match predictions.

## Features

- **League Standings**: View updated standings of major football leagues, including Serie A, Premier League, LaLiga, and others.
- **Match Statistics and Events**: View key match events such as goals, bookings, and substitutions, along with detailed statistics.
- **Match Predictions**: Generate match predictions with detailed team analysis, including win probabilities, double chance, and expected goals.
- **Injured Player Information**: View injured players for selected teams, with details on injury type.
- **Interactive Navigation**: Use keyboard commands and interactive menus to explore match information.
- **League Selection Menu**: Use the 'l' key to toggle the league selection menu for easy navigation.
- **Match Selection**: Choose between Match of the day, Match Shift, Standing, and Top Player statistics.

## Requirements

- Python 3.12+
- Python Libraries: 
  - `textual`
  - `gemini_ai`
  - `api_football`
  - `rich`
  - `weasyprint`
  - `mistune`

### Installation

1. Clone the repository:

```bash
git clone https://github.com/anidisc/goalmaster.git
cd goalmaster
```

2. Create a virtual environment and activate it:

```bash
python3.12 -m venv venv
source venv/bin/activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

### Configuration

To run the application, you'll need to configure the APIs:

1. **api_football**:
   - Get your API credentials from [api_football](https://rapidapi.com/api-sports/api/api-football) and configure them in your environment variables:
   ```bash
   export APIFOOTBALL_KEY="your_api_football_key"
   ```

2. **gemini_ai**:
   - Register your account on [Google Cloud](https://console.cloud.google.com/) and enable the Generative AI API.
   - Create a service account and download the JSON key file.
   - Configure the access token in your environment variables:
   ```bash
   export GOOGLE_API_KEY="your_google_api_key"
   ```

### Running the Application

To run the application, use the following command:

```bash
python3.12 goalmaster.py
```

## Screenshots

Here are some screenshots showcasing the main features of GoalMasterApp:

![League Selection](screenshots/league_selection.png)
_League selection menu showing available championships_

![Match Statistics](screenshots/match_statistics.png)
_Detailed match statistics and events_

![Injury Information](screenshots/injury_info.png)
_Injured players information for selected teams_

![Match Predictions](screenshots/match_predictions.png)
_Advanced match predictions with team analysis_

## Commands

The application offers a series of interactive commands that can be executed via the keyboard:

- `q`: Close the application
- `y`: Change the year of the selected football season
- `i`: Insert a manual command to view information about a league or match
- `l`: Toggle the league selection menu (show/hide)
- `j`: View player injuries for the selected match
- `r`: Remove the last displayed block
- `c`: Collapse all displayed sections
- `e`: Expand all displayed sections
- `s`: Show complete team statistics

### Example Usage

- To view the Serie A standings, enter the command `SERIEA -S`.
- To view live matches, enter `LIVE`.
- To view matches for a specific date, enter `SERIEA -T <days>`, where `<days>` is the number of days forward or backward from the current date.

### Usage Flow

1. Press `l` to open the league selection menu
2. Select a league from the list
3. Choose an action from the secondary menu (match of the day, standings, etc.)
4. Select a specific match when necessary
5. Use the special keys (`j`, `s`, etc.) to view additional information

### Predictions

GoalMasterApp offers advanced match predictions using AI. By analyzing statistics and team performance data, the app generates predictions for:

- **Match Result (1X2)**: Identifies the likely outcome of the match—win, draw, or loss.
- **Double Chance**: Provides predictions such as 1X, X2, or 12, where two outcomes are possible.
- **Goal Scoring**: Analyzes which teams are likely to score, if both teams will score (GG) or if one or both teams might not score (NG).
- **Scoring Probability**: Highlights the team with the highest probability of scoring (above 70%) and the team least likely to score (below 30%).

The predictions are based on the latest available match statistics, league standings, and home/away performances, offering users detailed insights for a better understanding of match results.

## What's New in Version 0.8.6

- **Injury Visualization**: Added the ability to view injured players for the selected match by pressing the `j` key.
- **Injury Data Update**: Improved the management of saving and updating injury data, using the current system date instead of the match date.
- **User Interface Improvement**: 
  - The `l` key now works as a toggle, showing and hiding the league selection menu.
  - Fixed issues with the display of interface components.
- **Advanced Event Management**: Improved logic for displaying match events, with an appropriate message when no events are available.

## Future Developments

In future versions, we plan to introduce:

- **Additional Data Visualizations**: Incorporate charts to visualize team performances, such as possession rates and shots on target.
- **Match Insights**: Provide more detailed analysis of player performances and potential match impacts, including injury reports.
- **Improved Predictions**: Refine the AI model for even more accurate predictions, integrating factors such as weather conditions and recent form.
- **Support for Other Leagues**: Expand the number of supported leagues and competitions, including international tournaments such as the FIFA World Cup and Copa Libertadores.
- **Mobile Compatibility**: Build a version of the app compatible with mobile devices for accessing data on the go.

## Development

To contribute to development:

1. Fork the project.
2. Create a new branch:

```bash
git checkout -b feature-new-functionality
```

3. Make your changes and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
