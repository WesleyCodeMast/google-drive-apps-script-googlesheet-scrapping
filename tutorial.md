https://developers.google.com/apps-script/api/reference/rest

https://developers.google.com/apps-script/add-ons/how-tos/building-workspace-addons

## create a  cron job  on Ubuntu( every 10 minutes) output the log in output.log file
*/10 * * * * /usr/bin/python3 /root/cron/upload_move_files_google_drive.py >> /root/cron/output.log 2>&1