import streamlit as st
from analyzer import YouTubeContentChecker
import os
from dotenv import load_dotenv
load_dotenv()


def main():
    st.title("YouTube Content Checker")
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


    # Input section - simple text boxes and button
    query = st.text_input("Search Query:")
    num_videos = st.number_input("Number of Videos:", min_value=1, max_value=20, value=5)
    
    if st.button("Analyze"):
        if query:  # Only proceed if query is not empty
            try:
                with st.spinner('Analyzing videos...'):
                    # Initialize and run analyzer
                    checker = YouTubeContentChecker(query=query, num_videos=num_videos)
                    similarity_scores, results_dict = checker.analyze_videos()

                    # Display results in YouTube-like format
                    for score in similarity_scores:
                        video_data = results_dict[str(score)]
                        
                        # Create a box for each video
                        st.markdown("""---""")  # Separator
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            # Video title as a link
                            st.markdown(f"### [{video_data['title']}]({video_data['url']})")
                            # Show first 200 characters of content
                            st.text(video_data['content'][:200] + "...")
                        
                        with col2:
                            # Display similarity score prominently
                            st.markdown(f"### Similarity Score: {score}%")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter a search query")

if __name__ == "__main__":
    main()