import streamlit as st
import preprocessor,helper
import re
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import matplotlib.dates as mdates
import seaborn as sns
from matplotlib.cm import get_cmap
from wordcloud import WordCloud




st.set_page_config(page_title="WhatsApp Chat Analyzer 📱", layout="wide")

# 🌟 Stylish Heading
st.markdown("""
    <h1 style='text-align: center; font-size: 60px; font-weight: bold; color: grey;'>
        📱 WhatsApp Chat Analyzer 📱
    </h1>
""", unsafe_allow_html=True)







st.sidebar.title('WhatsApp Chat Analyzer')
uploaded_file = st.sidebar.file_uploader("Choose a file", type="txt")

if uploaded_file is not None:
    # Read file as text
    bytes_data = uploaded_file.getvalue()
    raw_data = bytes_data.decode("utf-8")

    # Regex pattern to match date and time
    pattern = r'^(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2})[\s\u202f]*(AM|PM) - '

    converted_lines = []

    for line in raw_data.split('\n'):
        match = re.match(pattern, line)
        if match:
            date_str = match.group(1)
            time_str = f"{match.group(2)} {match.group(3)}"
            # Convert to datetime object
            datetime_obj = datetime.strptime(f"{date_str} {time_str}", "%m/%d/%y %I:%M %p")
            # Format to DD/MM/YYYY and 24-hr time
            formatted_date = datetime_obj.strftime("%d/%m/%Y")
            formatted_time = datetime_obj.strftime("%H:%M")
            # Replace in line
            new_line = re.sub(pattern, f'{formatted_date}, {formatted_time} - ', line)
            converted_lines.append(new_line)
        else:
            converted_lines.append(line)

    # Join converted lines into a single text
    converted_data = "\n".join(converted_lines)

    # Send to preprocessor
    df = preprocessor.preprocess(converted_data)

    # Show result
    #st.dataframe(df)

    #fetch  unique users
    user_list=df['user'].unique().tolist()
    user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0,'Overall')
    selected_user=st.sidebar.selectbox("Show analysis wrt",user_list)

    if st.sidebar.button("Show Analysis"):

        # Show result
        st.markdown("""
            <h2 style='color: darkred; font-size: 40px; font-weight: bold;'>
                💬 Messages Dataframe
            </h2>
        """, unsafe_allow_html=True)

        st.dataframe(df)


        #Stats Area
        num_messages,words,num_media_messages,num_links = helper.fetch_stats(selected_user,df)
        st.markdown("""
            <h2 style='color: darkred; font-size: 40px; font-weight: bold;'>
                🏆 Top Statistics
            </h2>
        """, unsafe_allow_html=True)

        col1,col2,col3,col4=st.columns(4)

        with col1:
            st.markdown("""
                <h3 style='font-size: 30px; color: goldenrod;'>
                    Total Messages
                </h3>
            """, unsafe_allow_html=True)

            st.title(num_messages)
        with col2:
            st.markdown("""
                <h3 style='font-size: 30px; color: goldenrod;'>
                    Total Words
                </h3>
            """, unsafe_allow_html=True)

            st.title(words)
        with col3:
            st.markdown("""
                <h3 style='font-size: 30px; color: goldenrod;'>
                    Media Shared
                </h3>
            """, unsafe_allow_html=True)

            st.title(num_media_messages)
        with col4:
            st.markdown("""
                <h3 style='font-size: 30px; color: goldenrod;'>
                    Links Shared
                </h3>
            """, unsafe_allow_html=True)

            st.title(num_links)








        #tmonthly timeline
        st.markdown("""
            <h2 style='color: darkred; font-size: 40px; font-weight: bold;'>
                📆 Monthly Timeline
            </h2>
        """, unsafe_allow_html=True)

        timeline = helper.monthly_timeline(selected_user, df)

        if not timeline.empty and 'time' in timeline.columns:
            fig, ax = plt.subplots(figsize=(10, 5))  # Wider figure for clarity

            ax.plot(timeline['time'], timeline['message'], label='Messages', color='purple', marker='o')

            ax.set_xticks(range(len(timeline['time'])))
            ax.set_xticklabels(timeline['time'], rotation=45, ha='right')  # Clean rotation

            ax.set_xlabel('Time')
            ax.set_ylabel('Number of Messages')
            ax.set_title('Monthly Chat Activity ', fontsize=14, color='darkblue')
            ax.legend(loc='upper left')
            ax.grid(True, linestyle='--', alpha=0.5)
            plt.tight_layout()

            st.pyplot(fig)
        else:
            st.warning("No data available for the selected user to generate a monthly timeline.")








        #Daily timeline
        st.markdown("""
            <h1 style='font-size: 40px; font-weight: bold; color: darkred;'>
                📅 Daily Timeline
            </h1>
        """, unsafe_allow_html=True)

        daily_timeline = helper.daily_timeline(selected_user, df)

        if not daily_timeline.empty and 'only_date' in daily_timeline.columns:
            # Convert only_date to datetime if not already
            daily_timeline['only_date'] = pd.to_datetime(daily_timeline['only_date'])

            fig, ax = plt.subplots(figsize=(12, 5))

            ax.plot(daily_timeline['only_date'], daily_timeline['message'],
                    label='Messages', color='goldenrod', marker='o', linestyle='-')

            # Format x-axis
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))

            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Number of Messages', fontsize=12)
            ax.set_title('Daily Chat Activity', fontsize=14, fontweight='bold', color='darkblue')
            ax.grid(True, linestyle='--', alpha=0.5)
            ax.legend(loc='upper left')

            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            st.pyplot(fig)
        else:
            st.warning("No data available to generate a daily timeline.")









        #activity map
        st.markdown("""
            <h1 style='font-size: 40px; font-weight: bold; color: darkred;'>
                🗺️ Activity Map
            </h1>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        # Most busy day
        with col1:
            st.markdown("""
                <h3 style='font-size: 30px; color: goldenrod;'>
                    Most Busy Day
                </h3>
            """, unsafe_allow_html=True)

            busy_day = helper.week_activity_map(selected_user, df)

            if not busy_day.empty:
                fig, ax = plt.subplots(figsize=(12, 5))
                ax.bar(busy_day.index, busy_day.values, color='purple')
                ax.set_xlabel('Day', fontsize=12)
                ax.set_ylabel('Activity', fontsize=12)
                ax.set_title('Most Busy Day Activity', fontsize=14, fontweight='bold', color='darkblue')
                ax.grid(True, linestyle='--', alpha=0.5)
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.warning("No data available to generate the most busy day.")

        # Most busy months
        with col2:
            st.markdown("""
                <h3 style='font-size: 30px; color: goldenrod;'>
                    Most Busy Months
                </h3>
            """, unsafe_allow_html=True)

            busy_month = helper.monthly_activity_map(selected_user, df)

            if not busy_month.empty:
                fig, ax = plt.subplots(figsize=(12, 5))
                ax.bar(busy_month.index, busy_month.values, color='purple')  # Set color to magenta
                ax.set_xlabel('Month', fontsize=12)
                ax.set_ylabel('Activity', fontsize=12)
                ax.set_title('Most Busy Month Activity', fontsize=14, fontweight='bold', color='darkblue')
                ax.grid(True, linestyle='--', alpha=0.5)
                plt.xticks(rotation='vertical')
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.warning("No data available to generate the most busy months.")





        # Activity Heatmap
        st.markdown("""
            <h1 style='font-size: 40px; color: darkred;'>
                📅 Weekly Activity Map
            </h1>
        """, unsafe_allow_html=True)

        user_heatmap = helper.activity_heatmap(selected_user, df)

        if user_heatmap is not None and not user_heatmap.empty:
            fig, ax = plt.subplots(figsize=(16, 6))  # Optional: Adjust size for better layout in Streamlit

            sns.heatmap(
                user_heatmap,
                cmap='Spectral',  # Vibrant, rainbow-like color palette
                linewidths=0.5,
                linecolor='white',
                annot=True,
                fmt=".0f",
                ax=ax
            )

            ax.set_title("Message Activity Heatmap", fontsize=16, fontweight='bold', color='darkblue')
            ax.set_xlabel("Time Period", fontsize=12)
            ax.set_ylabel("Day of Week", fontsize=12)
            ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
            plt.tight_layout()

            st.pyplot(fig)
        else:
            st.warning("No data available to display the weekly activity map.")

        # Finding the top busiest users in the group
        if selected_user == 'Overall':
            st.markdown("""
                <h1 style='font-size: 40px; color: darkred;'>
                    👥 Most Busy Users
                </h1>
            """, unsafe_allow_html=True)

            x, new_df = helper.most_busy_users(df)

            # Create equally sized columns
            col1, col2 = st.columns([1, 1])

            with col1:
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.bar(x.index, x.values, color='darkorange', label='Messages')
                ax.set_xlabel('Users', fontsize=12)
                ax.set_ylabel('Messages', fontsize=12)
                ax.set_title('Top Most Busy Users', fontsize=14, fontweight='bold', color='darkblue')
                ax.grid(True, linestyle='--', alpha=0.5)
                ax.legend(loc='upper right')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.dataframe(new_df, use_container_width=True)




        # WorldCloud
        st.markdown("""
            <h1 style='font-size: 40px; color: darkred;'>
                ☁️ WordCloud
            </h1>
        """, unsafe_allow_html=True)

        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        ax.axis("off")  # Optional: hides the axis ticks
        ax.set_title("Most Frequent Words", fontsize=16, fontweight='bold', color='darkblue')  # 🎯 Title added here
        st.pyplot(fig)






        # Most common words
        st.markdown("""
            <h1 style='font-size: 40px; color: darkred;'>
                🔤 Most Common Words
            </h1>
        """, unsafe_allow_html=True)

        most_common_df = helper.most_common_words(selected_user, df)

        if not most_common_df.empty:
            fig, ax = plt.subplots(figsize=(12, 6))

            words = most_common_df[0]
            counts = most_common_df[1]

            # Normalize counts for color mapping
            norm = plt.Normalize(min(counts), max(counts))
            cmap = get_cmap('twilight')  # You can also try: 'plasma', 'viridis', 'cool', 'Spectral'
            colors = cmap(norm(counts))

            bars = ax.barh(words, counts, color=colors)

            ax.set_xlabel("Frequency", fontsize=12)
            ax.set_ylabel("Words", fontsize=12)
            ax.set_title("Top Frequently Used Words", fontsize=14, fontweight='bold', color='darkblue')
            plt.gca().invert_yaxis()  # Show most frequent word on top
            plt.grid(axis='x', linestyle='--', alpha=0.5)

            # Create a colorbar as legend
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm, ax=ax)
            cbar.set_label('Word Frequency', fontsize=12)

            plt.tight_layout()
            st.pyplot(fig)

        else:
            st.warning("No common words found for this user.")









        # Emoji Analysis
        # Set font that supports emojis (for Windows)
        plt.rcParams['font.family'] = 'Segoe UI Emoji'
        st.markdown("""
            <h1 style='font-size: 40px; color: darkred;'>
                😄 Emoji Analysis
            </h1>
        """, unsafe_allow_html=True)

        emoji_df = helper.emoji_helper(selected_user, df)

        if not emoji_df.empty:
            # Rename columns for display
            emoji_df.columns = ['Emojis', 'Count']

            # Create equally sized columns
            col1, col2 = st.columns([1, 1])

            with col1:
                st.dataframe(emoji_df, use_container_width=True)

            with col2:
                fig, ax = plt.subplots(figsize=(5, 5))  # Adjust figure size
                # Plot a pie chart of top 10 emojis only (for readability)
                top_emojis = emoji_df.head(10)
                ax.pie(top_emojis['Count'], labels=top_emojis['Emojis'], autopct="%0.2f%%", startangle=90)
                ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

                # Add title to the pie chart with specific styling
                ax.set_title("Top Frequently Used Emojis", fontsize=14, fontweight='bold', color='darkblue')

                st.pyplot(fig)
        else:
            st.write("No emojis found for the selected user.")