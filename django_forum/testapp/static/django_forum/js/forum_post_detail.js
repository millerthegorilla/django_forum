function EditPost() {
  console.log("edit post function")
  $('.update-form-text').val($('#textarea').html())
  $('#title_input').val($('#post_title').html())
  $('.post-edit-div').show();
  tinymce.editors[0].show();
  $('#title-div').hide();
  $('#text-errors').hide();
  $('#textarea').hide();
  $('#modify-post-btns').hide();
}

function HideEditPost(){
    tinymce.editors[0].hide();
    $('.update-form-text').hide()
    $('.post-edit-div').hide()
    let bob=$('#title-input').val()
    console.log("bob is " + bob)
    $('#post_title').html(bob)
    $('#textarea').html($('.update-form-text').val())
    $('#title-div').show()
    $('#text-errors').show()
    $('#textarea').show()
    $('#modify-post-btns').show();
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
    console.log("initing")
    //editor.hide()
    //$(editor.getContainer()).find('button.tox-statusbar__wordcount').click();
    //$('#textarea').show()
}

$(document).ready(function () {

  $("#id_text").keyup(function(){
    $("#count").text("...characters left: " + String(500 - $(this).val().length));
  });

	$('.post-edit-div').hide();
	$('.update-form-text').hide();
	$('#comment-textarea').hide();
	$('.comment-form-buttons').hide();
	$('#editor-btn').on("click", function( event ) {
      EditPost()
  });
  $('#editor-cancel-btn').on("click", function( event ) {
      HideEditPost()
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
	tinymce.init({
	selector: '.update-form-text',
  init_instance_callback: function(editor) {
    console.log('Editor: ' + editor.id + ' is now initialized.');
  },
  menubar: "False",
  min-height: "500px",
  browser_spellcheck: "True",
  contextmenu: "False",
  plugins: "advlist autolink lists link image charmap print preview anchor searchreplace fullscreen insertdatetime media table paste code help wordcount spellchecker",
  toolbar: "undo redo | bold italic underline strikethrough | fontselect fontsizeselect formatselect | alignleft aligncenter alignright alignjustify | outdent indent |  numlist bullist checklist | forecolor backcolor casechange permanentpen formatpainter removeformat | pagebreak | charmap emoticons | fullscreen  preview save print | insertfile image media template link anchor | a11ycheck ltr rtl | showcomments addcomment table",
  custom_undo_redo_levels: "10",
	});
	HideEditPost()
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