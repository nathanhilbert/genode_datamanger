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
from datetime import datetime
import os
import hashlib
from urlparse import urlparse

import httplib2
import urllib
import logging

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib.staticfiles.templatetags import staticfiles
from django.core.validators import RegexValidator
from django.core.urlresolvers import reverse

from geonode.base.enumerations import ALL_LANGUAGES, \
    HIERARCHY_LEVELS, UPDATE_FREQUENCIES, \
    DEFAULT_SUPPLEMENTAL_INFORMATION, LINK_TYPES
from geonode.utils import bbox_to_wkt
from geonode.people.models import Profile, Role
from geonode.security.models import PermissionLevelMixin
from geonode.datamanager.utils import createLayerFromCSV
from django.utils.timezone import utc


from taggit.managers import TaggableManager

logger = logging.getLogger("geonode.datamanger.models")


class DataConnection(models.Model, PermissionLevelMixin):

    owner = models.ForeignKey(User, blank=True, null=True)


    # section 1
    alphanumeric = RegexValidator(r'^[\w\-\s]*$', 'Only alphanumeric characters are allowed.')
    title = models.CharField(_('Data Connection Name'), max_length=255, help_text=_('Title of data connection or survey'), unique=True, validators=[alphanumeric])
    creation_date = models.DateTimeField(_('date'), auto_now_add=True, help_text=_('Time this connection was created')) # passing the method itself, not the result
    lastedit_date = models.DateTimeField(_('date'), auto_now_add=True, help_text=_('Last time this was edited')) 

    description_con = models.TextField(_('Description'), blank=True, help_text=_('Brief narrative summary of the content of the resource(s)'))

    formhub_url = models.URLField(_('Formhub URL'), help_text=_('This should be in the format of https://formhub.org/[user name]/forms/[survey name]'))
    formhub_username = models.CharField(_('Formhub username'), max_length=255, help_text=_('User name of of your formhub account'))
    formhub_password = models.CharField(_('Formhub Password'), max_length=255, help_text=_('Password of FormHub Account'))


    update_freq = models.CharField(_('Update Frequency'), max_length=255, help_text=_('Automatically pull in data from Formhub'))

    lat_column = models.CharField(_('Latitude Column'), max_length=255, help_text=_('Will always end with _latitude'))
    lon_column = models.CharField(_('Longitude Column'), max_length=255, help_text=_('Will always end with _longitude'))

    geocode_column = models.CharField(_('Geocode Column (Optional)'), blank=True, null=True,max_length=255, help_text=_('If latitude and longitude are not present, can use this field to attempt to geocode'))
    geocode_country = models.CharField(_('Geocode Country (Optional)'), blank=True, null=True, max_length=255, help_text=_('Please enter the country.  If it is worldwide, leave blank'))

    layer_name = models.CharField(_('Layer Name'), max_length=255)

    def refresh(self):
        new_layer = createLayerFromCSV(self)
        if new_layer:
            self.layer_name = new_layer.typename
            self.lastedit_date = datetime.now()
            self.save()
        return

    def getLayerURL(self):
        return reverse('layer_detail', args=(self.layer_name,))

