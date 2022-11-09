window['title'] = "";
window['text'] = "";

function EditPost() {
  // $('.update-form-text').val($('#textarea').html())
  $('#text-div').hide()
  //$('#tinymce-text').show();
  $('#div_id_text').show()
  $('#title-input').prop("readonly", false);
  $('#title-input').css({"border-color": "#C1E0FF",
             "border-width":"1px",
             "border-style":"solid"});
  $('.post-edit-div').show();
  $('#modify-post-btns').hide();
  let bob = $('#text-div').html();
  if (bob != undefined)
  {
      tinymce.editors[0].setContent(bob);
  }
}

function HideEditPost(cancel){
    // $('#modify-post-btns').hide();
      //console.log($('#text-div').html())

      // try using a hidden html field to store the initial values
      
      if (!$('#error_1_id_text').length)
      {
        tinymce.editors[0].setContent($('#text-div').html())
      }
      if(!$('#error_0_id_text').length)
      {
        $('#title-input').val(window['title'])
      }
      $('#div_id_text').hide()
      $('#title-input').prop("readonly", true);
      $('#title-input').css('border','');
      // put tinymce content into div
      var bob = tinymce.editors[0].getContent();
      if (bob != undefined)
      {
          $('#text-div').html(bob);
      }
      $('#text-div').show()
      // hide tinymce
      $('.post-edit-div').hide()
      bob=$('#title-input').html()
      if (bob != undefined)
      {
          $('#post_title').html(bob)
      }
      $('#modify-post-btns').show();
   // }
}

function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) == (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

function showUpdateComment(id) {
  //$("textarea[id='#comment-textarea-" + id + "']").val($('#comment-text-' + id).html().trim())
  $("#comment-textarea-" + id).val($('#comment-text-' + id).text().trim())
  $('#comment-textarea-' + id).show()
  $('#comment-text-' + id).hide()
  $('#comment-form-buttons-' + id).show()
  $('#comment-modify-btns-' + id).hide()
}

function hideUpdateComment(id) {
    $('#comment-form-buttons-' + id).hide()
    $('#comment-modify-btns-' + id).show()
    $('#comment-textarea-' + id).val('')
    $('#comment-textarea-' + id).hide()
    $('#comment-text-' + id).show()
}

function onInstanceInit(editor) {
    var bob = tinymce.editors[0].getContent();
    console.log(bob)
    if (bob != undefined)
    {
      $('#text-div').html(bob);
    }
    $(editor.getContainer()).find('button.tox-statusbar__wordcount').click();
    window['title'] = $('#title-input').val()
    window['text'] = tinymce.editors[0].getContent() 
    HideEditPost()
}

$(document).ready(function () {
  $("#tinymce-text").keyup(function(){
    $("#count").text("...characters left: " + String(500 - $(this).val().length));
  });
	$('#editor-btn').on("click", function( event ) {
      EditPost()
  });
  $('#editor-cancel-btn').on("click", function( event ) {
      HideEditPost("cancel")
  });
	$('.comment-save').on("click", function( event ) {
  		event.preventDefault();
  		event.currentTarget.closest(".comment-update-form").submit();
  	});
  	$('.report-post').on("click", function( event ) {
  		event.preventDefault();
  		event.currentTarget.closest("#form-report-post").submit();
  	});
  	$('.report-comment').on("click", function( event ) {
  		event.preventDefault();
  		event.currentTarget.closest("#form-report-comment").submit();
  	});
	$('.comment-edit').on("click", function( event ) {
  		event.preventDefault();
  		showUpdateComment(event.currentTarget.id)
	});
	$('.comment-cancel').on("click", function( event ) {
  		event.preventDefault();
  		hideUpdateComment(event.currentTarget.id)
	});

  var commentModal = document.getElementById('commentModal')
  if (commentModal != null)
  {
    commentModal.addEventListener('show.bs.modal', function (event) {
      var button = event.relatedTarget
      var comment_slug_value = button.getAttribute('data-bs-comment-slug')
      var comment_id_value = button.getAttribute('data-bs-comment-id')
      $('#rem-comment-slug').attr('value', comment_slug_value)
      $('#rem-comment-id').attr('value', comment_id_value)
      let action=$('#delete-form').data('action').split('/')[1]
      $('#delete-form').attr('action', `/${action}/${comment_id_value}/${comment_slug_value}/`)
    })
  }
  $('#subscribed_cb').change(function() {
    parts = $(location).attr('pathname').split('/');
    var slugSegment = parts[3];
    $.ajax({
      type: 'POST',
      url: "/forum/subscribe/",
      data: { 'slug': slugSegment, 'data': this.checked, 'csrfmiddlewaretoken': getCookie('csrftoken') },
      success: function (response) {
        text=$("label[for='subscribed_cb']").text();
        if(text=='Subscribe to this thread') {
            text='Subscribed to this thread';
        } else {
            text='Subscribe to this thread';
        }
        $("label[for='subscribed_cb']").text(text);
      }
    })
  })
  if ($('#subscribed_cb').prop("checked") == true) {
    text='Subscribed to this thread';
  } else {
    text='Subscribe to this thread';
  }
  $("label[for='subscribed_cb']").text(text);

});