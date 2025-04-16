# Nuage

## Introduction

Nuage is a web application for managing video games. It allows users to browse, purchase, share, and comment on video games. Users can also manage their profiles, add friends, and track their achievements in games.

## Installation

To install and run the project locally, follow the steps below:

1. Clone the GitHub repository:
   ```bash
   git clone https://github.com/yacine20005/Nuage.git
   cd Projet-Nuage
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Configure the PostgreSQL database using the provided `dump-nuage-HAMADOUCHE-GAVAU--PELISSIER.sql` file:
   ```bash
   psql -U <your_user> -d <your_database> -f dump-nuage-HAMADOUCHE-GAVAU--PELISSIER.sql
   ```

4. Run the application:
   ```bash
   flask run
   ```

## Usage

Once the application is running, you can access the following features:

- **Boutique**: Browse and purchase video games.
- **Search**: Search for games by title, genre, developer, or publisher.
- **Profile**: Manage your profile, view your owned games, achievements, and friends.
- **Share**: Share games with your friends.
- **Comments**: Comment on games and read comments from other users.

### Detailed Explanations and Examples

#### Boutique

In the Boutique section, you can browse through a list of available games. Each game card displays the game's title, genre, price, and an image. You can sort the games by title, release date, average rating, or number of sales. To purchase a game, click on the "Buy" button on the game card.

#### Search

The Search feature allows you to find games by entering a search query and selecting a search type (title, genre, developer, or publisher). The search results will display a list of matching games with their details.

#### Profile

In the Profile section, you can view and manage your profile information, including your username, email, date of birth, and balance. You can also see a list of your owned games, games you have shared, your comments, and your friends. Additionally, you can add funds to your balance and add or remove friends.

#### Share

The Share feature allows you to share games with your friends. To share a game, go to the game's page and click on the "Share" button. Select a friend from the list and confirm the sharing.

#### Comments

In the Comments section, you can read comments from other users and leave your own comments on games you own. To leave a comment, go to the game's page, enter your comment and rating, and click "Submit".

For more details on each feature, refer to the source code and comments in the Python and HTML files.
