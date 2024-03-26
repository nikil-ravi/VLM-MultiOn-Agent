document.getElementById('uploadTrigger').addEventListener('click', function() {
    document.getElementById('imageInput').click();
});

document.getElementById('imageInput').addEventListener('change', function(e) {
    if (e.target.files.length > 0) {
        const formData = new FormData();
        formData.append("file", e.target.files[0]);

        // Get the text input value and append it to formData
        const userText = document.getElementById('userText').value;
        formData.append("input_text", userText);

        fetch('http://127.0.0.1:8000/upload/', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('response').textContent = JSON.stringify(data);
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('response').textContent = 'Failed to upload image.';
        });
    }
});
