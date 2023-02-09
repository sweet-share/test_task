This repo contains a solution of the first test task.


1. Image scraping. 

  Scraping is carried out by test_scraper.py. I have maneged to scrape 114 items to "download" folder, images were directly downloaded into two folders 
  (with person and without person). The scraper ignored pages without photos with persons (like this https://goo.su/KPZf) and successfully collected the right ones, 
  so I'd consider this task done. 
  
  Unfortunately, there were three pages with confused order of images (e.g. https://goo.su/0k0AoYW), so the images with persons were downloaded to folder without persons, and vice versa. 
  I couldn't distinguish those pictures by the means of HTML, and this issue needs solution which is not related to parsing (maybe some euristic or ML approach).
  
  Process: open main page, check how many pages with items there are, iterate through pages via AJAX-query, collect all individual pages of cloths, visit them and    download images. Had to use proxy, as the site has captcha protection against parsing.
  
 2. Image processing.
 
  Task is carried out in "Cloth processing.ipynb" Colab-notebook. I've just reversed the mask and applied it to the background to make it blue, that's it.
