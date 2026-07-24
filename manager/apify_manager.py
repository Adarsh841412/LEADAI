# import os 
# from dotenv import load_dotenv 
# load_dotenv() 
# import requests 
# from config.settings import APIFY_TOKEN
# print(APIFY_TOKEN)

# class ApifyManager:
#     APIFY_BASE_URL='https://api.apify.com/v2/users/me/usage/monthly'
    
#     def __init__(self):
        
#         self.api_keys = self._load_keys() 
    
#     def _load_keys(self):
        
#         """
#         load apify api keys from setting.py 
#         """
#         keys = APIFY_TOKEN
#         return [
#             key.strip() for key in keys.split(',') if key.strip() 
#         ]
        
#     def _check_key(self,api_key:str)->dict | None 
        
        

# a1 = ApifyManager() 

# print(a1._load_keys())
