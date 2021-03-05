from biosamples_v4.api import Client as BioSamplesClient
from biosamples_v4.aap import Client as AapClient
from biosamples_v4.encoders import SampleEncoder
from biosamples_v4.models import Sample


class BioSamples:
    def __init__(self, aap_client: AapClient, url):
        self.aap = aap_client
        self.biosamples = BioSamplesClient(url)
        self.encoder = SampleEncoder()

    def send_sample(self, sample: Sample):
        payload = self.encoder.default(sample)
        if sample.accession:
            return self.biosamples.update_sample(sample=payload, jwt=self.aap.get_token())
        return self.biosamples.persist_sample(sample=payload, jwt=self.aap.get_token())
