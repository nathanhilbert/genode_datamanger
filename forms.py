# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2012 OpenPlans
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import os
import tempfile
import taggit

from django import forms
from django.utils import simplejson as json
from django.utils.translation import ugettext_lazy as _

from geonode.datamanager.models import DataConnection
from geonode.people.models import Profile 
from geonode.datamanager.enumerations import DATAUPDATE_FREQ
from geonode.datamanager.utils import getFormhubColumns


class DataConnectionCreateForm(forms.ModelForm):

    formhub_password = forms.CharField(widget=forms.PasswordInput(), required=True)

    class Meta:
        model = DataConnection
        exclude = ('owner', 'creation_date', 'lastedit_date', 'update_freq', 'lat_column','lon_column','layer_name','geocode_column', 'geocode_country')

class DataConnectionEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        dataconnection = kwargs.pop('dataconnection')
        super(DataConnectionEditForm, self).__init__(*args, **kwargs)
        #get the dataconnection
        CHOICES = getFormhubColumns(dataconnection)

        self.fields['lat_column'].choices = CHOICES
        self.fields['lon_column'].choices = CHOICES
        self.fields['geocode_column'].choices = CHOICES
        

    lat_column = forms.ChoiceField(choices=[])
    lon_column = forms.ChoiceField(choices=[])
    geocode_column = forms.ChoiceField(choices=[], required=False)

    update_freq = forms.ChoiceField(choices=DATAUPDATE_FREQ)


    class Meta:
        model = DataConnection
        exclude = ('owner', 'creation_date', 'lastedit_date','layer_name', 'formhub_url', 'formhub_username', 'formhub_password',)
