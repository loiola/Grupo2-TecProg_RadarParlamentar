from django.core import serializers
import os

MODULE_DIR = os.getcwd() + '/exportadores/'

"""Deserializes political pary, legislative house, parliamentary, legislature, proposition,
voting and vote; And save the results."""


# Principal method: call other methods.
def main():
    deserialize_political_party()
    deserialize_legislative_house()
    deserialize_parliamentary()
    deserialize_legislature()
    deserialize_proposition()
    deserialize_voting()
    deserialize_vote()


def deserialize_political_party():

    # Receives the result of the XMLs serialization
    XMLSerializer = serializers.get_serializer("xml")

    # Receives the ​​XMLSerializer's variable values.
    xml_serializer = XMLSerializer()

    # Get values of serialization done by 'xml_serializer'.
    xml_serializer_data = xml_serializer.getvalue()

    for political_party in serializers.deserialize("xml", xml_serializer_data):
        political_party.save_data_in_file()


def deserialize_legislative_house():
    print("\nIsso aqui eh :" + MODULE_DIR + "\n")

    # Opening data in xml casa_legislativa.
    filepath = os.path.join(MODULE_DIR, 'dados/casa_legislativa.xml')
    out = open(filepath, "r")

    for legislative_house in serializers.deserialize("xml", out):
        legislative_house.save_data_in_file()


def deserialize_parliamentary():

    # Receives the result of the XMLs serialization
    XMLSerializer = serializers.get_serializer("xml")

    # Receives the ​​XMLSerializer's variable values.
    xml_serializer = XMLSerializer()

    # Get values of serialization done by 'xml_serializer'.
    xml_serializer_data = xml_serializer.getvalue()

    for parliamentary in serializers.deserialize("xml", xml_serializer_data):
        parliamentary.save_data_in_file()


def deserialize_legislature():

    # Receives the result of the XMLs serialization
    XMLSerializer = serializers.get_serializer("xml")

    # Receives the ​​XMLSerializer's variable values.
    xml_serializer = XMLSerializer()

    # Get values of serialization done by 'xml_serializer'.
    xml_serializer_data = xml_serializer.getvalue()

    for legislature in serializers.deserialize("xml", xml_serializer_data):
        legislature.save_data_in_file()


def deserialize_proposition():

    # Receives the result of the XMLs serialization
    XMLSerializer = serializers.get_serializer("xml")

    # Receives the ​​XMLSerializer's variable values.
    xml_serializer = XMLSerializer()

    # Get values of serialization done by 'xml_serializer'.
    xml_serializer_data = xml_serializer.getvalue()

    for proposition in serializers.deserialize("xml", xml_serializer_data):
        proposition.save_data_in_file()


def deserialize_voting():

    # Receives the result of the XMLs serialization
    XMLSerializer = serializers.get_serializer("xml")

    # Receives the ​​XMLSerializer's variable values.
    xml_serializer = XMLSerializer()

    # Get values of serialization done by 'xml_serializer'.
    xml_serializer_data = xml_serializer.getvalue()

    for voting in serializers.deserialize("xml", xml_serializer_data):
        voting.save_data_in_file()


def deserialize_vote():

    # Receives the result of the XMLs serialization
    XMLSerializer = serializers.get_serializer("xml")

    # Receives the ​​XMLSerializer's variable values.
    xml_serializer = XMLSerializer()

    # Get values of serialization done by 'xml_serializer'.
    xml_serializer_data = xml_serializer.getvalue()

    for vote in serializers.deserialize("xml", xml_serializer_data):
        vote.save_data_in_file()
