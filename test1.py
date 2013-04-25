from wordnik import *
apiUrl = 'http://api.wordnik.com/v4'
apiKey = '3a764609677c7b0b4000408a0a905c1febd664dfa62363aaf'
client = swagger.ApiClient(apiKey, apiUrl)

wordApi = WordApi.WordApi(client)
synonym = wordApi.getRelatedWords(word = "hello", relationshipTypes='synonym', limitPerRelationshipType=1)
print synonym[0].words