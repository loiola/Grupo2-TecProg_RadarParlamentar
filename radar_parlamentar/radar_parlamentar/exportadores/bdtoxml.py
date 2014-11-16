# !/usr/bin/python
# coding=utf8

# setup the environment
import os
import sys
sys.path.append(os.pardir)
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"


class XMLWriter:

    """ Helper class to write out an xml file."""

    def __init__(self, pretty=True):
        """ Set pretty to True if you want an indented XML file."""

        self.output = ""
        self.stack = []
        self.pretty = pretty

    def add_and_open_tag(self, tag):
        """ Add an open tag."""

        self.stack.append(tag)

        if self.pretty:
            self.output += "  " * (len(self.stack) - 1)
        else:
            self.output += "<" + tag + ">"

        if self.pretty:
            self.output += "\n"

    def close_tag(self):
        """ Close the innermost tag."""

        if self.pretty:
            self.output += "\n" + "  " * (len(self.stack) - 1)

        tag = self.stack.pop()

        self.output += "</" + tag + ">"

        if self.pretty:
            self.output += "\n"

    def close_all_tags(self):
        """ Close all open tags."""

        while len(self.stack) > 0:
            self.close_tag()

    def add_content(self, text):
        """ Add some content."""

        if self.pretty:
            self.output += "  " * len(self.stack)
        else:
            self.output += str(text)

    def save_data_in_file(self, filename):
        """ Save the data to a file."""

        self.close_all_tags()
        fileOpen = open(filename, "w")
        fileOpen.write(self.output)
        fileOpen.close_tag()

import django.db.models

writer = XMLWriter(pretty=False)
writer.add_and_open_tag("djangoexport")
models = django.db.models.get_models()

for model in models:
    # model._meta.object_name holds the name of the model
    writer.add_and_open_tag(model._meta.object_name + "s")

    for item in model.objects.all():
        writer.add_and_open_tag(model._meta.object_name)

        for field in item._meta.fields:
            writer.add_and_open_tag(field.name)
            value = getattr(item, field.name)

            if value is not None:

                if isinstance(value, django.db.models.base.Model):
                    
                    # This field is a foreign key, so save the primary key
                    # of the referring object.
                    pk_name = value._meta.pk.name
                    pk_value = getattr(value, pk_name)
                    writer.add_content(pk_value)

                else:
                    writer.add_content(value)
            writer.close_tag()
        writer.close_tag()
    writer.close_tag()
writer.close_tag()
writer.save_data_in_file("export.xml")
