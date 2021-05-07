# coding:utf-8

from django import forms
from django.forms import widgets  # 样式


class RegisterForms(forms.Form):
    username = forms.CharField(max_length=18, min_length=3, label='用户名',
                               error_messages={'required': '内容不能为空',
                                               'max_length': '用户名不能超过18个字符',
                                               'min_length': '用户名不能小于3个字符'},
                               widget=widgets.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(max_length=18, min_length=3, label='密码',
                               error_messages={'required': '内容不能为空',
                                               'max_length': '密码不能超过18个字符',
                                               'min_length': '密码不能小于3个字符'},
                               widget=widgets.PasswordInput(attrs={'class': 'form-control'}))
    re_password = forms.CharField(max_length=18, min_length=3, label='确认密码',
                                  error_messages={'required': '内容不能为空',
                                                  'max_length': '密码不能超过18个字符',
                                                  'min_length': '密码不能小于3个字符'},
                                  widget=widgets.PasswordInput(attrs={'class': 'form-control'}))

    email = forms.EmailField(label='邮箱', error_messages={'required': '内容不能为空',
                                                         'invalid': '不符合邮箱格式'},
                             widget=widgets.EmailInput(attrs={'class': 'form-control'}))

    # 局部钩子(用户名特殊字符)
    def clean_username(self):
        no_str = ['*', '/', '?', '#', '@', '&', '^']
        username = self.cleaned_data.get('username')
        for i in no_str:
            if i in username:
                raise forms.ValidationError(f'用户名中不能包含特殊符号{" ".join(no_str)}')
        else:
            return username

    # 全局钩子(密码一致性)
    def clean(self):
        password = self.cleaned_data.get('password')
        re_password = self.cleaned_data.get('re_password')
        if password == re_password:
            return self.cleaned_data
        else:
            raise forms.ValidationError('两次密码不一致')


# 修改密码校验
class PasswordForm(forms.Form):
    password = forms.CharField(max_length=18, min_length=3, label='密码',
                               error_messages={'required': '内容不能为空',
                                               'max_length': '密码不能超过18个字符',
                                               'min_length': '密码不能小于3个字符'},
                               widget=widgets.PasswordInput(attrs={'class': 'form-control'}))
    re_password = forms.CharField(max_length=18, min_length=3, label='确认密码',
                                  error_messages={'required': '内容不能为空',
                                                  'max_length': '密码不能超过18个字符',
                                                  'min_length': '密码不能小于3个字符'},
                                  widget=widgets.PasswordInput(attrs={'class': 'form-control'}))

    # 全局钩子(密码一致性)
    def clean(self):
        password = self.cleaned_data.get('password')
        re_password = self.cleaned_data.get('re_password')
        if password == re_password:
            return self.cleaned_data
        else:
            raise forms.ValidationError('两次密码不一致')
