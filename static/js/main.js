//#region   =================   Header  ========================

const toggleBtn = document.querySelector('.menu');
const dropDownMenu = document.querySelector('.dropdown-menu');

if (toggleBtn) {
	const toggleBtnIcon = toggleBtn.querySelector('i');

	toggleBtn.onclick = function () {
		dropDownMenu.classList.toggle('open');
		const isOpen = dropDownMenu.classList.contains('open');
		toggleBtnIcon.classList.toggle('ri-menu-3-line', !isOpen);
		toggleBtnIcon.classList.toggle('ri-close-line', isOpen);
	};
}

//#endregion   ==============   Header  ======================== 



//#region   =================   Create Room - Date Time Widgets  ========================

function formatTime(date) {
	let hours = date.getHours();
	let minutes = date.getMinutes();
	let ampm = hours >= 12 ? 'PM' : 'AM';
	hours = hours % 12;
	hours = hours ? hours : 12; // the hour '0' should be '12'
	minutes = minutes < 10 ? '0' + minutes : minutes;
	return hours + ':' + minutes + ' ' + ampm;
}

function formatDate(date) {
	const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
	return date.toLocaleDateString('en-US', options);
}

function updateDateTime() {
	const now = new Date();
	document.getElementById('current-time').textContent = formatTime(now);
	document.getElementById('current-date').textContent = formatDate(now);
}

if (document.getElementById('current-time')) {
	updateDateTime();
	setInterval(updateDateTime, 60000);
}

//#endregion   ==============   Create Room - Date Time Widgets  ========================



//#region   =================   Chat Controllers  ========================

let chat_btn = document.getElementById('chat-btn');
let room_chat_section = document.querySelector(".room-chat-section");
if(chat_btn){

	chat_btn.addEventListener("click", () => {
		let room_chat_open = room_chat_section.classList.contains('chat_visible');
		if (!room_chat_open) {
			room_chat_section.classList.toggle("chat_visible")
			chat_btn.style.backgroundColor = "var(--blue-color)";
			chat_btn.style.borderColor = "var(--blue-color)";
			chat_btn.style.color = "white";
		}
		else{
			room_chat_section.classList.toggle("chat_visible")
			chat_btn.style.backgroundColor = "white";
			chat_btn.style.borderColor = "#dddddd";
			chat_btn.style.color = "var(--text-color)";
		}
	})
}


let header_chat_btn = document.getElementById('header-chat-btn');
if (header_chat_btn) {
	header_chat_btn.addEventListener("click", () => {
		room_chat_section.classList.toggle("chat_visible")
		chat_btn.style.backgroundColor = "white";
		chat_btn.style.borderColor = "#dddddd";
		chat_btn.style.color = "var(--text-color)";
	})
}

//#endregion   ==============   Chat Controllers  ======================== 



//#region   =================   Caption Controllers  ========================

let caption_btn = document.getElementById('caption-btn');
let meeting_captions_section = document.querySelector(".meeting-captions");

if (caption_btn) {
	caption_btn.addEventListener("click", ()=>{
		let meeting_captions_hide = meeting_captions_section.classList.contains('meeting_captions_hide');
		if (!meeting_captions_hide) {
			meeting_captions_section.classList.toggle("meeting_captions_hide");
			caption_btn.style.backgroundColor = "var(--primary-color)";
			caption_btn.style.borderColor = "var(--primary-color)";
			caption_btn.style.color = "white";
		}
		else{
			meeting_captions_section.classList.toggle("meeting_captions_hide");
			caption_btn.style.backgroundColor = "white";
			caption_btn.style.borderColor = "#dddddd";
			caption_btn.style.color = "var(--text-color)";
		}

	})
}

//#endregion   ==============   Caption Controllers  ======================== 



//#region   =================   Copy Room Link  ========================

let copy_btn = document.getElementById("copy-btn");
if (copy_btn){
	let chatroom = copy_btn.querySelector("p");
	copy_btn.addEventListener("click", () => {
		navigator.clipboard.writeText(window.location.host+'/room/'+chatroom.innerText+'/');
		Swal.fire({
			text: "Link Copied to the Clipboard",
			icon: "success",
			showConfirmButton: false,
		});
	})
}

//#endregion   ==============   Copy Room Link  ======================== 



//#region   =================   Room Form Submission  ========================

const create_room_form = document.getElementById("create-room-form");
const join_room_form = document.getElementById("join-room-form");

const handleRoomFormSubmit = async (event) => {
	event.preventDefault();

	const room = event.target.meet_id.value.trim();
	const joinName = event.target.join_name.value.trim();
	const languageSpeak = event.target.language_speak.value.trim();

	if (!room) {
		Swal.fire({
			text: "Please provide the meeting id for the room you want to join",
			icon: "error",
			showConfirmButton: false,
		});
		return;
	}

	if (!joinName) {
		Swal.fire({
			text: "Please provide the name with which you want to join the meeting",
			icon: "error",
			showConfirmButton: false,
		});
		return;
	}

	try {
		const { uid, token } = await fetchRoomToken(room);
		saveToSessionStorage({UID: uid, token, room, name: joinName, lang: languageSpeak, id_num: generateRandomId()});
		navigateToRoom();

	} catch (error) {
		Swal.fire({
			title: "Error fetching the token",
			text: "Failed to process your meeting request. Please try again",
			icon: "error",
			showConfirmButton: false,
		});
	}
};


const fetchRoomToken = async (room) => {
	const response = await fetch(`/get_token/?channel=${room}`);
	return await response.json();
};


const saveToSessionStorage = (data) => {
	for (const [key, value] of Object.entries(data)) {
		sessionStorage.setItem(key, value);
	}
};


const generateRandomId = () => {
	return Math.floor(Math.random() * 100) + 1;
};


const navigateToRoom = () => {
	window.open('/room/', '_self');
};



if (create_room_form){
	create_room_form.addEventListener('submit', handleRoomFormSubmit);
}

if (join_room_form){
	join_room_form.addEventListener('submit', handleRoomFormSubmit);
}

//#endregion   ==============   Room Form Submission  ======================== 



//#region   =================   Head  ========================
//#endregion   ==============   Head  ======================== 