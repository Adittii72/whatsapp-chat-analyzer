import streamlit as st
import preprocessor, helper

st.sidebar.title("WhatsApp Chat Analysis")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
  bytes_data = uploaded_file.getvalue()
  data = bytes_data.decode("utf-8")
  # st.text(data)
  df = preprocessor.preprocess(data)

  st.dataframe(df)

  #fetch unique users
  users_list = df['user'].unique().tolist()
  users_list.remove('group_notification')
  users_list.sort()
  users_list.insert(0, "Overall")

  selected_user = st.sidebar.selectbox("Show analysis wrt", users_list)

  if st.sidebar.button("Show Analysis"):
    num_messages = helper.fetch_stats(selected_user, df)
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
      st.metric(label="Total Messages", int(num_messages))