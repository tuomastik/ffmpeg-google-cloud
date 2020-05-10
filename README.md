# FFmpeg on Google Cloud

This repository contains App Engine and Cloud Functions implementation of 
`webm` -> `mp4`/`gif` video conversion using FFmpeg.

## Usage

1. Download precompiled linux-64 `ffmpeg` binary from [ffbinaries.com](https://ffbinaries.com/downloads)
and place it with `ffmpeg` name in [`app_engine`](app_engine) or [`cloud_functions`](cloud_functions)
directory based on which of the services you want to deploy.

2. Prepare [Google Cloud SDK](https://cloud.google.com/sdk/) command-line tool

    2.1. Authenticate
    ```bash
    gcloud auth login
    ```
    2.2. Change to the correct project:
    ```bash
    gcloud config set project YOUR_PROJECT
    ```

3. Deploy the service

    3.1 App Engine
    ```bash
    cd app_engine
    gcloud app deploy --version=1 --quiet
    ```

    3.2 Cloud Functions
    
    List of all possible arguments: https://cloud.google.com/sdk/gcloud/reference/functions/deploy
    ```bash
    cd cloud_functions
    gcloud functions deploy YOUR_FUNCTION_NAME --runtime=python37 --entry-point=convert_webm --trigger-http --allow-unauthenticated --memory=512MB --timeout=540s
    ```

