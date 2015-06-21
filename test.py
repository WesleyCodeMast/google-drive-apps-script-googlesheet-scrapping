from google.oauth2 import service_account
import google.auth.transport.requests
from googleapiclient.discovery import build
import sys
import random
import csv
import io
import requests
from google.auth.transport.requests import AuthorizedSession
import os
from google.oauth2.credentials import Credentials
import app_script

credentials = service_account.Credentials.from_service_account_file('credential.json')

service = build('drive', 'v3', credentials=credentials)

