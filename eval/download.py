r"""Functions to download semantic correspondence datasets"""
import tarfile
import os

import requests

from . import pfpascal
from . import pfwillow
from . import caltech
from . import spair
from . import cub2011


def load_dataset(benchmark, datapath, thres, device, split='test', augmentation=False, feature_size=16, sub_class = "all", item_index=-1):
    r"""Instantiates desired correspondence dataset"""
    correspondence_benchmark = {
        'pfpascal': pfpascal.PFPascalDataset,
        'pfwillow': pfwillow.PFWillowDataset,
        'caltech': caltech.CaltechDataset,
        'spair': spair.SPairDataset,
        'cubs': cub2011.CUBDataset,
    }

    dataset = correspondence_benchmark.get(benchmark)
    if dataset is None:
        raise Exception('Invalid benchmark dataset %s.' % benchmark)

    return dataset(benchmark=benchmark, datapath=datapath, thres=thres, device=device, split=split, augmentation=augmentation, feature_size=feature_size, sub_class=sub_class, item_index=item_index)


def download_from_google(token_id, filename):
    r"""Downloads desired filename from Google drive"""
    print('Downloading %s ...' % os.path.basename(filename))

    url = 'https://docs.google.com/uc?export=download'
    destination = filename + '.tar.gz'
    session = requests.Session()

    response = session.get(url, params={'id': token_id, 'confirm':'t'}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': token_id, 'confirm': token}
        response = session.get(url, params=params, stream=True)
    save_response_content(response, destination)
    file = tarfile.open(destination, 'r:gz')

    print("Extracting %s ..." % destination)
    file.extractall(filename)
    file.close()

    os.remove(destination)
    os.rename(filename, filename + '_tmp')
    os.rename(os.path.join(filename + '_tmp', os.path.basename(filename)), filename)
    os.rmdir(filename+'_tmp')


def get_confirm_token(response):
    r"""Retrieves confirm token"""
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None


def save_response_content(response, destination):
    r"""Saves the response to the destination"""
    chunk_size = 32768

    with open(destination, "wb") as file:
        for chunk in response.iter_content(chunk_size):
            if chunk:
                file.write(chunk)


def download_dataset(datapath, benchmark):
    r"""Downloads semantic correspondence benchmark dataset from Google drive"""
    if not os.path.isdir(datapath):
        os.mkdir(datapath)

    file_data = {
        'pfwillow': ('1tDP0y8RO5s45L-vqnortRaieiWENQco_', 'PF-WILLOW'),
        'pfpascal': ('1OOwpGzJnTsFXYh-YffMQ9XKM_Kl_zdzg', 'PF-PASCAL'),
        'caltech': ('1IV0E5sJ6xSdDyIvVSTdZjPHELMwGzsMn', 'Caltech-101'),
        'spair': ('1s73NVEFPro260H1tXxCh1ain7oApR8of', 'SPair-71k'),
        'cubs': (None, 'CUB_200_2011'),
    }

    file_id, filename = file_data[benchmark]
    abs_filepath = os.path.join(datapath, filename)

    if not os.path.isdir(abs_filepath):
        download_from_google(file_id, abs_filepath)
