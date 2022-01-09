# dsc-final-project-epic-ml-visualizer

This project is for the final submission of the DSC lecture.

The app is built with streamlit and deployed on Microsoft Azure (for the time of the lecture).

After the lecture the docker-file as well as the deployment will be deleted.

## Run App locally

### First step: download model

Execute `download_models.sh` and download the pretrained model files from huggingface.

This app uses the model from https://huggingface.co/papluca/xlm-roberta-base-language-detection

### Second step: create venv

Create a virutal env and install the dependencies from `requirements.txt` file

### Start app

Then open the folder streamlit `streamlit` and run the command `streamlit run main.py`

or execute `docker-compose up` in root of this repo and start the container

## Which data is used?

The project uses data that was collected for the master thesis 'identifying epic moments in video games'.

The master thesis uses game data from *League of Legends* and chat data from *Twitch TV*.

This visualisation project shows the game and match data of 2 players.

For making the data public available here in this repository the used chat data has been encrypted - and will be deleted after the lecture.

## What is the idea behind?

The idea is a visualization part of the data and a small ML part.

The Visualization part should let the user choose a player, further a match and should show some visualizations of the match.

The ML part should predict the language of a chat message and/or a whole chat of a match.

## Description of the data

The data comes from 2 League of Legends Streamers of Twitch.

One is Noway4u_sir and the other is Tobiasfate.   
Noway4u_sir uses German language in his chat and tobiasfate uses English in his chat.

The data consists of 50 Matches (randomly picked from a bigger dataset) from both players with chat messages.

The data is managed in the directory dsc_data - all files in this directory are encrypted.

Each subfolder of this directory contains the data of the streamer/player.

These consist of a match_summary, match_participtant_summary and a match_timeline.

The match_summary contains all games of the player and the property participants describes which players fighted each other in a single match. 
Each row of match_summary describes one match. 
The final stats of the single participants are in the appropriate datafile from match_participant_summary. These can be joined by the matchId and the puuid of the player.

Every match has one match_timeline that contains data of all players, batched by 60_000 ms.
This timeline data shows especially when some event (like a kill or a death) happended in the game.

## Where did the data come from?

The data was logged for a master thesis and it was extracted from a bigger data set.

The 50 matches of two players/streamers are in the dsc_data directory. 

