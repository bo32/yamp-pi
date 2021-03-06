_MUTE = 'mute'
_SOUND_UP = 'sound_up'
_SOUND_DOWN = 'sound_down'
_PLAY = 'play/'
_PLAY_URL = 'play_url/'
_NEXT = 'next'
_PREVIOUS = 'previous'

function pause() {
    send('pause');
}

function previous() {
    send(_PREVIOUS);
}

function next() {
    send(_NEXT);
}

function mute() {
    send(_MUTE);
}

function sound_down() {
    send(_SOUND_DOWN);
}

function sound_up() {
    send(_SOUND_UP);
}

function play(folder) {
    send(_PLAY + folder);
}

function play_url(url_key) {
    send(_PLAY_URL + url_key);
}

function send(action) {
    const http = new XMLHttpRequest();
    http.onreadystatechange = function() {
        if (http.readyState == XMLHttpRequest.DONE) {
            if (action.startsWith(_PLAY_URL)) {
                // TODO
            } else if (action.startsWith(_PLAY)) {
                const json_response = JSON.parse(http.responseText);
                update_current_track(json_response);
            } else { // bit ugly this
                const json_response = JSON.parse(http.responseText);
                switch (action) {
                    case _MUTE:
                        document.getElementById("mute_button").innerHTML = json_response.muted ? "Unmute" : "Mute";
                        break;
                    case _SOUND_DOWN:
                    case _SOUND_UP:
                        document.getElementById("sound_down").disabled = json_response.is_sound_min;
                        document.getElementById("sound_up").disabled = json_response.is_sound_max;
                        break;
                    case _NEXT:
                    case _PREVIOUS:
                        update_current_track(json_response);
                        break;

                    default:
                        break;
                }
            }
        }
    }
    http.open("GET", action);
    http.send();
}

function update_current_track(data) {
    document.getElementById("current_track_title").innerHTML = data.title
}