    var socket = io.connect('http://' + document.domain + ':' + location.port);
    var firsttime = true;
    var username ='';
    socket.on('add user',function (user,Online_User) {
      if(firsttime){
        username = user;
        firsttime = false
      }
      $('#online').empty();
      for (var i =0; i<Online_User.length; i++){
        $('#online').append('<li>' + Online_User[i] + '</li>');
      }
    });
        socket.on('message', data => {
      let msg = "<p> [" + data["time"] + "] <br>" + data['username']
      if (data["type"] == "comment") {
        msg += " : " + data['comment'] + "</p>"
      } else if (data["type"] == "link") {
        if (data["valid"]) {
          msg += " : Shared A YouTube Video"
          msg += "<br><a href=" + data["link"] + ">"
          msg += "Link </a>"
          msg += '<br><iframe src="'
          msg += data["embedded"]
          msg += '" width="300" height="300" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen>></iframe></p>'
        } else {
          msg += " : Shared An Invalid YouTube Link!"
          msg += "<br><a href=" + data["link"] + ">"
          msg += "Link </a></p>"
        }
      }
      $('#display-message').append(msg)
      scrollBot()
    })

    document.addEventListener("keypress", function(event) {
      if (event.code === "Enter") {
        sendMessage();
      }
    })

    function sendMessage() {
      const chatBox = document.getElementById("chat-comment");
      const comment = chatBox.value;
      chatBox.value = "";
      chatBox.focus();
      if (comment !== "") {
        socket.send({
          'username': username,
          'comment': comment,
          "type": "comment"
        });
      }
    }

    function shareLink() {
      const linkBox = document.getElementById("youtube-link")
      const link = linkBox.value
      linkBox.value = ""
      linkBox.focus()
      if (link !== "") {
        socket.send({
          'username': username,
          'link': link,
          "type": "link"
        })
      }
    }

    function scrollBot(){
      const ele=document.getElementById("display-message").lastChild
      ele.scrollIntoView()
    }
    function addMessage(message) {
      const chatMessage = JSON.parse(message.data);
      let chat = document.getElementById('chat');
      chat.innerHTML += "<b>" + chatMessage['username'] + "</b>: " + chatMessage["comment"] + "<br/>";
    }

    var ul = document.getElementById("online");
    ul.addEventListener('click', function (e) {
    var target = e.target; // Clicked element
    while (target && target.parentNode !== ul) {
        target = target.parentNode; // If the clicked element isn't a direct child
        if(!target) { return; } // If element doesn't exist
    }
    if (target.tagName === 'LI'){
      alert(target.id); // Check if the element is a LI
    }
});