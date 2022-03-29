import pytest
import os.path
import requests

# For run tests u need directory 'test_files' with files
FILE_PATH_DIR = os.path.abspath('test_files')


class MainParameters:
    """
    Class contains main parameters
    """
    URL = 'http://127.0.0.1:5000/'
    HTML_PAGE = '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
        <input type=file name=file>
        <input type=submit value=Upload>
    </form>
    '''
    class_url = URL + 'classification'
    score_url = URL + 'scores'
    images_url = URL + 'images'


class TestServiceScores(MainParameters):
    """
    Class for testing 'scores'.  Some tests failed because flask-service need
    more catching unusual values in parameters.
    """

    def test_scores_get_good_name(self):
        # Prepare data
        files = {'file': open(FILE_PATH_DIR + '/Buffy_dog.jpeg', 'rb')}
        response_class = requests.post(self.class_url, files=files)

        # Main part
        response_scores = requests.get(self.score_url + '/Buffy_dog.jpeg')
        assert response_scores.status_code == 200
        assert 'image' in response_scores.text
        assert 'score' in response_scores.text
        assert response_scores.json()['image'] == 'Buffy_dog.jpeg'

        # Clean data
        response_clean = requests.delete(self.score_url + '/Buffy_dog.jpeg')
        response_clean = requests.delete(self.images_url + '/Buffy_dog.jpeg')

    def test_scores_get_bad_name(self):
        # Main part
        response_scores = requests.get(self.score_url + '/Buffy_dog.jpeg')
        assert response_scores.status_code == 200
        assert 'score' in response_scores.text
        assert response_scores.json()['score'] == 'Score not found'

    def test_scores_get_empty_name(self):
        # Main part
        response_scores = requests.get(self.score_url + '/')
        assert response_scores.status_code == 404

    def test_scores_delete_score_image(self):
        # Prepare data
        files = {'file': open(FILE_PATH_DIR + '/Buffy_dog.jpeg', 'rb')}
        response_class = requests.post(self.class_url, files=files)

        # Main part
        response_score = requests.delete(self.score_url + '/Buffy_dog.jpeg')
        assert response_score.status_code == 200
        assert 'image' in response_score.text
        assert 'score' in response_score.text
        assert response_score.json()['image'] == 'Buffy_dog.jpeg'
        assert response_score.json()['score'] == 'Score was deleted'
        response_score = requests.get(self.score_url + '/Buffy_dog.jpeg')
        assert response_score.status_code == 200
        assert 'score' in response_score.text
        assert response_score.json()['score'] == 'Score not found'

        # Clean data
        response_clean = requests.delete(self.images_url + '/Buffy_dog.jpeg')

    def test_scores_delete_bad_name(self):
        # Main part
        response_scores = requests.delete(self.score_url + '/Buffy_dog.jpeg')
        assert response_scores.status_code == 200
        assert 'image' in response_scores.text
        assert 'score' in response_scores.text
        assert response_scores.json()['image'] == 'Buffy_dog.jpeg'
        assert response_scores.json()['score'] == 'Score not found'

    def test_scores_delete_empty_name(self):
        # Main part
        response_scores = requests.delete(self.score_url + '/Buffy_dog.jpeg')
        assert 'score' in response_scores.text
        assert response_scores.json()['score'] == 'Score not found'
        assert response_scores.status_code == 200


class TestServiceImages(MainParameters):
    """
    Class for testing 'images'. Some tests failed because flask-service need
    more catching unusual values in parameters.
    """

    def test_images_good_name(self):
        # Prepare data
        files = {'file': open(FILE_PATH_DIR + '/Buffy_dog.jpeg', 'rb')}
        response_class = requests.post(self.class_url, files=files)

        # Main part
        response_image = requests.get(self.images_url + '/Buffy_dog.jpeg')
        assert response_image.status_code == 200

        # Clean data
        response_clean = requests.delete(self.score_url + '/Buffy_dog.jpeg')
        response_clean = requests.delete(self.images_url + '/Buffy_dog.jpeg')

    def test_images_bad_name(self):
        # Main part
        response_image = requests.get(self.images_url + '/Buffy_dog.jpeg')
        assert response_image.status_code == 404

    def test_images_empty_name(self):
        # Main part
        response_image = requests.get(self.images_url + '/')
        assert response_image.status_code == 404

    def test_images_delete_image(self):
        # Prepare data
        files = {'file': open(FILE_PATH_DIR + '/Buffy_dog.jpeg', 'rb')}
        response_class = requests.post(self.class_url, files=files)

        # Main part
        response_image = requests.delete(self.images_url + '/Buffy_dog.jpeg')
        assert response_image.status_code == 200
        assert 'action' in response_image.text
        assert response_image.json()['action'] == 'Deleted'
        assert 'image' in response_image.text
        assert response_image.json()['image'] == 'Buffy_dog.jpeg'
        response_get = requests.get(self.images_url + '/Buffy_dog.jpeg')
        assert response_get.status_code == 404

        # Clean data
        response_clean = requests.delete(self.score_url + '/Buffy_dog.jpeg')

    def test_images_delete_bad_name(self):
        # Main part
        response_image = requests.delete(self.images_url + '/Buffy_dog.jpeg')
        assert response_image.status_code == 200
        assert 'action' in response_image.text
        assert response_image.json()['action'] == 'Not found'
        assert 'image' in response_image.text
        assert response_image.json()['image'] == 'Buffy_dog.jpeg'

    def test_images_delete_empty_name(self):
        # Main part
        response_image = requests.delete(self.images_url + '/')
        assert response_image.status_code == 404


class TestServiceClassification(MainParameters):
    """
    Class for testing 'images'. Some tests failed because flask-service need
    more catching unusual values in parameters.
    """

    @pytest.mark.parametrize(
        "file_path",
        [FILE_PATH_DIR + '/dingo-op.jpg', FILE_PATH_DIR + '/Buffy_dog.jpeg',
         FILE_PATH_DIR + '/n02086240_10604.JPEG', FILE_PATH_DIR + '/sample_image.png'],
        ids=['test_with_jpg', 'test_with_jpeg', 'test_with_JPEG', 'test_with_png']
    )
    def test_classification_post_good_images(self, file_path):
        files = {'file': open(file_path, 'rb'), }
        response = requests.post(self.class_url, files=files)
        assert response.status_code == 200
        assert 'score' in response.text

        # Clean data
        response_clean = requests.delete(self.score_url + '/Buffy_dog.jpeg')
        response_clean = requests.delete(self.images_url + '/Buffy_dog.jpeg')

    def test_classification_post_bad_named_file(self):
        files = {'file': open(FILE_PATH_DIR + '/photo.txt', 'rb'), }
        response = requests.post(self.class_url, files=files)
        assert response.status_code == 200
        assert response.text == self.HTML_PAGE

    @pytest.mark.xfail
    def test_classification_post_empty_name(self):
        # Main part
        response = requests.post(self.class_url, files='')
        assert response.status_code == 404

    def test_classification_get_empty_param(self):
        response = requests.get(self.class_url)
        assert response.status_code == 200
        assert response.text == self.HTML_PAGE

    def test_classification_post_ranked_image(self):
        files = {'file': open(FILE_PATH_DIR + '/ILSVRC2012_val_00020379.JPEG', 'rb'), }
        response = requests.post(self.class_url, files=files)
        print(response.text)
        assert response.status_code == 200
        assert 'score' in response.text
        assert response.json()['score'] == 'Old English sheepdog'

        # Clean data
        response_clean = requests.delete(self.score_url + '/Buffy_dog.jpeg')
        response_clean = requests.delete(self.images_url + '/Buffy_dog.jpeg')

