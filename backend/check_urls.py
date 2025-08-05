#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reader.settings')
django.setup()

from books.views import BookViewSet
from rest_framework.decorators import action
import inspect

print('=== BookViewSet Analysis ===')
print(f'BookViewSet class: {BookViewSet}')
print(f'BookViewSet MRO: {BookViewSet.__mro__}')

print('\n=== All attributes in BookViewSet ===')
for name in dir(BookViewSet):
    if not name.startswith('_'):
        attr = getattr(BookViewSet, name)
        print(f'{name}: {type(attr)}')
        if hasattr(attr, 'detail'):
            print(f'  -> detail: {attr.detail}')
        if hasattr(attr, 'methods'):
            print(f'  -> methods: {attr.methods}')

print('\n=== Checking content method specifically ===')
if hasattr(BookViewSet, 'content'):
    content_method = getattr(BookViewSet, 'content')
    print(f'Content method found: {content_method}')
    print(f'Type: {type(content_method)}')
    print(f'Has detail attr: {hasattr(content_method, "detail")}')
    print(f'Has methods attr: {hasattr(content_method, "methods")}')
    print(f'Has mapping attr: {hasattr(content_method, "mapping")}')
    
    # Check if it's decorated with @action
    if hasattr(content_method, 'detail'):
        print(f'Detail: {content_method.detail}')
    if hasattr(content_method, 'methods'):
        print(f'Methods: {content_method.methods}')
else:
    print('Content method NOT found!')

print('\n=== Router registration ===')
from books.urls import router
for prefix, viewset, basename in router.registry:
    print(f'{prefix} -> {viewset} (basename: {basename})')
    if viewset == BookViewSet:
        print('  BookViewSet is registered!')
        # Get the actual viewset instance
        viewset_instance = viewset()
        extra_actions = viewset_instance.get_extra_actions()
        print(f'  Extra actions: {[action.__name__ for action in extra_actions]}')