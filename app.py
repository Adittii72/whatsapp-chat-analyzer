import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt

st.sidebar.title("WhatsApp Chat Analysis")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
  bytes_data = uploaded_file.getvalue()
  data = bytes_data.decode("utf-8")
  df = preprocessor.preprocess(data)

  st.dataframe(df)

  users_list = df['user'].unique().tolist()
  users_list.remove('group_notification')
  users_list.sort()
  users_list.insert(0, "Overall")

  selected_user = st.sidebar.selectbox("Show analysis wrt", users_list)

  if st.sidebar.button("Show Analysis"):
    num_messages, words, num_media_messages, links = helper.fetch_stats(selected_user, df)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
      st.metric("Total Messages", num_messages)

    with col2:
      st.metric("Total Words", words)

    with col3:
      st.metric("Media Shared", num_media_messages)

    with col4:
      st.metric("Links Shared", links)


    if selected_user=='Overall':
      st.title("Most Busy Users")
      x, new_df= helper.most_busy_users(df)
      fig, ax = plt.subplots()
      col1, col2 = st.columns(2)

      with col1:
        ax.bar(x.index, x.values, color='burlywood')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

      with col2:
        st.dataframe(new_df)
    
    st.title("WordCloud")
    df_wc = helper.create_wordcloud(selected_user, df)
    fig, ax = plt.subplots()
    ax.imshow(df_wc)
    st.pyplot(fig)

    st.title("Most Common Words")
    most_common_df = helper.most_common_words(selected_user, df)
    fig, ax = plt.subplots()
    ax.barh(most_common_df[0], most_common_df[1], color='maroon')
    plt.xticks(rotation='vertical')
    st.pyplot(fig)

    
    emoji_df = helper.emoji_helper(selected_user, df)
    st.title("Emoji Analysis")

    col1, col2 = st.columns(2)

    with col1:
      st.dataframe(emoji_df)

    with col2:
      plt.rcParams['font.family'] = 'Segoe UI Emoji'
      fig, ax = plt.subplots()
      ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f")
      st.pyplot(fig)
    