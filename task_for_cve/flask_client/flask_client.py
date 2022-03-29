import os.path
import requests

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

#### Requests for /classification
# Base page
r = requests.get(URL + 'classification')
assert r.status_code == 200
assert r.text == HTML_PAGE

# Good image jpg
files = {'file': open('/home/user/PycharmProjects/flask_test/test_files/dingo-op.jpg', 'rb')}
r = requests.post(URL + 'classification', files=files)
assert r.status_code == 200
assert 'score' in r.text

# Good image png
files = {'file': open('/home/user/PycharmProjects/flask_test/test_files/sample_image.png', 'rb')}
r = requests.post(URL + 'classification', files=files)
assert r.status_code == 200
assert 'score' in r.text

# Good image jpeg
files = {'file': open('/home/user/PycharmProjects/flask_test/test_files/Buffy_dog.jpeg', 'rb')}
r = requests.post(URL + 'classification', files=files)
assert r.status_code == 200
assert 'score' in r.text

# Bad image - file in format txt
files = {'file': open('/home/user/PycharmProjects/flask_test/test_files/photo.txt', 'rb')}
r = requests.post(URL + 'classification', files=files)
assert r.status_code == 200
assert r.text == HTML_PAGE

# Empty image and no parameter 'files' in request return 500 error
# r = requests.post(URL+'classification', files='')
# print(r.text)
# print(r.status_code)
# assert r.status_code == 200
# assert r.text == HTML_PAGE
#### Requests for /classification


#### Requests for /images
# Get really image
files = {'file': open('/home/user/PycharmProjects/flask_test/test_files/Buffy_dog.jpeg', 'rb')}
r1 = requests.post(URL + 'classification', files=files)
r2 = requests.get(URL + 'images/Buffy_dog.jpeg')
assert r2.status_code == 200
file = open("./sample_image.png", "wb")
file.write(r.content)
file.close()
assert os.path.exists("./sample_image.png")
os.remove("./sample_image.png")

# Get bad name image
r2 = requests.get(URL + 'images/Bu.jpeg')
assert r2.status_code == 404

# Delete image from directory
files = {'file': open('/home/user/PycharmProjects/flask_test/test_files/Buffy_dog.jpeg', 'rb')}
r1 = requests.post(URL + 'classification', files=files)
r2 = requests.delete(URL + 'images/Buffy_dog.jpeg')
assert r2.status_code == 200
assert 'action' in r2.text
assert r2.json()['action'] == 'Deleted'
assert 'image' in r2.text
assert r2.json()['image'] == 'Buffy_dog.jpeg'

# Delete image with bad name
files = {'file': open('/home/user/PycharmProjects/flask_test/test_files/Buffy_dog.jpeg', 'rb')}
r1 = requests.post(URL + 'classification', files=files)
r2 = requests.delete(URL + 'images/Buffy_dog.jpeg')
assert r2.status_code == 200
assert 'action' in r2.text
assert r2.json()['action'] == 'Deleted'
assert 'image' in r2.text
assert r2.json()['image'] == 'Buffy_dog.jpeg'
r3 = requests.get(URL + 'images/Buffy_dog.jpeg')
assert r3.status_code == 404
### Requests for /images


#### Requests for /scores
# Get score in real image
files = {'file': open('/home/user/PycharmProjects/flask_test/test_files/Buffy_dog.jpeg', 'rb')}
r1 = requests.post(URL + 'classification', files=files)
r2 = requests.get(URL + 'scores/Buffy_dog.jpeg')
assert r2.status_code == 200
assert 'image' in r2.text
assert 'score' in r2.text
assert r2.json()['image'] == 'Buffy_dog.jpeg'

# Get score in bad-named image
r2 = requests.get(URL + 'scores/Buffy.jpeg')
assert r2.status_code == 200
assert 'image' in r2.text
assert 'score' in r2.text
assert r2.json()['image'] == 'Buffy.jpeg'
assert r2.json()['score'] == 'Score not found'

# Delete score in real image
files = {'file': open('/home/user/PycharmProjects/flask_test/test_files/Buffy_dog.jpeg', 'rb')}
r1 = requests.post(URL + 'classification', files=files)
r2 = requests.delete(URL + 'scores/Buffy_dog.jpeg')
assert r2.status_code == 200
assert 'image' in r2.text
assert 'score' in r2.text
assert r2.json()['image'] == 'Buffy_dog.jpeg'
assert r2.json()['score'] == 'Score was deleted'

# Delete core in bad-named image
r2 = requests.get(URL + 'scores/Buffy.jpeg')
assert r2.status_code == 200
assert 'image' in r2.text
assert 'score' in r2.text
assert r2.json()['image'] == 'Buffy.jpeg'
assert r2.json()['score'] == 'Score not found'
#### Requests for /scores
