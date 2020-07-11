var languageOfUser = navigator.language || navigator.userLanguage;
languageOfUser = languageOfUser.split("-")[0];

var lang;
var url = "http://localhost:9090"
var langRef = {};
var API = mentorAPI(url);
var smartField = smartTypingField();
var loggedIn = false;
var hasProfile = false;
var userprofile = {};
var contactmethods = []

function notifyUser(m) {
	function trigger(message) { // Triggers the yellow rounded message popup
		setTimeout(function() {
			document.getElementById("message").innerHTML = message;
			document.getElementById("notificationArea").style.display = "fixed"; //Display the message
			setTimeout(function() {
				document.getElementById("notificationArea").style.display = "none"; //Wait for 3sec and then close the popup
			}, 3000);
		}, 1000);
	}
	
	if (m.info) {
		if (m.info == "SUCCESS") { trigger(lang.getText().STATE_SUCCESS); }
		else if (m.info == "NOPROFILE") { trigger(lang.getText().STATE_NOPROFILE); }
	} else if (m.error) {
		// TODO:
	}
}
function changeLang(language) {
	languageOfUser = language;
	
	lang = i18u(language, langRef);
	lang.loadLang("../json/" + language + ".json", changeUIText);
	langRef = lang.langRef;
}

async function createoviewprofile() {
	if (hasProfile) {
		if (contactmethods.length == 0) {
			API.contactmethods(function(resp) {contactmethods = resp.split(",")});
		}
		// TODO: 
	} else {
		API.createProfile(notifyUser);
	}
}

function changeUIText(UItext) {
	let createoviewprofile = document.getElementById("createoviewprofile");
	let loginologout = document.getElementById("loginologout");
	let navimg = document.getElementsByClassName("menu")[0];
	
	if (loggedIn) {
		navimg.src = "images/humanface.svg";
		loginologout.innerHTML = lang.getText().LNK_LOGOUT;
		createoviewprofile.style.display = "block";
		if (hasProfile) {
			createoviewprofile.innerHTML = lang.getText().LNK_VIEWPROFILE;
			createoviewprofile.classList.remove("red");
		} else {
			createoviewprofile.innerHTML = lang.getText().LNK_CREATEPROFILE;
			createoviewprofile.classList.add("red");
		}
	} else {
		navimg.src = "images/menu.svg";
		loginologout.innerHTML = lang.getText().LNK_LOGIN;
		createoviewprofile.style.display = "none";
	}
	
	console.log(lang.getText());
	smartField.createSearch(document.getElementById("smartLocation"), lang.getText().SEARCH_LOCATION, lang.getText().SEARCH_LOCATION_RESULT, lang.getText().SEARCH_LOCATION_PARTS);
	smartField.createSearch(document.getElementById("smartContact"), lang.getText().SEARCH_CONTACT, lang.getText().SEARCH_CONTACT_RESULT, lang.getText().SEARCH_CONTACT_PARTS);
}

function init() {
	API.myuser(function(state) {
		if (!state.error) { //user is logged in
			loggedIn = true;
			if (!state.info) { //user has profile
				hasProfile = true;
				userprofile = state;
			}
		}
	});
	
	changeLang(languageOfUser);
}

function hashChange(e) {
	let hash = location.hash;
	
	let triggers = {
		"lang": changeLang,
	}
	hash = hash.split("&");
	
	for (let i in hash) {
		if (value.indexOf("=") > -1) {
			let value = hash[i].split("=");
			if (value[0] in triggers) {
				triggers[value[0]](value[1]);
			}
		}
	}
}
window.addEventListener = hashChange;
init();
