from django import forms

from django import forms

import PayFun.models

MAX_UPLOAD_SIZE = 2500000

class LaunchFrom(forms.ModelForm):
    class Meta:
        model = Activity

    def clean_content(self):
        content = self.cleaned_data['content']
        if not content:
            raise forms.ValidationError("You have to specify the activity.")
        return content 

    def clean_title(self):
        title = self.cleaned_data['title']
        if not title:
            raise forms.ValidationError("You have to name the activity.")
        return title

    def clean_brief_description(self):
        brief_description = self.cleaned_data['brief_description']
        if not brief_description:
            raise forms.ValidationError("You have to briefly describe the activity.")
        return brief_description

    def clean_target_money(self):
        target_money = self.cleaned_data['target_money']
        if not target_money:
            raise forms.ValidationError("You have to input the amount of money you need.")
        return target_money

    def clean_start_time(self):
        target_money = self.cleaned_data['start_time']
        if not start_time:
            raise forms.ValidationError("You have to specify the start time of the activity.")
        return start_time

    def clean_end_time(self):
        end_time = self.cleaned_data['end_time']
        if not end_time:
            raise forms.ValidationError("You have to specify the end time of the activity.")
        return end_time

    def clean_location(self);
        location = self.cleaned_data['location']
        if not location:
            raise forms.ValidationError("You have to specify the location of the activity.")
        return location



