SERVER_URL = ' http://127.0.0.1:5000/'

var submitBtn = document.getElementById('submit')
submitBtn.addEventListener('click', () => {
  const pSelect = document.getElementById('platform-select')
  const playerName = document.getElementById('player-name').value

  // get the index of selected option
  const pIndex = pSelect.selectedIndex

  const platform = pSelect[pIndex].value

  var data = {
    'platform-name': platform,
    'player-name': playerName
  }
  console.log('data', data)
  fetch(SERVER_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
    .then(res => res.json())
    .then(response => console.log('Success', response))
    .catch(err => console.error('Error', err))
})
