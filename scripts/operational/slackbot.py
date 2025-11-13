"""
This script posts the latest visualisation of the forecast to the Bento lab Slack
"""

__author__      = "T.W. Alleman"
__copyright__   = "Copyright (c) 2025 by T.W. Alleman, IDD Group (JHUBSPH) & Bento Lab (Cornell CVM). All Rights Reserved."

import re
import os
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Used to find the right forecast
model_name = 'SIR-1S'
hyperparameters = 'exclude_None'

# Get the Slack bot token from GH secrets
CHANNEL_ID = "C07VD6H3Z1B".strip() # Bento Lab "#respiratory-diseases"
BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("SLACK_BOT_TOKEN not set in environment")

#################################
## Find latest forecast figure ##
#################################

def extract_timestamp(fname, pattern):
    match = pattern.search(fname.name)
    if match:
        return datetime.strptime(match.group(0)[:10], "%Y-%m-%d")
    return None

from pathlib import Path
forecast_folder = Path(os.path.join(os.path.dirname(__file__), f'../../data/interim/calibration/forecast/{model_name}/hyperparameters-{hyperparameters}/'))
pattern = re.compile(r"\d{4}-\d{2}-\d{2}-Cornell-JHU_hierarchSIR")                                     # regex to capture gathered timestamp
files_with_time = [(f, extract_timestamp(f, pattern)) for f in forecast_folder.glob("*.png")]          # collect files and their timestamps
files_with_time = [(f, t) for f, t in files_with_time if t is not None]
path_to_fig, reference_date = max(files_with_time, key=lambda x: x[1])                                           # get the latest file

#####################
## Upload to Slack ##
#####################

# helper function
def slack_post(path_to_fig, reference_date):
    """"
    Post the visualisation in the Bento Lab #respiratory-diseases Slack channel
    """
    
    # Initialize Slack client
    client = WebClient(token=BOT_TOKEN)

    try:
        # Upload the image to Slack
        response = client.files_upload_v2(
            channel=CHANNEL_ID,
            file=path_to_fig,
            filename=f"forecast_reference_date-{reference_date.strftime('%Y-%m-%d')}.png",
            title=f"CDC FluSight forecast for reference date {reference_date.strftime('%Y-%m-%d')}",
            initial_comment="This week's 4-week ahead influenza forecast."
        )
        print("File uploaded successfully:", response["file"]["permalink"])
    except SlackApiError as e:
        print("Error uploading file: {e.response['error']}")

    pass

# post
slack_post(path_to_fig, reference_date)