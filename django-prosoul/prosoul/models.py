# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2020 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
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
# Authors:
#   Alvaro del Castillo San Felix <acs@bitergia.com>
#   David Moreno <dmoreno@bitergia.com>
#
#

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_comma_separated_integer_list


class ProsoulModel(models.Model):
    """ Basic metadata for Prosoul objects """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    description = models.CharField(max_length=1024, default='', null=True, blank=True)

    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        abstract = True


class DataSourceType(ProsoulModel):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class MetricData(ProsoulModel):
    # Name of the metric in Elasticsearch with the data for the metric
    implementation = models.CharField(max_length=200, null=True, blank=True)
    # params to be used to compute the metric, including filters
    params = models.CharField(max_length=1024, null=True, blank=True)

    def __str__(self):
        metric_data_str = str(self.id)
        if self.implementation:
            metric_data_str += " " + self.implementation
        if self.params:
            metric_data_str += " " + self.params
        return metric_data_str


class Metric(ProsoulModel):
    name = models.CharField(max_length=200, unique=True)
    calculation_type = models.CharField(max_length=200, default='max')
    data = models.ForeignKey(MetricData, on_delete=models.CASCADE, null=True, blank=True)

    data_source_type = models.ForeignKey(DataSourceType,
                                         on_delete=models.CASCADE, null=True, blank=True)

    thresholds = models.CharField(max_length=200, default=None, null=True, blank=True,
                                  validators=[validate_comma_separated_integer_list])
    reverse_thresholds = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Factoid(ProsoulModel):
    name = models.CharField(max_length=200, unique=True)

    data_source_type = models.ForeignKey(DataSourceType,
                                         on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class Attribute(ProsoulModel):
    name = models.CharField(max_length=200, unique=True)
    # Relations
    metrics = models.ManyToManyField(Metric, blank=True)
    factoids = models.ManyToManyField(Factoid, blank=True)
    subattributes = models.ManyToManyField("Attribute", blank=True)

    def __str__(self):
        return self.name


class Goal(ProsoulModel):
    name = models.CharField(max_length=200, unique=True)
    # Relations
    attributes = models.ManyToManyField(Attribute)
    subgoals = models.ManyToManyField("Goal", blank=True)

    def __str__(self):
        return self.name


class QualityModel(ProsoulModel):
    """ Quality Model (maturity, Health ...)"""
    name = models.CharField(max_length=200, unique=True)
    # Relations
    goals = models.ManyToManyField("Goal")

    def __str__(self):
        return self.name
