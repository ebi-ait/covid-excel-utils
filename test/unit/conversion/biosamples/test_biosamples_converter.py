from typing import List
import unittest

from biosamples_v4.models import Attribute
from submission.submission import Entity
from conversion.biosamples import BioSamplesConverter

class TestBioSamplesConverter(unittest.TestCase):
    def setUp(self):
        column_map = {
            'AC': {
                'attribute': 'geographic_location_latitude',
                'object': 'sample',
                'units': 'DD'
            },
            'AD': {
                'attribute': 'geographic_location_longitude',
                'object': 'sample',
                'units': 'DD'
            },
            'AH': {
                'attribute': 'host_age',
                'object': 'sample',
                'units': 'years'
            }
        }
        self.converter = BioSamplesConverter(column_map)

    def test_converter_adds_units_to_map(self):
        expected_unit_map = {
            'geographic_location_latitude': 'DD',
            'geographic_location_longitude': 'DD',
            'host_age': 'years',
        }
        self.assertDictEqual(expected_unit_map, self.converter.unit_map)

    def test_converter_adds_units_to_sample(self):
        attributes = {
            'sample_title': 'Oro-Nasopharyngeal swab',
            'tax_id': '2697049',
            'scientific_name': 'Severe acute respiratory syndrome coronavirus 2',
            'geographic_location_latitude': '53.1424',
            'geographic_location_longitude': '7.6921',
            'host_age': '81 - 90'
        }
        expected_attributes = [
            Attribute(name='organism', value=attributes['scientific_name'], iris="http://purl.obolibrary.org/obo/NCBITaxon_2697049"),
            Attribute(name='geographic location latitude', value='53.1424', unit='DD'),
            Attribute(name='geographic location longitude', value='7.6921', unit='DD'),
            Attribute(name='host age', value='81 - 90', unit='years')
        ]
        entity = Entity('sample', 'sample1', attributes)
        sample = self.converter.convert_sample(entity)
        
        self.assertEqual(attributes['sample_title'], sample.name)
        self.assertEqual(attributes['tax_id'], sample.ncbi_taxon_id)
        self.assertEqual(attributes['scientific_name'], sample.species)
        self.assertAttributesEqual(expected_attributes, sample.attributes)
    
    def assertAttributesEqual(self, expected: List[Attribute], actual: List[Attribute]):
        self.assertEqual(len(expected), len(actual))
        for index in range(0, len(expected)):
            self.assertAttributeEqual(expected[index], actual[index])
    
    def assertAttributeEqual(self, expected: Attribute, actual: Attribute):
        self.assertEqual(expected.name, actual.name)
        self.assertEqual(expected.value, actual.value)
        self.assertEqual(expected.unit, actual.unit)
        self.assertListEqual(expected.iris, actual.iris)
