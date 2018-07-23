const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const port = process.env.PORT || 7777;
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use('/', express.static(__dirname + '/public'));

app.get('/', function (req, res) {
	res.render('index.html');
});

app.listen(port, function () {
	console.log(`AI Buddy Web server launched on port ${port}`);
});