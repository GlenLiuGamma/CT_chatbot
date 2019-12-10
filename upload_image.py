from imgurpython import ImgurClient

client_id = 'd3bdaa58914468d'
client_secret = '52eb640062b0e091988b9d6522a6fe2fbf6af9dd'
access_token = 'caf152cace432225365dbf2b76d377e35f3f152d'
refresh_token = '3d1138cd0637a789875b387fd3a231e6a2069f92'


client = ImgurClient(client_id, client_secret, access_token, refresh_token)
config = {
    'album': None,
    'name': 'test-name!',
    'title': 'test-title',
    'description': 'test-description'
}
print("Uploading image... ")
image = client.upload_from_path('photo/1.png', config=config, anon=False)
print("Done")
print(image['link'])