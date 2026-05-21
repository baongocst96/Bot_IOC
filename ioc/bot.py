import requests
import pandas as pd
import json
import re

from datetime import datetime
from datetime import date

# =====================
# CONFIG
# =====================

BOT_TOKEN = "8972081279:AAFmTyEoknmAabTq61srZ83oj_xEQFeMVyU"
CHAT_ID = "669294645"

SHEET_ID = "1tCIjG_GLb7qAcmAtsOTCLpe6cYXajkSvRUw_TJvF3jk"

# gid sheet
GID = "1092247411"

# =====================
# READ GOOGLE SHEET
# =====================

url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json&gid={GID}"

response = requests.get(url)

# Google trả text không phải json chuẩn
content = response.text

# cắt phần json
json_data = re.search(r"google.visualization.Query.setResponse\((.*)\);", content, re.S).group(1)

data = json.loads(json_data)

# =====================
# PARSE DATA
# =====================

cols = [
    col.get("label", "")
    for col in data["table"]["cols"]
]

rows = []

for row in data["table"]["rows"]:

    values = []

    for cell in row["c"]:

        if cell is None:
            values.append("")
        else:
            values.append(cell.get("v", ""))

    rows.append(values)

df = pd.DataFrame(rows, columns=cols)

# =====================
# CHECK TASK
# =====================

today = datetime.today().date()

messages = []

for index, row in df.iterrows():

    try:

        due = str(row["Due"]).strip()

        status = str(row["Trạng thái"]).strip()

        linh_vuc = str(row["Lĩnh vực"]).strip()

        muc_tieu = str(row["Mục tiêu"]).strip()

        if due == "":
            continue

        match = re.search(r"Date\((\d+),(\d+),(\d+)\)", due)

        if match:

            year = int(match.group(1))

            month = int(match.group(2)) + 1

            day = int(match.group(3))

            due_date = date(year, month, day)

        else:

            due_date = pd.to_datetime(
                due,
                dayfirst=True
            ).date()

        days_left = (due_date - today).days

        if 0 <= days_left <= 3:

            if status.lower() != "hoàn thành":

                msg = f"""
⚠️ Sắp đến hạn công việc

📌 Lĩnh vực: {linh_vuc}

📝 Mục tiêu:
{muc_tieu}

📅 Due: {due_date.strftime('%d/%m/%Y')}

⏳ Còn {days_left} ngày
"""

                messages.append(msg)

    except Exception as e:
        print("Lỗi dòng:", e)

# =====================
# SEND TELEGRAM
# =====================

for msg in messages:

    send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    requests.post(send_url, data=payload)

print("Done")