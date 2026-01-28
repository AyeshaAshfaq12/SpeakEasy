const APP_ID = '23368c20269344c6ab9d386b5837ee4d';
const CHANNEL = sessionStorage.getItem('room');
const TOKEN = sessionStorage.getItem('token');
let UID = Number(sessionStorage.getItem('UID'));
let NAME = sessionStorage.getItem('name');

const client = AgoraRTC.createClient({mode:'rtc', codec:'vp8'});

let localTracks = [];
let remoteUsers = {};



//#region   =================   Agora Functions  ========================

let joinAndDisplayLocalStream = async () => {

    document.querySelector('#copy-btn p').innerText = CHANNEL ;

    client.on('user-published', handleUserJoined);

    client.on('user-left', handleUserLeft);

    try {
        await client.join(APP_ID, CHANNEL, TOKEN, UID);
    } catch (error) {
        console.error(error);
        window.open('/', '_self');
    }
    
    localTracks = await AgoraRTC.createMicrophoneAndCameraTracks();
    
    let member = await createMember();

    let player = `
        <div class="video-container" id="user-container-${UID}">
            <div class="username-wrapper"><span class="user-name">${member.name}</span></div>
            <div class="video-player" id="user-${UID}"></div>
        </div>
    `;

    document.getElementById('video-streams').insertAdjacentHTML('afterBegin', player);

    localTracks[1].play(`user-${UID}`);

    await client.publish([localTracks[0], localTracks[1]]);

}


let handleUserJoined = async (user, mediaType) => {
    remoteUsers[user.uid] = user;
    await client.subscribe(user, mediaType);

    if(mediaType == 'video'){
        let player = document.getElementById(`user-container-${user.uid}`);

        if(player != null){
            player.remove();
        }

        let member = await getMember(user)

        player = `
            <div class="video-container" id="user-container-${user.uid}">
                <div class="username-wrapper"><span class="user-name">${member.name}</span></div>
                <div class="video-player" id="user-${user.uid}"></div>
            </div>
        `;
    
        document.getElementById('video-streams').insertAdjacentHTML('afterBegin', player);

        user.videoTrack.play(`user-${user.uid}`);
    }

    if(mediaType == 'audio'){
        user.audioTrack.play();
    }

}


let handleUserLeft = async (user)  => {
    delete remoteUsers[user.uid];
    document.getElementById(`user-container-${user.uid}`).remove();
}


let leaveAndRemoveLocalStream = async () => {
    for (let i=0; localTracks.length > i; i++){
        localTracks[i].stop();
        localTracks[i].close();
    }

    await client.leave();

    deleteMember();

    window.open('/', '_self');
}

joinAndDisplayLocalStream();

document.getElementById('leave-btn').addEventListener('click', leaveAndRemoveLocalStream); 

//#endregion   ==============   Agora Functions  ======================== 



//#region   =================   Agora - Helper Functions  ========================

let getMember = async (user) => {
    let response = await fetch(`/get_member/?UID=${user.uid}&room_name=${CHANNEL}`);
    let member = await response.json();
    return member; 
}


let createMember = async () => {
    let response = await fetch('/create_member/', {
        method: 'POST',
        headers: {
            'Content-type': 'application/json',
        },
        body: JSON.stringify({'name': NAME, 'UID': UID, 'room_name': CHANNEL, 'lang': sessionStorage.getItem('lang')}),
    });


    let member = await response.json();

    return member;
}


let deleteMember = async () => {
    let response = await fetch('/delete_member/', {
        method: 'POST',
        headers: {
            'Content-type': 'application/json',
        },
        body: JSON.stringify({'name': NAME, 'UID': UID, 'room_name': CHANNEL}),
    });

    sessionStorage.removeItem('room')
    sessionStorage.removeItem('UID')
    sessionStorage.removeItem('lang')
    sessionStorage.removeItem('name')
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('id_num')
}

//#endregion   ==============   Agora - Helper Functions  ======================== 



//#region   =================   Stream Controllers  ========================

let camera_btn = document.getElementById('camera-btn');
if (camera_btn) {

    let toggleCamera = async (e) => {
        console.log(e)
        if(localTracks[1].muted){
            if(e.target.classList.contains("controller-icon-wrapper")){
                await localTracks[1].setMuted(false);
                e.target.style.backgroundColor = "white";
                e.target.style.borderColor = "#dddddd";
                e.target.style.color = "var(--text-color)";
                e.target.querySelector('i').className = "ri-video-off-fill";
            }
        }else{
            if(e.target.classList.contains("controller-icon-wrapper")){
                await localTracks[1].setMuted(true);
                e.target.style.backgroundColor = "#b10303";
                e.target.style.borderColor = "#b10303";
                e.target.style.color = "white";
                e.target.querySelector('i').className = "ri-video-on-fill";
            }
        }
    }

    camera_btn.addEventListener('click', toggleCamera);
}


let mic_btn = document.getElementById('mic-btn')
if (mic_btn) {

    let toggleMic = async (e) => {
        if(localTracks[0].muted){
            if(e.target.classList.contains("controller-icon-wrapper")){
                await localTracks[0].setMuted(false);
                e.target.style.backgroundColor = "white";
                e.target.style.borderColor = "#dddddd";
                e.target.style.color = "var(--text-color)";
                e.target.querySelector('i').className = "ri-mic-off-fill";
            }
        }else{
            if(e.target.classList.contains("controller-icon-wrapper")){
                await localTracks[0].setMuted(true);
                e.target.style.backgroundColor = "#b10303";
                e.target.style.borderColor = "#b10303";
                e.target.style.color = "white";
                e.target.querySelector('i').className = "ri-mic-fill";
            }
        }
    }
    
    mic_btn.addEventListener('click', toggleMic);

}

//#endregion   ==============   Stream Controllers  ======================== 



//#region   =================   Head  ========================
//#endregion   ==============   Head  ======================== 