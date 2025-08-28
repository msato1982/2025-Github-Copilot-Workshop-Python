import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from deliverManager import Event, EventArgs, KitchenObjectSO

def test_event_add_and_invoke():
    event = Event()
    called = {}
    def handler(sender, args):
        called['flag'] = True
    event.add_handler(handler)
    event.invoke(None)
    assert called.get('flag') is True

def test_event_remove_handler():
    event = Event()
    called = {}
    def handler(sender, args):
        called['flag'] = True
    event.add_handler(handler)
    event.remove_handler(handler)
    event.invoke(None)
    assert called.get('flag') is None

def test_kitchen_object_so():
    obj = KitchenObjectSO(name='Apple', object_id=1)
    assert obj.name == 'Apple'
    assert obj.object_id == 1
