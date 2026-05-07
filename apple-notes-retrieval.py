import requests
import sqlite3
import subprocess

# pull notes via AppleScript
script = '''
tell application "Notes"
    set output to ""
    repeat with n in notes of folder "Ideas"
        set output to output & name of n & "|||" & body of n & "###"
    end repeat
end tell
return output
'''

result = subprocess.check_output(["osascript", "-e", script]).decode()

for note in result.split("###"):
    if "|||" not in note:
        continue

    title, body = note.split("|||")

    # check SQLite if already processed
    # send to Home Assistant if new