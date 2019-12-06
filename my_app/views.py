# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
from requests.compat import quote_plus
from django.shortcuts import render
from bs4 import BeautifulSoup
from django.template.response import TemplateResponse
from . import models

BASE_CRAIGSLIST_URL = 'https://losangeles.craigslist.org/search/?query={}'
"""I have set location as LosAngeles because Craigs-List isn't working in India that much"""
BASE_IMAGE_URL = 'https://images.craigslist.org/{}_300x300.jpg'

# Create your views here.

def home(request):
    return render(request, 'base.html')


def new_search(request):
    search = request.POST.get("search")
    models.Search.objects.create(search=search)
    """We are using quote_plus for automating the task of putting '%20' in between strings 
    whenever there is any kind of spaces in query
    use this command to see how it works #print(quote_plus(search))"""

    final_url = BASE_CRAIGSLIST_URL.format(quote_plus(search))
    response = requests.get(final_url)
    data = response.text

    soup = BeautifulSoup(data, features='html.parser')
    post_listings = soup.find_all('li', {'class': 'result-row'})

    """post_title = soup.find_all('a', {'class': 'result-title'})
    post_title = post_listings[0].find(class_='result-title').text
    post_url = post_listings[0].find('a').get('href')
    post_price = post_listings[0].find(class_='result-price').text
    """
    final_postings = []

    for post in post_listings:
        post_title = post.find(class_='result-title').text
        post_url = post.find('a').get('href')
        if post.find(class_='result-price'):
            post_price = post.find(class_='result-price').text
        else:
            post_price = 'N/A'

        """It was hard to get Images from CraigsList because they didn't had 
        any specific class for assigning Images.
         But they did had one Item need Data-ids which could be used to scrap Images """

        if post.find(class_='result-image').get('data-ids'):
            post_image_id = post.find(class_='result-image').get('data-ids').split(',')[0].split(':')[1]
            final_image_url = BASE_IMAGE_URL.format(post_image_id)
        else:
            post_image_id = 'https://img.memecdn.com/error-404-boobies-not-found_c_1350377.jpg'
            final_image_url = post_image_id

        final_postings.append((post_title, post_url, post_price, final_image_url))
    """We have appended all the posts generated on CraigsLists"""

    stuff_for_frontend = {
        'search': search,
        'final_postings': final_postings,
    }
    return render(request, 'my_app/new_search.html', stuff_for_frontend)
