var form=document.getElementById('form')

form.addEventListener('submit', function(e){
 e.preventDefault()

 var name=document.getElementById('name').value
 var body=document.getElementById('body').value

 fetch('http://localhost:8080/api/resource/Note?fields=[%22*%22]', {
  method: 'POST',
  body: JSON.stringify({
    title:name,
    content:body,

  }),
  headers: {
    'Content-Type': 'application/json',
    "X-Frappe-CSRF-Token": frappe.csrf_token  }
  })
  .then(function(response){ 
  return response.json()
    })
  .then(function(data){
  console.log(data)
  title=document.getElementById("title")
  body=document.getElementById("bd")
 
  title.innerHTML = "data.name"
  body.innerHTML = data.content  
  console.log(body.innerHTML)
}).catch(error => console.error('Error:', error)); 
});