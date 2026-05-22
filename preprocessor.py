import re
import pandas as pd

def preprocess(data):
  pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'

  messages = re.split(pattern, data)[1:]
  dates = re.findall(pattern, data)

  min_len = min(len(messages), len(dates))
  messages = messages[:min_len]
  dates = dates[:min_len]

  df = pd.DataFrame({
      'message_date': dates,
      'user_message': messages
  })

  df['message_date'] = df['message_date'].str.replace(' - ', '')

  # 🔹 7. Convert to datetime
  df['message_date'] = pd.to_datetime(
      df['message_date'],
      format='%d/%m/%y, %H:%M',
      errors='coerce'
  )

  df.rename(columns={'message_date': 'date'}, inplace=True)

  df['user_message'] = df['user_message'].str.replace('\n', ' ')
  df['user_message'] = df['user_message'].str.strip()

  users = []
  msgs = []

  for message in df['user_message']:
      entry = re.split(r'([\w\W]+?):\s', message)

      if entry[1:]:  # user exists
          users.append(entry[1])
          msgs.append(entry[2])
      else:
          users.append('group_notification')
          msgs.append(entry[0])

  df['user'] = users
  df['message'] = msgs

  df = df[['date', 'user', 'message']]
  df['only_date'] = df['date'].dt.date 
  df['year'] = df['date'].dt.year
  df['month_num'] = df['date'].dt.month
  df['month'] = df['date'].dt.month_name()
  df['day'] = df['date'].dt.day
  df['day_name'] = df['date'].dt.day_name()
  df['hour'] = df['date'].dt.hour
  df['minute'] = df['date'].dt.minute


  period = []
  for hour in df[['day_name', 'hour']]['hour']:
      if hour == 23:
          period.append(str(hour) + '-' + str('00'))
      elif hour == 0:
          period.append(str('00') + '-' + str(hour + 1))
      else:
          period.append(str(hour) + '-' + str(hour + 1))

  df['period'] = period

  return df