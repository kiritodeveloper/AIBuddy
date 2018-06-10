const request = require('superagent');

let service = {};

service.postImage = async (imageUrl) => {
  let response = await request
    .post('http://127.0.0.1:5000/upload')
    .send({ 'url': imageUrl });

  return response.body;
}

module.exports = service;
