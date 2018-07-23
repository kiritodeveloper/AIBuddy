$("document").ready(function () {
	var resultForm = document.getElementById("result");
	var error = document.getElementById("error");
	error.style.display = "none";
	result.style.display = "none"; 
	$('input[type=file]').on("change", function () {
		var $files = $(this).get(0).files;
		var formData = new FormData();
		formData.append("file", $files[0]);
		var submitForm = document.getElementById("imgur");
		if ($files.length) {
			if ($files[0].size > $(this).data("max-size") * 1024) {
				console.log("Please select a smaller file!");
				error.style.display = "block";
				return false;
			}
			var apiUrl = 'http://206.189.212.73:5000/upload';
			var settings = {
				"async": true,
				"crossDomain": false,
				"url": apiUrl,
				"method": "POST",
				"datatype": "json",
				"processData": false,
				"contentType": false,
				"data": formData,
				beforeSend: function (xhr) {
					console.log("Enviando...");
					submitForm.style.display = "none";
					document.getElementById("subtitle").innerHTML = "Enviando...";
				},
				success: function (res) {
					var lastIndex = res.minusvalido.lastIndexOf(" ");
					document.getElementById("subtitle").innerHTML = "Resultado!";
					resultForm.style = ".grid-container {display: grid;grid-template-columns: auto auto;}";
					$("#result1").percircle({
						text: res.minusvalido,
						percent: res.minusvalido.slice(0, lastIndex),
						progressBarColor: "#1ec0b0"
					})
					$("#result2").percircle({
						text: res.no_minusvalidos,
						percent: res.no_minusvalidos.slice(0, lastIndex),
						progressBarColor: "#1ec0b0"
					})
				},
				error: function () {
					alert("Error");
				}
			}
			$.ajax(settings).done(function (res) {
				console.log("Done");
			});
		}
	});
});