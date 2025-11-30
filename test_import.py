#!/usr/bin/env python
"""Test script for recipe import functionality"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodplanner.settings')
django.setup()

from hello.views import import_recipe
from django.test import RequestFactory
from django.http import QueryDict

def test_import():
    """Test the import functionality"""
    factory = RequestFactory()
    
    # Create a POST request with the test URL
    post_data = QueryDict('url=https://menunedeli.ru/recipe/kurinye-nozhki-v-duxovke-s-risom/')
    request = factory.post('/import-recipe/', post_data)
    
    # Call the import function
    response = import_recipe(request)
    
    # Print the result
    print("Import test result:")
    print(response.content.decode('utf-8'))

if __name__ == "__main__":
    test_import()