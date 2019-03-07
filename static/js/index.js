SERVER_URL = 'http://127.0.0.1:5000'

$(document).ready(() => {
  $(document)
    .ajaxStart(function () {
      $('#loading').show()
    })
    .ajaxStop(function () {
      $('#loading').hide()
    })

  $('#submit').on('click', function () {
    console.log('BUTTON CLICKED')

    $('#matches').empty()
    $('.box').css('display', 'flex')

    const platformName = $('#platform-select option:selected').val()
    const playerName = $('#player-name').val()

    var data = {}
    data['platform-name'] = platformName
    data['player-name'] = playerName

    const feats = [
      'bestRankPoint',
      'dailyKills',
      'dailyWins',
      'top10s',
      'weeklyKills',
      'weeklyWins'
    ]

    $.ajax({
      url: SERVER_URL,
      dataType: 'json',
      contentType: 'application/json; charset=utf-8',
      data: JSON.stringify(data),
      type: 'POST',
      success: function (resp) {
        console.log(resp)
        if (resp['lifetimeStats'] !== null) {
          const solo = resp['lifetimeStats']['gameModeStats']['solo']
          $('#solo').append('<h2>Solo</h2>')
          $.each(solo, (key, val) => {
            if (feats.includes(key)) {
              $('#solo').append(
                '<div><p>' + key + '</p><h3>' + val + '</h3></div>'
              )
            }
          })

          const duo = resp['lifetimeStats']['gameModeStats']['duo']
          $('#duo').append('<h2>Duo</h2>')
          $.each(duo, (key, val) => {
            if (feats.includes(key)) {
              $('#duo').append(
                '<div><p>' + key + '</p><h3>' + val + '</h3></div>'
              )
            }
          })

          const squad = resp['lifetimeStats']['gameModeStats']['squad']
          $('#squad').append('<h2>Squad</h2>')
          $.each(squad, (key, val) => {
            if (feats.includes(key)) {
              $('#squad').append(
                '<div><p>' + key + '</p><h3>' + val + '</h3></div>'
              )
            }
          })
        }
        if (resp['matches'] !== null && resp['matches'].length > 0) {
          $('#matches').append('<h2> Select the match</h2>')
          $.each(resp['matches'], (idx, match) => {
            $('#matches').append(
              '<li class="match row" id=' +
                match['id'] +
                '><h4> Match  </h4><h3><b> ' +
                match['id'] +
                '</h3></b></li>'
            )
          })
        } else {
          $('#matches').append(
            '<p>Oops!! Seems like you  havent played any matches in last 15 days</p>'
          )
        }
      },
      error: function (err) {
        console.log(err)
      }
    })
  })

  $('#matches').on('click', 'li', function () {
    $(this).empty()

    matchId = $(this).attr('id')
    console.log('Match Id = ', matchId)
    console.log('SEND AJAX REQUEST')

    var thisLi = this
    console.log(thisLi)

    $.ajax({
      url: SERVER_URL + '/predict',
      dataType: 'json',
      contentType: 'application/json; charset=utf-8',
      data: JSON.stringify(matchId),
      type: 'POST',
      success: function (resp) {
        console.log(resp)

        $(thisLi).append('<h4 class="col-sm-12">MATCH INFO</h4>')
        $.each(resp['matchInfo'], (key, val) => {
          if (val !== null && key !== 'createdAt') {
            $(thisLi).append(
              '<div class="col-sm-6">' + key + ' : ' + val + '</div>'
            )
          }
        })

        $(thisLi).append('<h4 class="col-sm-12">MATCH STATISTICS</h4>')
        $.each(resp['stats'], (key, val) => {
          if (key !== 'output') {
            $(thisLi).append(
              '<div class="col-sm-4">' + key + ' : ' + val + '</div>'
            )
          }
        })

        $(thisLi).append(
          '<h4> WINNING PROBABILITY: ' + resp['output'] + '%</h4>'
        )
      },
      error: function (err) {
        console.log(err)
      }
    })
  })
})
