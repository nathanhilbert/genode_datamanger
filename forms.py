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


class DataConnectionForm(forms.ModelForm):

    collection_date_start = forms.DateField(widget=forms.TextInput(attrs={'class':'datepicker'}), input_formats=("%m/%d/%Y",))
    collection_date_end = forms.DateField(widget=forms.TextInput(attrs={'class':'datepicker'}), input_formats=("%m/%d/%Y",))

    keywords = taggit.forms.TagField(required=False,
                                     help_text=_("A space or comma-separated list of keywords"))
    class Meta:
        model = DataConnection
        exclude = ('uuid', 'owner', 'creation_date', 'lastedit_date')
