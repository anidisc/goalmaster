## GoalMasterApp

GoalMasterApp is an interactive application built with [Textual](https://textual.textualize.io/), designed to provide statistics, events, standings, and predictions for major football leagues. It leverages the [api_football](https://rapidapi.com/api-sports/api/api-football) API to fetch up-to-date match data and [gemini_ai](https://gemini.ai) for generating advanced match predictions.

## Features

- **League Standings**: Displays current standings for major football leagues, including Serie A, Premier League, LaLiga, and more.
- **Match Statistics and Events**: View major match events such as goals, bookings, and substitutions, along with detailed match stats.
- **Match Predictions**: Generate match predictions with a detailed analysis of teams, including win probabilities, double chance, and expected goals.
- **Interactive Navigation**: Use keyboard commands and interactive menus to explore match information.

## Requirements

- Python 3.12+
- Python Libraries: 
  - `textual`
  - `gemini_ai`
  - `api_football`
  - `rich`

### Installation

1. Clone the repository:

````bash
git clone https://github.com/your-username/goal-master-app.git cd goal-master-app

2. Create a virtual environment and activate it:

```bash
python3.12 -m venv venv
source venv/bin/activate
````

1. Install the dependencies:

```bash
pip install -r requirements.txt
```

### Configuration

To run the application, you'll need to configure the APIs.

1. **api_football**:

- Get your API credentials from [api_football](https://rapidapi.com/api-sports/api/api-football) and configure them in the `api_football.py` file.

1. **gemini_ai**:

- Register your account at [gemini_ai](https://gemini.ai) and configure the access token in the `gemini_ai.py` file.

### Running the Application

To run the application, use the following command:

```bash
python3.12 goalmasterapp.py
```

## Commands

The application offers a series of interactive commands that can be executed via the keyboard:

- `q`: Quit the application.
- `y`: Change the year of the selected football season.
- `i`: Insert a manual command to display information about a league or match.
- `r`: Remove the last displayed block.
- `c`: Collapse or expand all displayed sections.

### Example Usage

- To display the Serie A standings, enter the command `SERIEA -S`.
- To display live matches, enter `LIVE`.
- To display matches for a specific date, enter `SERIEA -T <days>`, where `<days>` is the number of days forward or backward from the current date.

### Predictions

GoalMasterApp offers advanced match predictions using AI. By analyzing team statistics and performance data, the app generates predictions for:

- **Match Result (1X2)**: Identifies the likely match outcome—win, draw, or loss.
- **Double Chance**: Provides predictions such as 1X, X2, or 12, where two outcomes are possible.
- **Goal Scoring**: Analyzes which teams are likely to score, whether both teams will score (GG), or if one or both teams may not score (NG).
- **Scoring Probabilities**: Highlights the team with the highest probability of scoring (above 70%) and the team least likely to score (below 30%).

Predictions are based on the latest available match statistics, league standings, and home/away performance, offering users detailed insights for better understanding the game outcomes.

## Future Development

In future versions, we plan to introduce:

- **Additional Data Visualizations**: Incorporate charts and graphs to display team performance, such as possession rates and shots on target.
- **In-depth Match Insights**: Provide more detailed analysis of player performance and potential match impacts, including injury reports.
- **Enhanced Predictions**: Refine the AI model for even more accurate match predictions, integrating factors such as weather conditions and recent form.
- **Support for More Leagues**: Expand the number of leagues and competitions supported, including international tournaments like the FIFA World Cup and Copa Libertadores.
- **Mobile Compatibility**: Build a mobile-friendly version of the app to access data on the go.

## Development

To contribute to the development:

1. Fork the project.
2. Create a new branch:

```bash
git checkout -b feature-new-functionality
```

1. Make your changes and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
