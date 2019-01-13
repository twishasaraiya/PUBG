SERVER_URL = 'http://127.0.0.1:5000'

$(document).ready(() => {
  $('#submit').on('click', function () {
    console.log('BUTTON CLICKED')
    const platformName = $('#platform-select option:selected').val()
    const playerName = $('#player-name').val()

    var data = {
      'platform-name': platformName,
      'player-name': playerName
    }
    console.log('DATA', data)
    console.log('SEND AJAX REQUEST')
    $.ajax({
      url: SERVER_URL,
      data: data,
      type: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      success: function (resp) {
        console.log(resp)
        $('#prediction').style('visibility', 'visible')
      },
      error: function (err) {
        console.log(err)
      }
    })
  })
})
