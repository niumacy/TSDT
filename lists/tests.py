from django.test import TestCase
from django.urls import resolve
from lists.views import home_page
from django.http import HttpRequest
from django.template.loader import render_to_string
from lists.models import Item, List

class HomePageTest(TestCase):    
    def test_uses_home_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')
        
class ListViewTest(TestCase):
    def test_uses_list_template(self):
        response = self.client.get('/lists/the-new-page/')
        self.assertTemplateUsed(response, 'list.html')

    def test_displays_all_list_items(self):
        list_user = List.objects.create()
        Item.objects.create(text='itemey 1', list=list_user)
        Item.objects.create(text='itemey 2', list=list_user)
        
class NewListTest(TestCase):
    def test_can_save_a_POST_request(self):
        response = self.client.post('/lists/new', data={'item_text': 'A new list item'})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_redirects_after_POST(self):
        response = self.client.post('/lists/new', data={'item_text': 'A new list item'})
        self.assertRedirects(response, '/lists/the-new-page/')

class ListAndItemModelsTest(TestCase):
    def test_saving_and_retrieving_items(self):
        list_user = List()  # 创建 List 实例
        list_user.save()

        first_item = Item()
        first_item.text = 'The first list item'
        first_item.list = list_user  # 关联到 List
        first_item.save()

        second_item = Item()
        second_item.text = 'Item the second'
        second_item.list = list_user  # 关联到同一个 List
        second_item.save()

        saved_list = List.objects.first()  # 获取第一个 List
        self.assertEqual(saved_list, list_user)  # 验证 List 保存正确

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual(first_saved_item.text, 'The first list item')
        self.assertEqual(first_saved_item.list, list_user)  # 验证关联
        self.assertEqual(second_saved_item.text, 'Item the second')
        self.assertEqual(second_saved_item.list, list_user)  # 验证关联