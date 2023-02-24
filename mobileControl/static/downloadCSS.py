import requests

# Download Bootstrap CSS
bootstrap_url = 'https://github.com/twbs/bootstrap/releases/download/v5.0.2/bootstrap-5.0.2-dist.zip'
bootstrap_response = requests.get(bootstrap_url)
with open('bootstrap.zip', 'wb') as file:
    file.write(bootstrap_response.content)

# Download Font Awesome CSS
fontawesome_url = 'https://use.fontawesome.com/releases/v5.15.3/css/all.css'
fontawesome_response = requests.get(fontawesome_url)
with open('fontawesome.css', 'w') as file:
    file.write(fontawesome_response.text)

# Download Iro CSS
iro_url = 'https://cdn.jsdelivr.net/npm/@jaames/iro@4.3.4/build/iro.min.css'
iro_response = requests.get(iro_url)
with open('iro.min.css', 'w') as file:
    file.write(iro_response.text)
