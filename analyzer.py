from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain_community.tools import YouTubeSearchTool
from langchain_community.document_loaders import YoutubeLoader
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import requests
from bs4 import BeautifulSoup
import re
import ast
from api import openai_api_key

class YouTubeContentChecker:
    def __init__(self, query: str, num_videos: int = 10):
        self.query = query
        self.num_videos = num_videos
        self.openai_embed = OpenAIEmbeddings()
        self.llm = OpenAI(temperature=0)

    def get_urls(self):
        tool = YouTubeSearchTool()
        string_urls = tool.run(f"{self.query}, {self.num_videos}")
        return ast.literal_eval(string_urls)

    def calculate_similarity(self, title: str, content: str) -> float:
        """Calculate similarity between title and content"""
        try:
            title_embed = self.openai_embed.embed_query(title)
            content_embed = self.openai_embed.embed_query(content)
            similarity = cosine_similarity([title_embed], [content_embed])[0][0]
            return round(similarity * 100, 2)
        except Exception as e:
            print(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def get_youtube_title(self, url: str) -> str:
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.find('meta', property='og:title')
            if title:
                return title['content']
                
            title = soup.find('title')
            if title:
                return re.sub(r'\s*-\s*YouTube$', '', title.string)
                
            return None
            
        except Exception as e:
            print(f"Error getting title from {url}: {e}")
            return None
    
    def get_video_content(self, url: str) -> tuple:
        try:
            loader = YoutubeLoader.from_youtube_url(
                url,
                add_video_info=False,
                language=['en', 'ko']
            )
            
            content = loader.load()
            
            if not content or len(content) == 0:
                return None, None
                
            return content[0].page_content, content[0].metadata
            
        except Exception as e:
            print(f"Error loading content for {url}: {str(e)}")
            return None, None

    def parse_videos(self, urls: list) -> dict:
        video_dict = {}

        for url in urls:
            title = self.get_youtube_title(url)
            content, metadata = self.get_video_content(url)

            if content is None:
                print(f"Skipping {url} due to content loading error")
                continue

            video_dict[title] = {
                "content": content,
                "metadata": metadata,
                "url": url
            }
        return video_dict
        
    def analyze_videos(self) -> tuple:
        similarity_in_nums = []
        num_first_dict = {}

        urls = self.get_urls()
        title_first_dict = self.parse_videos(urls)

        for title, data in title_first_dict.items():
            content = data["content"]
            url = data["url"]
            
            # Use calculate_similarity instead of check_similarity
            similarity = self.calculate_similarity(title=title, content=content)
            similarity_in_nums.append(similarity)
            
            title_first_dict[title]["similarity"] = str(similarity)
            num_first_dict[str(similarity)] = {
                "title": title,
                "content": content,
                "url": url
            }
        
        similarity_scores = sorted(similarity_in_nums, reverse=True)
        return similarity_scores, num_first_dict

if __name__ == "__main__":
    import os

    os.environ["OPENAI_API_KEY"] = openai_api_key

    query = input("What are you searching for: ")
    query_nums = input("How many results?")
    
    # Create the checker instance with required query
    fact_checker = YouTubeContentChecker(query=query, num_videos=query_nums)
    
    # Use analyze_videos instead of check_similarity
    similarity_scores, num_first_dict = fact_checker.analyze_videos()

    # Print results
    for score in similarity_scores:
        title = num_first_dict[str(score)]["title"]
        url = num_first_dict[str(score)]["url"]
        print(f"Similarity: {score}% | Title: {title} | URL: {url}")




        
        


        

    
    


