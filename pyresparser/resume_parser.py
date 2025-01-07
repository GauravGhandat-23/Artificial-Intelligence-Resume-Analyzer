import os
import multiprocessing as mp
import io
import spacy
import pprint
from spacy.matcher import Matcher
from . import utils


class ResumeParser(object):
    def __init__(self, resume, skills_file=None, custom_regex=None, nlp=None, custom_nlp=None, matcher=None):
        self.__skills_file = skills_file
        self.__custom_regex = custom_regex
        self.__matcher = matcher
        self.__resume = resume
        self.__details = {
            'name': None,
            'email': None,
            'mobile_number': None,
            'skills': None,
            'degree': None,
            'no_of_pages': None,
        }
        self.__text_raw = self.__extract_text()
        self.__text = ' '.join(self.__text_raw.split())
        self.__nlp = nlp(self.__text)
        self.__custom_nlp = custom_nlp(self.__text_raw)
        self.__noun_chunks = list(self.__nlp.noun_chunks)
        self.__get_basic_details()

    def __extract_text(self):
        ext = os.path.splitext(self.__resume)[1].split('.')[1] if not isinstance(self.__resume, io.BytesIO) else self.__resume.name.split('.')[1]
        return utils.extract_text(self.__resume, '.' + ext)

    def get_extracted_data(self):
        return self.__details

    def __get_basic_details(self):
        cust_ent = utils.extract_entities_wih_custom_model(self.__custom_nlp)
        name = utils.extract_name(self.__nlp, matcher=self.__matcher)
        email = utils.extract_email(self.__text)
        mobile = utils.extract_mobile_number(self.__text, self.__custom_regex)
        skills = utils.extract_skills(self.__nlp, self.__noun_chunks, self.__skills_file)
        entities = utils.extract_entity_sections_grad(self.__text_raw)

        # extract name
        self.__details['name'] = cust_ent.get('Name', [name])[0]

        # extract email
        self.__details['email'] = email

        # extract mobile number
        self.__details['mobile_number'] = mobile

        # extract skills
        self.__details['skills'] = skills

        # no of pages
        self.__details['no_of_pages'] = utils.get_number_of_pages(self.__resume)

        # extract education Degree
        self.__details['degree'] = cust_ent.get('Degree', None)


def resume_result_wrapper(resume, nlp, custom_nlp, matcher):
    parser = ResumeParser(resume, nlp=nlp, custom_nlp=custom_nlp, matcher=matcher)
    return parser.get_extracted_data()


def init_pool():
    # Load the spaCy models once and pass them to workers
    nlp = spacy.load('en_core_web_sm')
    custom_nlp = spacy.load(os.path.dirname(os.path.abspath(__file__)))
    matcher = Matcher(nlp.vocab)
    return nlp, custom_nlp, matcher


if __name__ == '__main__':
    # Initialize pool with shared resources (nlp, custom_nlp, matcher)
    nlp, custom_nlp, matcher = init_pool()

    resumes = []
    data = []
    for root, directories, filenames in os.walk('resumes'):
        for filename in filenames:
            file = os.path.join(root, filename)
            resumes.append(file)

    with mp.Pool(mp.cpu_count(), initializer=init_pool, initargs=()) as pool:
        results = pool.starmap(resume_result_wrapper, [(resume, nlp, custom_nlp, matcher) for resume in resumes])

    pprint.pprint(results)
