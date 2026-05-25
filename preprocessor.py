import re
import pandas as pd

MESSAGE_START_PATTERN = re.compile(
  r'^\s*\[?(?P<message_date>\d{1,2}/\d{1,2}/\d{2,4},\s*\d{1,2}:\d{2}(?::\d{2})?\s*(?:[AaPp]\.?[Mm]\.?)?)\]?\s*(?:-\s*)?(?P<user_message>.*)$'
)

def _parse_message_dates(message_dates):
  message_dates = (
      message_dates.astype(str)
      .str.replace(r'\s*-\s*$', '', regex=True)
      .str.replace('\u202f', ' ', regex=False)
      .str.replace('\xa0', ' ', regex=False)
      .str.replace(r'(?i)\s*a\.?m\.?$', ' AM', regex=True)
      .str.replace(r'(?i)\s*p\.?m\.?$', ' PM', regex=True)
      .str.strip()
  )

  parsed_dates = pd.Series(pd.NaT, index=message_dates.index, dtype='datetime64[ns]')
  date_formats = [
      '%d/%m/%y, %H:%M',
      '%d/%m/%Y, %H:%M',
      '%d/%m/%y, %H:%M:%S',
      '%d/%m/%Y, %H:%M:%S',
      '%d/%m/%y, %I:%M %p',
      '%d/%m/%Y, %I:%M %p',
      '%d/%m/%y, %I:%M:%S %p',
      '%d/%m/%Y, %I:%M:%S %p',
  ]

  for date_format in date_formats:
      missing_dates = parsed_dates.isna()
      if not missing_dates.any():
          break

      parsed_dates.loc[missing_dates] = pd.to_datetime(
          message_dates.loc[missing_dates],
          format=date_format,
          errors='coerce'
      )

  return parsed_dates

def preprocess(data):
  dates = []
  messages = []

  for line in data.splitlines():
      match = MESSAGE_START_PATTERN.match(line)

      if match:
          dates.append(match.group('message_date'))
          messages.append(match.group('user_message'))
      elif messages:
          messages[-1] = messages[-1] + ' ' + line.strip()

  df = pd.DataFrame({
      'message_date': dates,
      'user_message': messages
  })

  df['message_date'] = _parse_message_dates(df['message_date'])

  # 🔹 7. Convert to datetime
  df = df.dropna(subset=['message_date'])

  df.rename(columns={'message_date': 'date'}, inplace=True)

  df['user_message'] = df['user_message'].astype(str).str.replace('\n', ' ', regex=False)
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
